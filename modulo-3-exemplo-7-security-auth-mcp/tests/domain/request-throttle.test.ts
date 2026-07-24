import { describe, it } from 'node:test'
import assert from 'node:assert'
import { RequestThrottle } from '../../src/domain/request-throttle.ts'
import { RateLimitError } from '../../src/domain/errors.ts'

describe('RequestThrottle DDoS simulation', () => {
  it('blocks burst traffic after the configured threshold', () => {
    const throttle = new RequestThrottle(10, 60_000)
    const result = throttle.simulateDdosBurst(25)

    assert.strictEqual(result.allowed, 10)
    assert.strictEqual(result.blocked, 15)
    assert.strictEqual(result.firstBlockedAt, 11)
  })

  it('throws RateLimitError when tracking beyond the limit', () => {
    const throttle = new RequestThrottle(3, 60_000)

    throttle.track()
    throttle.track()
    throttle.track()

    assert.throws(() => throttle.track(), RateLimitError)
    assert.strictEqual(throttle.remaining, 0)
  })

  it('simulates coordinated DDoS from multiple parallel bursts', () => {
    const throttle = new RequestThrottle(5, 1_000)
    const waves = [5, 5, 5, 5]
    let totalBlocked = 0
    let totalAllowed = 0

    for (const waveSize of waves) {
      const result = throttle.simulateDdosBurst(waveSize)
      totalAllowed += result.allowed
      totalBlocked += result.blocked
    }

    assert.strictEqual(totalAllowed, 5)
    assert.strictEqual(totalBlocked, 15)
  })

  it('recovers after the sliding window expires', async () => {
    const throttle = new RequestThrottle(2, 50)
    throttle.simulateDdosBurst(4)
    assert.strictEqual(throttle.remaining, 0)

    await new Promise((resolve) => setTimeout(resolve, 60))

    throttle.track()
    assert.strictEqual(throttle.remaining, 1)
  })
})
