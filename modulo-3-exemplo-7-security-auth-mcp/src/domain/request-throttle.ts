import { RateLimitError } from "./errors.ts";

export interface DdosSimulationResult {
    allowed: number;
    blocked: number;
    firstBlockedAt: number | null;
}

export class RequestThrottle {
    private readonly maxRequests: number;
    private readonly windowMs: number;
    private readonly timestamps: number[] = [];

    constructor(maxRequests: number, windowMs: number) {
        this.maxRequests = maxRequests;
        this.windowMs = windowMs;
    }

    get remaining(): number {
        this.prune();
        return Math.max(0, this.maxRequests - this.timestamps.length);
    }

    track(): void {
        this.prune();
        if (this.timestamps.length >= this.maxRequests) {
            throw new RateLimitError();
        }
        this.timestamps.push(Date.now());
    }

    reset(): void {
        this.timestamps.length = 0;
    }

    simulateDdosBurst(requestCount: number): DdosSimulationResult {
        const result: DdosSimulationResult = {
            allowed: 0,
            blocked: 0,
            firstBlockedAt: null,
        };

        for (let index = 0; index < requestCount; index++) {
            try {
                this.track();
                result.allowed++;
            } catch {
                result.blocked++;
                if (result.firstBlockedAt === null) {
                    result.firstBlockedAt = index + 1;
                }
            }
        }

        return result;
    }

    private prune(): void {
        const cutoff = Date.now() - this.windowMs;
        while (this.timestamps.length > 0 && this.timestamps[0]! < cutoff) {
            this.timestamps.shift();
        }
    }
}
