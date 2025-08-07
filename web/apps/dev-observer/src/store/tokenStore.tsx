import type {StateCreator} from "zustand";
import {fetchWithAuth} from "@/store/api.tsx";
import {
  AddTokenRequest,
  AddTokenResponse,
  DeleteTokenResponse,
  GetTokenResponse,
  ListTokensRequest,
  ListTokensResponse,
  RepoToken,
  UpdateTokenRequest,
  UpdateTokenResponse
} from "@devplan/contextify-api";
import {tokenAPI, tokensAPI, tokensListAPI} from "@/store/apiPaths.tsx";

export interface TokenState {
  tokens: Record<string, RepoToken>;

  listTokens: (req: ListTokensRequest) => Promise<string[]>;
  fetchTokenById: (id: string) => Promise<void>;
  addToken: (token: RepoToken) => Promise<void>;
  updateToken: (id: string, tokenData: { token: string }) => Promise<void>;
  deleteToken: (id: string) => Promise<void>;
}

export const createTokensSlice: StateCreator<
  TokenState,
  [],
  [],
  TokenState
> = ((set) => ({
  tokens: {},

  listTokens: async req => fetchWithAuth(tokensListAPI(), ListTokensResponse, {
    method: "POST", body: JSON.stringify(ListTokensRequest.toJSON(req)),
  }).then(res => {
    const {tokens} = res;
    const tokenMap = tokens.reduce((a, t) => ({...a, [t.id]: t}), {} as Record<string, RepoToken>);
    set(s => ({...s, tokens: {...s.tokens, ...tokenMap}}));
    return tokens.map(t => t.id);
  }),

  fetchTokenById: async id => fetchWithAuth(tokenAPI(id), GetTokenResponse)
    .then(r => {
      const {token} = r;
      if (token) {
        set(s => ({...s, tokens: {...s.tokens, [token.id]: token}}));
      }
    }),

  addToken: async token => {
    return fetchWithAuth(
      tokensAPI(),
      AddTokenResponse,
      {method: "POST", body: JSON.stringify(AddTokenRequest.toJSON({token}))},
    ).then(r => {
      const {token} = r;
      if (token) {
        set(s => ({...s, tokens: {...s.tokens, [token.id]: token}}));
      }
    });
  },

  updateToken: async (id, tokenData) => fetchWithAuth(
    tokenAPI(id),
    UpdateTokenResponse,
    {method: "PUT", body: JSON.stringify(UpdateTokenRequest.toJSON(tokenData))},
  ).then(r => {
    const {token} = r;
    if (token) {
      set(s => ({...s, tokens: {...s.tokens, [token.id]: token}}));
    }
  }),

  deleteToken: async id => fetchWithAuth(tokenAPI(id), DeleteTokenResponse, {method: "DELETE"})
    .then(() => {
      return
    }),
}));