import { describe, it } from "node:test";
import assert from "node:assert";
import { formatPhoneMask } from "../../src/domain/phoneMask.ts";

describe("formatPhoneMask", () => {
    it("should format an 11-digit phone number", () => {
        assert.strictEqual(formatPhoneMask("11999998888"), "(11) 99999-8888");
    });

    it("should strip non-digit characters before formatting", () => {
        assert.strictEqual(formatPhoneMask("(11) 99999-8888"), "(11) 99999-8888");
        assert.strictEqual(formatPhoneMask("999-000-111"), "(00) 99900-0111");
    });

    it("should pad missing digits on the left with zeros", () => {
        assert.strictEqual(formatPhoneMask("123"), "(00) 00000-0123");
        assert.strictEqual(formatPhoneMask("1198888"), "(00) 00119-8888");
    });

    it("should use only the last 11 digits when input is longer", () => {
        assert.strictEqual(formatPhoneMask("5511999998888"), "(11) 99999-8888");
    });

    it("should return all zeros when phone has no digits", () => {
        assert.strictEqual(formatPhoneMask(""), "(00) 00000-0000");
        assert.strictEqual(formatPhoneMask("abc"), "(00) 00000-0000");
    });
});
