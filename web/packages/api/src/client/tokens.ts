import {BaseClient} from './base';
import {
  AddTokenRequest,
  AddTokenResponse,
  DeleteTokenResponse,
  GetTokenResponse,
  ListTokensRequest,
  ListTokensResponse,
  UpdateTokenRequest,
  UpdateTokenResponse
} from '../pb/dev_observer/api/web/tokens';

/**
 * Client for interacting with the Tokens API
 */
export class TokensClient extends BaseClient {
  /**
   * Add a token
   * @param request - The add token request
   * @returns The add token response
   */
  async add(request: AddTokenRequest): Promise<AddTokenResponse> {
    return this._post('/api/v1/tokens', AddTokenResponse, AddTokenRequest.toJSON(request));
  }

  /**
   * List tokens
   * @param request - The list tokens request (optional namespace filter)
   * @returns The list tokens response
   */
  async list(request: ListTokensRequest = {}): Promise<ListTokensResponse> {
    return this._post('/api/v1/tokens/list', ListTokensResponse, ListTokensRequest.toJSON(request));
  }

  /**
   * Get a specific token
   * @param tokenId - The token ID
   * @returns The get token response
   */
  async get(tokenId: string): Promise<GetTokenResponse> {
    return this._get(`/api/v1/tokens/token/${tokenId}`, GetTokenResponse);
  }

  /**
   * Update a specific token
   * @param tokenId - The token ID
   * @param request - The update token request
   * @returns The update token response
   */
  async update(tokenId: string, request: UpdateTokenRequest): Promise<UpdateTokenResponse> {
    return this._put(`/api/v1/tokens/token/${tokenId}`, UpdateTokenResponse, UpdateTokenRequest.toJSON(request));
  }

  /**
   * Delete a specific token
   * @param tokenId - The token ID
   * @returns The delete token response
   */
  async delete(tokenId: string): Promise<DeleteTokenResponse> {
    return this._delete(`/api/v1/tokens/token/${tokenId}`, DeleteTokenResponse);
  }
}