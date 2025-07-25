import type {GlobalConfig, UserManagementStatus} from "@devplan/contextify-api";
import {
  GetGlobalConfigResponse,
  GetUserManagementStatusResponse,
  UpdateGlobalConfigRequest,
  UpdateGlobalConfigResponse
} from "@devplan/contextify-api";
import type {StateCreator} from "zustand";
import {configAPI, usersStatusAPI} from "@/store/apiPaths.tsx";
import {fetchWithAuth} from "@/store/api.tsx";

export interface ConfigState {
  globalConfig: GlobalConfig | undefined;
  usersStatus: UserManagementStatus | undefined;

  fetchGlobalConfig: () => Promise<void>;
  updateGlobalConfig: (configUpdate: Partial<GlobalConfig>) => Promise<void>;
  fetchUsersConfig: () => Promise<void>;
}

export const createConfigSlice: StateCreator<
  ConfigState,
  [],
  [],
  ConfigState
> = ((set, get) => ({
  globalConfig: undefined,
  usersStatus: undefined,
  fetchGlobalConfig: async () => fetchWithAuth(configAPI(), GetGlobalConfigResponse)
    .then(r => set(s => ({...s, globalConfig: r.config}))),
  updateGlobalConfig: async update => fetchWithAuth(configAPI(),
    UpdateGlobalConfigResponse,
    {
      method: "POST", body: JSON.stringify(UpdateGlobalConfigRequest.toJSON(
        {config: {...get().globalConfig!, ...update}}
      ))
    }
  ).then(r => set(s => ({...s, globalConfig: r.config}))),
  fetchUsersConfig: async () => fetchWithAuth(usersStatusAPI(), GetUserManagementStatusResponse)
    .then(r => set(s => ({...s, usersStatus: r.status ?? {enabled: false}}))),
}))