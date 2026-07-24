export type Role = "admin" | "member";
export type Department = "sales" | "support" | "engineering";

export interface TokenContext {
    role: Role;
    department: Department;
}

export interface ServiceTokenMetadata extends TokenContext {
    serviceToken: string;
}

const ROLES: Role[] = ["admin", "member"];
const DEPARTMENTS: Department[] = ["sales", "support", "engineering"];

export function isRole(value: string): value is Role {
    return ROLES.includes(value as Role);
}

export function isDepartment(value: string): value is Department {
    return DEPARTMENTS.includes(value as Department);
}

export function parseTokenContextFromEnv(): TokenContext {
    const role = process.env.SERVICE_TOKEN_ROLE ?? "";
    const department = process.env.SERVICE_TOKEN_DEPARTMENT ?? "";

    if (!isRole(role)) {
        throw new Error(
            `SERVICE_TOKEN_ROLE must be one of: ${ROLES.join(", ")}`
        );
    }
    if (!isDepartment(department)) {
        throw new Error(
            `SERVICE_TOKEN_DEPARTMENT must be one of: ${DEPARTMENTS.join(", ")}`
        );
    }

    return { role, department };
}
