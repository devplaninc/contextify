import axios, {AxiosInstance, AxiosRequestConfig} from 'axios';

export interface ParseableMessage<T> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  fromJSON(object: any): T;
}

export class VoidParser implements ParseableMessage<void> {

  fromJSON(): void {
    return
  }
}

/**
 * Base client for making API requests
 */
export class BaseClient {
  protected readonly client: AxiosInstance;
  protected readonly baseUrl: string;

  /**
   * Create a new BaseClient
   * @param baseUrl - The base URL for the API
   * @param config - Additional Axios configuration
   */
  constructor(baseUrl: string = 'http://localhost:8090', config: AxiosRequestConfig = {}) {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      ...config,
    });
  }

  /**
   * Set the authorization token for API requests
   * @param token - The authorization token
   */
  setAuthToken(token: string): void {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  /**
   * Clear the authorization token
   */
  clearAuthToken(): void {
    delete this.client.defaults.headers.common['Authorization'];
  }

  protected async _get<T>(url: string, response: ParseableMessage<T>, config?: AxiosRequestConfig): Promise<T> {
    const resp = await this.client.get<T>(url, config);
    return response.fromJSON(resp.data);
  }

  protected async _post<T>(
    url: string,
    response: ParseableMessage<T>,
    data?: unknown,
    config?: AxiosRequestConfig,
  ): Promise<T> {
    const resp = await this.client.post<T>(url, data, config);
    return response.fromJSON(resp.data)
  }

  protected async _delete<T>(
    url: string,
    response: ParseableMessage<T>,
    data?: unknown,
    config?: AxiosRequestConfig,
  ): Promise<T> {
    const resp = await this.client.delete<T>(url, { ...config, data });
    return response.fromJSON(resp.data);
  }
}