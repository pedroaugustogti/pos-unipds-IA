import type { Customer, CustomerQuery, CustomerMutation } from "../domain/customer.ts";
import { CustomerHttpClient } from "../infrastructure/customer-http-client.ts";
import { RequestThrottle } from "../domain/request-throttle.ts";

const DEFAULT_MAX_REQUESTS = 90;
const DEFAULT_WINDOW_MS = 60_000;

function createThrottleFromEnv(): RequestThrottle {
    const maxRequests = Number(process.env.RATE_LIMIT_MAX_REQUESTS ?? DEFAULT_MAX_REQUESTS);
    const windowMs = Number(process.env.RATE_LIMIT_WINDOW_MS ?? DEFAULT_WINDOW_MS);
    return new RequestThrottle(maxRequests, windowMs);
}

export class CustomerService {
    private readonly client: CustomerHttpClient;
    private readonly throttle: RequestThrottle;

    constructor(
        baseUrl: string,
        serviceToken: string,
        throttle = createThrottleFromEnv()
    ) {
        this.client = new CustomerHttpClient(baseUrl, serviceToken);
        this.throttle = throttle;
    }

    private guardRequest(): void {
        this.throttle.track();
    }

    async listCustomers(): Promise<Customer[]> {
        this.guardRequest();
        return this.client.listCustomers();
    }

    async createCustomer(customer: Omit<Customer, "_id">) {
        this.guardRequest();
        return this.client.createCustomer(customer);
    }

    async findCustomer(query: CustomerQuery): Promise<Customer | null> {
        this.guardRequest();
        if (query._id) return this.client.getCustomerById(query._id);

        const customers = await this.client.listCustomers();
        return (
            customers.find((customer) => {
                const entries = Object.entries(query) as [keyof Customer, string][];

                return entries.every(([key, value]) => {
                    const customerValue = customer[key];
                    return customerValue?.includes(value);
                });
            }) ?? null
        );
    }

    async updateCustomer(
        id: string,
        data: Partial<Omit<Customer, "_id">>
    ): Promise<CustomerMutation> {
        this.guardRequest();
        return this.client.updateCustomer(id, data);
    }

    async deleteCustomer(id: string): Promise<CustomerMutation> {
        this.guardRequest();
        return this.client.deleteCustomer(id);
    }
}
