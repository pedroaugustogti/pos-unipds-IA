import { Graphics } from "pixi.js";
import { buildLayout } from "./layout";
import { ScoreTracker } from "./score-tracker";

const DIFF_THRESHOLD = 30;
const MOTION_RATIO_MIN = 0.15;
const FLY_ZONE_Y_MIN = 30;
const FLY_ZONE_Y_MAX = 480;

function hasMotionInBox(currentCanvas, bgCanvas, box) {
    if (!bgCanvas || !box) return true;

    const x1 = Math.max(0, Math.floor(box.x1));
    const y1 = Math.max(0, Math.floor(box.y1));
    const x2 = Math.min(currentCanvas.width, Math.ceil(box.x2));
    const y2 = Math.min(currentCanvas.height, Math.ceil(box.y2));
    const bw = x2 - x1;
    const bh = y2 - y1;
    if (bw <= 0 || bh <= 0) return true;

    const ctx = currentCanvas.getContext('2d');
    const bgCtx = bgCanvas.getContext('2d');

    const current = ctx.getImageData(x1, y1, bw, bh);
    const bg = bgCtx.getImageData(x1, y1, bw, bh);

    let movedPixels = 0;
    const totalPixels = bw * bh;

    for (let i = 0; i < current.data.length; i += 4) {
        const dr = Math.abs(current.data[i] - bg.data[i]);
        const dg = Math.abs(current.data[i + 1] - bg.data[i + 1]);
        const db = Math.abs(current.data[i + 2] - bg.data[i + 2]);
        if (dr + dg + db > DIFF_THRESHOLD) movedPixels++;
    }

    return (movedPixels / totalPixels) >= MOTION_RATIO_MIN;
}

export default async function main(game) {
    const container = buildLayout(game.app);
    const worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });
    const tracker = new ScoreTracker();

    let bgCanvas = null;
    let lastFrameCanvas = null;
    let workerBusy = false;
    let lastHitInfo = null;
    let captureTimestamp = 0;
    const pipelineLatencies = [];

    const DEAD_DUCK_COOLDOWN = 400;
    const DEAD_DUCK_RADIUS_X = 80;

    function isDeadDuck(x, y, box) {
        if (!lastHitInfo) return false;
        if (Date.now() - lastHitInfo.time > DEAD_DUCK_COOLDOWN) return false;

        const dx = Math.abs(x - lastHitInfo.x);
        const dy = y - lastHitInfo.y;
        if (dx > DEAD_DUCK_RADIUS_X) return false;
        if (dy < -20) return false;

        if (box) {
            const boxW = box.x2 - box.x1;
            if (boxW < lastHitInfo.boxW * 0.85) return true;
        }

        return dy > 15;
    }

    const boundingBox = new Graphics();
    game.stage.addChild(boundingBox);

    game.stage.aim.anchor.set(0.5, 0.5);
    game.stage.aim.visible = false;

    worker.onmessage = ({ data }) => {
        const { type } = data;
        workerBusy = false;
        const pipelineMs = Date.now() - captureTimestamp;
        pipelineLatencies.push(pipelineMs);

        if (type === 'prediction') {
            if (data.y < FLY_ZONE_Y_MIN || data.y > FLY_ZONE_Y_MAX) return;

            const level = game.levelIndex || 0;
            const skipMotionCheck = level >= 3;
            if (!skipMotionCheck && !hasMotionInBox(lastFrameCanvas, bgCanvas, data.box)) return;

            if (!game.bullets || game.bullets <= 0) return;
            if (isDeadDuck(data.x, data.y, data.box)) return;

            boundingBox.clear();
            if (data.box) {
                const { x1, y1, x2, y2 } = data.box;
                boundingBox.rect(x1, y1, x2 - x1, y2 - y1);
            }

            container.updateHUD(data);
            game.stage.aim.visible = true;

            game.stage.aim.setPosition(data.x, data.y);
            const position = game.stage.aim.getGlobalPosition();

            const ducksHitBefore = game.ducksShot || 0;
            game.handleClick({ global: position });
            const ducksHitAfter = game.ducksShot || 0;
            const hit = ducksHitAfter > ducksHitBefore;

            if (hit) {
                lastHitInfo = {
                    x: data.x,
                    y: data.y,
                    time: Date.now(),
                    boxW: data.box ? (data.box.x2 - data.box.x1) : 60,
                };
            }

            tracker.record({
                phase: 'after',
                level: game.levelIndex,
                score: data.score,
                x: data.x,
                y: data.y,
                box: data.box,
                dominantColors: data.dominantColors,
                hit,
                pipelineMs,
            });
        }

        const lvl = game.levelIndex || 0;
        const recaptureDelay = RECAPTURE_DELAYS[lvl];
        if (recaptureDelay !== null) {
            setTimeout(captureAndSend, recaptureDelay);
        }
    };

    function captureBg(canvas) {
        bgCanvas = document.createElement('canvas');
        bgCanvas.width = canvas.width;
        bgCanvas.height = canvas.height;
        bgCanvas.getContext('2d', { willReadFrequently: true }).drawImage(canvas, 0, 0);
    }

    function saveFrame(canvas) {
        if (!lastFrameCanvas) {
            lastFrameCanvas = document.createElement('canvas');
            lastFrameCanvas.getContext('2d', { willReadFrequently: true });
        }
        lastFrameCanvas.width = canvas.width;
        lastFrameCanvas.height = canvas.height;
        lastFrameCanvas.getContext('2d').drawImage(canvas, 0, 0);
    }

    let lastWave = -1;

    const LEVEL_INTERVALS = [200, 120, 80, 80, 80, 80];

    // Re-capture delay based on frame subtraction displacement and duck count
    // Pipeline latency: ~140ms | Avg box width: ~60px
    // boxClearMs = 60 / (speed * 0.06) → time for duck to clear one bounding box
    // baseCooldown = max(0, boxClearMs - 140)
    // switchPenalty: 0ms (≤2 ducks), 30ms (3 ducks), 60ms (≥10 ducks)
    //
    // L0: speed=5, 2 ducks  → interval 200ms handles it
    // L1: speed=6, 3 ducks  → interval 120ms handles it
    // L2: speed=7, 3 ducks  → 65ms (low duck count, velocity 0.246 px/ms → 34px displacement)
    // L3: speed=7, 10 ducks → 90ms (10 ducks cause aim-switching; extra cooldown reduces 0.453→~0.3 px/ms)
    // L4: speed=8, 2 ducks  → 30ms (fast speed, small buffer to avoid over-firing)
    // L5: speed=8, 15 ducks → 0ms (data shows no aim-switching; faster cycle = less displacement)
    const RECAPTURE_DELAYS = [null, null, 65, 90, 30, 0];

    function getCaptureInterval() {
        const level = game.levelIndex || 0;
        return LEVEL_INTERVALS[level] || 200;
    }

    async function captureAndSend() {
        if (workerBusy) return;

        try {
            boundingBox.clear();
            game.stage.aim.visible = false;
            const canvas = game.app.renderer.extract.canvas(game.stage);
            const currentWave = game.wave || 0;
            const hasDucks = game.stage?.ducks?.some(d => d.alive);
            const currentLevel = game.levelIndex || 0;

            if (!bgCanvas || (currentWave !== lastWave && !hasDucks)) {
                captureBg(canvas);
                lastWave = currentWave;
                return;
            }

            if (!game.bullets || game.bullets <= 0) return;

            if (currentLevel < 3) {
                saveFrame(canvas);
            }

            const bitmap = await createImageBitmap(canvas);

            captureTimestamp = Date.now();
            workerBusy = true;
            worker.postMessage({
                type: 'predict',
                image: bitmap,
                level: currentLevel,
            }, [bitmap]);
        } catch (_) {
            workerBusy = false;
        }
    }

    function scheduleCaptureLoop() {
        setTimeout(() => {
            captureAndSend();
            scheduleCaptureLoop();
        }, getCaptureInterval());
    }

    scheduleCaptureLoop();

    setInterval(() => {
        tracker.printReport();
    }, 30000);

    window.addEventListener('beforeunload', () => {
        tracker.save();
    });

    window._tracker = tracker;
    window._pipelineStats = () => {
        if (pipelineLatencies.length === 0) return 'No data yet';
        const sorted = [...pipelineLatencies].sort((a, b) => a - b);
        const avg = sorted.reduce((a, b) => a + b, 0) / sorted.length;
        const p50 = sorted[Math.floor(sorted.length * 0.5)];
        const p90 = sorted[Math.floor(sorted.length * 0.9)];
        const p99 = sorted[Math.floor(sorted.length * 0.99)];
        return {
            count: sorted.length,
            avgMs: Math.round(avg),
            p50Ms: p50,
            p90Ms: p90,
            p99Ms: p99,
            minMs: sorted[0],
            maxMs: sorted[sorted.length - 1],
        };
    };

    return container;
}
