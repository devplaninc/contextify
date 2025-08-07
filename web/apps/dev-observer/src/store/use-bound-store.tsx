import {createWithEqualityFn as create} from "zustand/traditional";
import {type ConfigState, createConfigSlice} from "@/store/configStore.tsx";
import {createRepositoriesSlice, type RepositoryState} from "@/store/repositoryStore.tsx";
import {createObservationsSlice, type ObservationsState} from "@/store/observationsStore.tsx";
import {createWebSitesSlice, type WebSiteState} from "@/store/websiteStore.tsx";
import {createTokensSlice, type TokenState} from "@/store/tokenStore.tsx";

export const useBoundStore = create<
  ConfigState & RepositoryState & ObservationsState & WebSiteState & TokenState
>()((...a) => ({
  ...createConfigSlice(...a),
  ...createRepositoriesSlice(...a),
  ...createObservationsSlice(...a),
  ...createWebSitesSlice(...a),
  ...createTokensSlice(...a),
}))
