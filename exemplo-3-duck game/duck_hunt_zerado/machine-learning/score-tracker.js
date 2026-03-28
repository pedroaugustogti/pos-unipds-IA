const STORAGE_KEY = 'duck-hunt-score-history';

export class ScoreTracker {
    constructor() {
        this.currentSession = {
            startedAt: new Date().toISOString(),
            entries: [],
        };
        this.history = this._loadHistory();
        this._startTime = Date.now();
    }

    record({ phase, level, score, x, y, box, dominantColors, hit, pipelineMs }) {
        const entry = {
            timestamp: Date.now() - this._startTime,
            phase,
            level,
            score: parseFloat(score),
            aim: { x: Math.round(x), y: Math.round(y) },
            box: box ? {
                x1: Math.round(box.x1),
                y1: Math.round(box.y1),
                x2: Math.round(box.x2),
                y2: Math.round(box.y2),
                width: Math.round(box.x2 - box.x1),
                height: Math.round(box.y2 - box.y1),
            } : null,
            dominantColors: dominantColors || [],
            hit: !!hit,
            pipelineMs: pipelineMs || 0,
        };
        this.currentSession.entries.push(entry);
        return entry;
    }

    _loadHistory() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            return raw ? JSON.parse(raw) : { sessions: [] };
        } catch {
            return { sessions: [] };
        }
    }

    save() {
        this.history.sessions.push(this.currentSession);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.history));
        console.log(`💾 Session saved (${this.currentSession.entries.length} entries). Total sessions: ${this.history.sessions.length}`);
    }

    _calcStats(entries) {
        if (entries.length === 0) {
            return { total: 0, hits: 0, misses: 0, hitRate: '0.00%', avgScore: '0.00', minScore: '0.00', maxScore: '0.00', avgPipelineMs: 0 };
        }

        const hits = entries.filter(e => e.hit).length;
        const scores = entries.map(e => e.score);
        const pipelines = entries.map(e => e.pipelineMs || 0).filter(v => v > 0);
        const avgPipeline = pipelines.length > 0
            ? Math.round(pipelines.reduce((a, b) => a + b, 0) / pipelines.length)
            : 0;

        return {
            total: entries.length,
            hits,
            misses: entries.length - hits,
            hitRate: ((hits / entries.length) * 100).toFixed(2) + '%',
            avgScore: (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(2),
            minScore: Math.min(...scores).toFixed(2),
            maxScore: Math.max(...scores).toFixed(2),
            avgPipelineMs: avgPipeline,
        };
    }

    _statsByLevel(entries) {
        const levels = {};
        for (const e of entries) {
            const key = e.level ?? 'unknown';
            if (!levels[key]) levels[key] = [];
            levels[key].push(e);
        }
        const result = {};
        for (const [lvl, list] of Object.entries(levels)) {
            result[lvl] = this._calcStats(list);
        }
        return result;
    }

    getMissAnalysis() {
        const misses = this.currentSession.entries.filter(e => !e.hit);
        const byLevel = {};
        for (const m of misses) {
            const key = m.level ?? 'unknown';
            if (!byLevel[key]) byLevel[key] = [];
            byLevel[key].push({
                aim: m.aim,
                box: m.box,
                colors: m.dominantColors,
                score: m.score,
            });
        }
        return byLevel;
    }

    getReport() {
        const before = this.currentSession.entries.filter(e => e.phase === 'before');
        const after = this.currentSession.entries.filter(e => e.phase === 'after');

        return {
            before: {
                overall: this._calcStats(before),
                byLevel: this._statsByLevel(before),
            },
            after: {
                overall: this._calcStats(after),
                byLevel: this._statsByLevel(after),
            },
            missAnalysis: this.getMissAnalysis(),
        };
    }

    printReport() {
        const report = this.getReport();
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('📊 Score Comparison Report');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

        for (const phase of ['before', 'after']) {
            const data = report[phase];
            if (data.overall.total === 0) continue;

            console.log(`\n🔹 ${phase.toUpperCase()} — Overall`);
            this._printStats(data.overall);

            for (const [lvl, stats] of Object.entries(data.byLevel)) {
                console.log(`\n   📍 Level ${lvl}`);
                this._printStats(stats, '      ');
            }
        }

        const missAnalysis = report.missAnalysis;
        const totalMisses = Object.values(missAnalysis).reduce((sum, arr) => sum + arr.length, 0);
        if (totalMisses > 0) {
            console.log(`\n❌ Miss Analysis (${totalMisses} misses)`);
            for (const [lvl, misses] of Object.entries(missAnalysis)) {
                console.log(`   Level ${lvl}: ${misses.length} misses`);
                for (const m of misses.slice(0, 3)) {
                    console.log(`     aim(${m.aim.x},${m.aim.y}) box[${m.box?.width}x${m.box?.height}] colors:[${m.colors.join(', ')}] score:${m.score}`);
                }
                if (misses.length > 3) console.log(`     ... and ${misses.length - 3} more`);
            }
        }

        if (report.before.overall.total > 0 && report.after.overall.total > 0) {
            const diff = (parseFloat(report.after.overall.hitRate) - parseFloat(report.before.overall.hitRate)).toFixed(2);
            const sign = diff >= 0 ? '+' : '';
            console.log(`\n📈 Hit rate change: ${sign}${diff}%`);
        }

        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    }

    _printStats(s, indent = '   ') {
        console.log(`${indent}Total: ${s.total} | Hits: ${s.hits} | Misses: ${s.misses}`);
        console.log(`${indent}Hit rate: ${s.hitRate} | Pipeline: ${s.avgPipelineMs}ms avg`);
        console.log(`${indent}Score — avg: ${s.avgScore} | min: ${s.minScore} | max: ${s.maxScore}`);
    }

    compareWithPrevious() {
        if (this.history.sessions.length === 0) {
            console.log('📭 No previous sessions to compare');
            return null;
        }

        const prev = this.history.sessions[this.history.sessions.length - 1];
        const prevStats = this._calcStats(prev.entries);
        const currStats = this._calcStats(this.currentSession.entries);

        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('🔄 Session Comparison (current vs previous)');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('\n🕐 Previous session:', prev.startedAt);
        this._printStats(prevStats);
        console.log('\n🕐 Current session:', this.currentSession.startedAt);
        this._printStats(currStats);

        const diff = (parseFloat(currStats.hitRate) - parseFloat(prevStats.hitRate)).toFixed(2);
        const sign = diff >= 0 ? '+' : '';
        console.log(`\n📈 Hit rate change: ${sign}${diff}%`);
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

        return { previous: prevStats, current: currStats, diff };
    }

    exportJSON() {
        const data = {
            currentSession: this.currentSession,
            history: this.history,
        };
        const json = JSON.stringify(data, null, 2);
        console.log('📄 JSON exported (' + this.currentSession.entries.length + ' entries)');
        return json;
    }

    downloadJSON() {
        const json = this.exportJSON();
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `duck-hunt-scores-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    reset() {
        this.currentSession = {
            startedAt: new Date().toISOString(),
            entries: [],
        };
        this._startTime = Date.now();
    }

    clearHistory() {
        this.history = { sessions: [] };
        localStorage.removeItem(STORAGE_KEY);
        console.log('🗑️ History cleared');
    }
}
