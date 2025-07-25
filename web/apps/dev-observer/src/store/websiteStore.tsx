import type {StateCreator} from "zustand";
import {baseAPI} from "@/store/apiPaths.tsx";
import {
  AddWebSiteRequest,
  AddWebSiteResponse,
  DeleteWebSiteResponse,
  GetWebSiteResponse,
  ListWebSitesResponse,
  RescanWebSiteResponse,
  WebSite
} from "@devplan/contextify-api";
import {fetchWithAuth} from "@/store/api.tsx";

// Define API paths for websites
export function websitesAPI() {
  return `${baseAPI()}/websites` as const;
}

export function websiteAPI<W extends string>(websiteId: W) {
  return `${websitesAPI()}/${websiteId}` as const;
}

export function websiteRescanAPI<W extends string>(websiteId: W) {
  return `${websiteAPI(websiteId)}/rescan` as const;
}

// Define the website state
export interface WebSiteState {
  websites: Record<string, WebSite>;

  fetchWebSites: () => Promise<void>;
  fetchWebSite: (id: string) => Promise<void>;
  addWebSite: (url: string) => Promise<void>;
  deleteWebSite: (id: string) => Promise<void>;
  rescanWebSite: (id: string) => Promise<void>;
}

// Create the website slice
export const createWebSitesSlice: StateCreator<
  WebSiteState,
  [],
  [],
  WebSiteState
> = ((set) => ({
  websites: {},

  fetchWebSites: async () => fetchWithAuth(websitesAPI(), ListWebSitesResponse)
    .then(({sites}) => {
      const websites = sites.reduce((a, w) => ({...a, [w.url]: w}), {} as Record<string, WebSite>)
      set(s => ({...s, websites}))
    }),

  fetchWebSite: async id => fetchWithAuth(websiteAPI(id), GetWebSiteResponse)
    .then(({site}) => {
      if (site) {
        set(s => ({...s, websites: {...s.websites, [site.id]: site}}))
      }
    }),

  addWebSite: async url => fetchWithAuth(
    websitesAPI(),
    AddWebSiteResponse,
    {method: "POST", body: JSON.stringify(AddWebSiteRequest.toJSON({url, scanIfNew: true}))},
  ).then(({site}) => {
    if (site) {
      set(s => ({...s, websites: {...s.websites, [site.url]: site}}))
    }
  }),

  deleteWebSite: async id => fetchWithAuth(websiteAPI(id), DeleteWebSiteResponse, {method: "DELETE"})
    .then(({sites}) => {
      const websites = sites.reduce((a, w) => ({...a, [w.id]: w}), {} as Record<string, WebSite>)
      set(s => ({...s, websites}))
    }),

  rescanWebSite: async id => fetchWithAuth(
    websiteRescanAPI(id),
    RescanWebSiteResponse,
    {method: "POST"},
  ).then(() => {
    return
  }),
}));
