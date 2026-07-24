import { describe, it } from 'node:test'
import assert from 'node:assert'
import { assertToolAccess, canAccessTool } from '../../src/domain/authorization.ts'
import { ForbiddenError } from '../../src/domain/errors.ts'

describe('authorization by role and department', () => {
  it('allows admin from sales to create customers', () => {
    assert.strictEqual(
      canAccessTool('create_customer', { role: 'admin', department: 'sales' }),
      true
    )
  })

  it('blocks admin from support from creating customers', () => {
    assert.strictEqual(
      canAccessTool('create_customer', { role: 'admin', department: 'support' }),
      false
    )
    assert.throws(
      () => assertToolAccess('create_customer', { role: 'admin', department: 'support' }),
      (error: Error) => {
        assert.ok(error instanceof ForbiddenError)
        assert.match(error.message, /department 'support'/)
        return true
      }
    )
  })

  it('blocks member from sales from deleting customers', () => {
    assert.throws(
      () => assertToolAccess('delete_customer', { role: 'member', department: 'sales' }),
      (error: Error) => {
        assert.ok(error instanceof ForbiddenError)
        assert.match(error.message, /role 'member'/)
        return true
      }
    )
  })

  it('allows member from support to update customers', () => {
    assert.strictEqual(
      canAccessTool('update_customer', { role: 'member', department: 'support' }),
      true
    )
  })

  it('blocks member from engineering from updating customers', () => {
    assert.throws(
      () => assertToolAccess('update_customer', { role: 'member', department: 'engineering' }),
      (error: Error) => {
        assert.ok(error instanceof ForbiddenError)
        assert.match(error.message, /department 'engineering'/)
        return true
      }
    )
  })

  it('allows any department to list customers', () => {
    for (const department of ['sales', 'support', 'engineering'] as const) {
      assert.strictEqual(
        canAccessTool('list_customers', { role: 'member', department }),
        true
      )
    }
  })
})
