import { BaseClient } from './base';
import {
  GetObservationResponse,
  GetObservationsResponse,
  CreateProcessingItemRequest,
  CreateProcessingItemResponse,
  DeleteProcessingItemRequest,
  DeleteProcessingItemResponse,
  GetProcessingResultsRequest,
  GetProcessingResultsResponse,
  GetProcessingResultResponse,
  GetProcessingRunStatusResponse,
  GetProcessingItemsRequest,
  GetProcessingItemsResponse
} from '../pb/dev_observer/api/web/observations';

/**
 * Client for interacting with the Observations API
 */
export class ObservationsClient extends BaseClient {
  async listByKind(kind: string): Promise<GetObservationsResponse> {
    return this._get(`/api/v1/observations/kind/${kind}`, GetObservationsResponse);
  }

  async get(kind: string, name: string, key: string): Promise<GetObservationResponse> {
    // The server replaces / with | in the key parameter
    const encodedKey = key.replace(/\//g, '|');
    return this._get(`/api/v1/observation/${kind}/${name}/${encodedKey}`, GetObservationResponse);
  }

  async addProcessingItem(request: CreateProcessingItemRequest): Promise<CreateProcessingItemResponse> {
    return this._post(
      `/api/v1/processing/items`, CreateProcessingItemResponse, CreateProcessingItemRequest.toJSON(request));
  }

  async getFilteredProcessingItems(request: GetProcessingItemsRequest): Promise<GetProcessingItemsResponse> {
    return this._post(
      `/api/v1/processing/items/filter`, GetProcessingItemsResponse, GetProcessingItemsRequest.toJSON(request));
  }

  async deleteProcessingItem(request: DeleteProcessingItemRequest): Promise<DeleteProcessingItemResponse> {
    return this._delete(
      `/api/v1/processing/items`, DeleteProcessingItemResponse, DeleteProcessingItemRequest.toJSON(request));
  }

  async getProcessingResults(request: GetProcessingResultsRequest): Promise<GetProcessingResultsResponse> {
    return this._post(
      `/api/v1/processing/results`, GetProcessingResultsResponse, GetProcessingResultsRequest.toJSON(request));
  }

  async getProcessingResult(resultId: string): Promise<GetProcessingResultResponse> {
    return this._get(`/api/v1/processing/results/${resultId}`, GetProcessingResultResponse);
  }

  async getProcessingRequestStatus(requestId: string): Promise<GetProcessingRunStatusResponse> {
    return this._get(`/api/v1/processing/requests/runs/${requestId}`, GetProcessingRunStatusResponse);
  }
}