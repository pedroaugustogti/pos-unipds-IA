import type { Department, Role, TokenContext } from "./token-context.ts";
import { ForbiddenError } from "./errors.ts";

export type ToolName =
    | "list_customers"
    | "get_customer"
    | "create_customer"
    | "update_customer"
    | "delete_customer";

interface ToolPermission {
    roles: Role[];
    departments: Department[];
}

const TOOL_PERMISSIONS: Record<ToolName, ToolPermission> = {
    list_customers: {
        roles: ["admin", "member"],
        departments: ["sales", "support", "engineering"],
    },
    get_customer: {
        roles: ["admin", "member"],
        departments: ["sales", "support", "engineering"],
    },
    create_customer: {
        roles: ["admin"],
        departments: ["sales"],
    },
    update_customer: {
        roles: ["admin", "member"],
        departments: ["sales", "support"],
    },
    delete_customer: {
        roles: ["admin"],
        departments: ["sales"],
    },
};

export function canAccessTool(tool: ToolName, context: TokenContext): boolean {
    const permission = TOOL_PERMISSIONS[tool];
    return (
        permission.roles.includes(context.role) &&
        permission.departments.includes(context.department)
    );
}

export function assertToolAccess(tool: ToolName, context: TokenContext): void {
    const permission = TOOL_PERMISSIONS[tool];

    if (!permission.roles.includes(context.role)) {
        throw new ForbiddenError(
            `Forbidden: role '${context.role}' cannot execute '${tool}'`
        );
    }

    if (!permission.departments.includes(context.department)) {
        throw new ForbiddenError(
            `Forbidden: department '${context.department}' cannot execute '${tool}'`
        );
    }
}
