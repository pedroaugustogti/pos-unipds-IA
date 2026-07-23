const PHONE_MASK_LENGTH = 11;

export function formatPhoneMask(phone: string): string {
    const digits = phone.replace(/\D/g, "");
    const normalized = digits.length > PHONE_MASK_LENGTH
        ? digits.slice(-PHONE_MASK_LENGTH)
        : digits.padStart(PHONE_MASK_LENGTH, "0");

    const areaCode = normalized.slice(0, 2);
    const firstPart = normalized.slice(2, 7);
    const secondPart = normalized.slice(7, 11);

    return `(${areaCode}) ${firstPart}-${secondPart}`;
}
