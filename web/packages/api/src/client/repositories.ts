import {BaseClient} from './base';
import {
  AddRepositoryRequest,
  AddRepositoryResponse,
  DeleteRepositoryResponse,
  GetRepositoryResponse,
  ListRepositoriesResponse,
  RescanRepositoryResponse
} from '../pb/dev_observer/api/web/repositories';

/**
 * Client for interacting with the Repositories API
 */
export class RepositoriesClient extends BaseClient {
  /**
   * Add a repository
   * @param request - The add repository request
   * @returns The add repository response
   */
  async add(request: AddRepositoryRequest): Promise<AddRepositoryResponse> {
    return this._post('/api/v1/repositories', AddRepositoryResponse,  AddRepositoryRequest.toJSON(request));
  }

  /**
   * List all repositories
   * @returns The list repositories response
   */
  async list(): Promise<ListRepositoriesResponse> {
    return this._get('/api/v1/repositories', ListRepositoriesResponse);
  }

  /**
   * Get a specific repository
   * @param repoId - The repository ID
   * @returns The get repository response
   */
  async get(repoId: string): Promise<GetRepositoryResponse> {
    return this._get(`/api/v1/repositories/${repoId}`, GetRepositoryResponse);
  }

  /**
   * Delete a specific repository
   * @param repoId - The repository ID
   * @returns The delete repository response
   */
  async delete(repoId: string): Promise<DeleteRepositoryResponse> {
    return this._delete(`/api/v1/repositories/${repoId}`, DeleteRepositoryResponse);
  }

  /**
   * Trigger a rescan of a specific repository
   * @param repoId - The repository ID
   * @returns The rescan repository response
   */
  async rescan(repoId: string): Promise<RescanRepositoryResponse> {
    return this._post(`/api/v1/repositories/${repoId}/rescan`, RescanRepositoryResponse);
  }
}