// Code generated by protoc-gen-ts_proto. DO NOT EDIT.
// versions:
//   protoc-gen-ts_proto  v2.7.5
//   protoc               v5.28.3
// source: dev_observer/api/storage/local.proto

/* eslint-disable */
import { BinaryReader, BinaryWriter } from "@bufbuild/protobuf/wire";
import { GlobalConfig } from "../types/config";
import { ProcessingItem, ProcessingItemResult } from "../types/processing";
import { GitHubRepository } from "../types/repo";
import { WebSite } from "../types/sites";

export const protobufPackage = "dev_observer.api.storage.local";

export interface LocalStorageData {
  githubRepos: GitHubRepository[];
  processingItems: ProcessingItem[];
  globalConfig: GlobalConfig | undefined;
  webSites: WebSite[];
  processingResults: ProcessingItemResult[];
}

function createBaseLocalStorageData(): LocalStorageData {
  return { githubRepos: [], processingItems: [], globalConfig: undefined, webSites: [], processingResults: [] };
}

export const LocalStorageData: MessageFns<LocalStorageData> = {
  encode(message: LocalStorageData, writer: BinaryWriter = new BinaryWriter()): BinaryWriter {
    for (const v of message.githubRepos) {
      GitHubRepository.encode(v!, writer.uint32(10).fork()).join();
    }
    for (const v of message.processingItems) {
      ProcessingItem.encode(v!, writer.uint32(18).fork()).join();
    }
    if (message.globalConfig !== undefined) {
      GlobalConfig.encode(message.globalConfig, writer.uint32(26).fork()).join();
    }
    for (const v of message.webSites) {
      WebSite.encode(v!, writer.uint32(34).fork()).join();
    }
    for (const v of message.processingResults) {
      ProcessingItemResult.encode(v!, writer.uint32(42).fork()).join();
    }
    return writer;
  },

  decode(input: BinaryReader | Uint8Array, length?: number): LocalStorageData {
    const reader = input instanceof BinaryReader ? input : new BinaryReader(input);
    const end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseLocalStorageData();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1: {
          if (tag !== 10) {
            break;
          }

          message.githubRepos.push(GitHubRepository.decode(reader, reader.uint32()));
          continue;
        }
        case 2: {
          if (tag !== 18) {
            break;
          }

          message.processingItems.push(ProcessingItem.decode(reader, reader.uint32()));
          continue;
        }
        case 3: {
          if (tag !== 26) {
            break;
          }

          message.globalConfig = GlobalConfig.decode(reader, reader.uint32());
          continue;
        }
        case 4: {
          if (tag !== 34) {
            break;
          }

          message.webSites.push(WebSite.decode(reader, reader.uint32()));
          continue;
        }
        case 5: {
          if (tag !== 42) {
            break;
          }

          message.processingResults.push(ProcessingItemResult.decode(reader, reader.uint32()));
          continue;
        }
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skip(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): LocalStorageData {
    return {
      githubRepos: gt.Array.isArray(object?.githubRepos)
        ? object.githubRepos.map((e: any) => GitHubRepository.fromJSON(e))
        : [],
      processingItems: gt.Array.isArray(object?.processingItems)
        ? object.processingItems.map((e: any) => ProcessingItem.fromJSON(e))
        : [],
      globalConfig: isSet(object.globalConfig) ? GlobalConfig.fromJSON(object.globalConfig) : undefined,
      webSites: gt.Array.isArray(object?.webSites) ? object.webSites.map((e: any) => WebSite.fromJSON(e)) : [],
      processingResults: gt.Array.isArray(object?.processingResults)
        ? object.processingResults.map((e: any) => ProcessingItemResult.fromJSON(e))
        : [],
    };
  },

  toJSON(message: LocalStorageData): unknown {
    const obj: any = {};
    if (message.githubRepos?.length) {
      obj.githubRepos = message.githubRepos.map((e) => GitHubRepository.toJSON(e));
    }
    if (message.processingItems?.length) {
      obj.processingItems = message.processingItems.map((e) => ProcessingItem.toJSON(e));
    }
    if (message.globalConfig !== undefined) {
      obj.globalConfig = GlobalConfig.toJSON(message.globalConfig);
    }
    if (message.webSites?.length) {
      obj.webSites = message.webSites.map((e) => WebSite.toJSON(e));
    }
    if (message.processingResults?.length) {
      obj.processingResults = message.processingResults.map((e) => ProcessingItemResult.toJSON(e));
    }
    return obj;
  },

  create(base?: DeepPartial<LocalStorageData>): LocalStorageData {
    return LocalStorageData.fromPartial(base ?? {});
  },
  fromPartial(object: DeepPartial<LocalStorageData>): LocalStorageData {
    const message = createBaseLocalStorageData();
    message.githubRepos = object.githubRepos?.map((e) => GitHubRepository.fromPartial(e)) || [];
    message.processingItems = object.processingItems?.map((e) => ProcessingItem.fromPartial(e)) || [];
    message.globalConfig = (object.globalConfig !== undefined && object.globalConfig !== null)
      ? GlobalConfig.fromPartial(object.globalConfig)
      : undefined;
    message.webSites = object.webSites?.map((e) => WebSite.fromPartial(e)) || [];
    message.processingResults = object.processingResults?.map((e) => ProcessingItemResult.fromPartial(e)) || [];
    return message;
  },
};

declare const self: any | undefined;
declare const window: any | undefined;
declare const global: any | undefined;
const gt: any = (() => {
  if (typeof globalThis !== "undefined") {
    return globalThis;
  }
  if (typeof self !== "undefined") {
    return self;
  }
  if (typeof window !== "undefined") {
    return window;
  }
  if (typeof global !== "undefined") {
    return global;
  }
  throw "Unable to locate global object";
})();

type Builtin = Date | Function | Uint8Array | string | number | boolean | undefined;

export type DeepPartial<T> = T extends Builtin ? T
  : T extends globalThis.Array<infer U> ? globalThis.Array<DeepPartial<U>>
  : T extends ReadonlyArray<infer U> ? ReadonlyArray<DeepPartial<U>>
  : T extends { $case: string; value: unknown } ? { $case: T["$case"]; value?: DeepPartial<T["value"]> }
  : T extends {} ? { [K in keyof T]?: DeepPartial<T[K]> }
  : Partial<T>;

function isSet(value: any): boolean {
  return value !== null && value !== undefined;
}

export interface MessageFns<T> {
  encode(message: T, writer?: BinaryWriter): BinaryWriter;
  decode(input: BinaryReader | Uint8Array, length?: number): T;
  fromJSON(object: any): T;
  toJSON(message: T): unknown;
  create(base?: DeepPartial<T>): T;
  fromPartial(object: DeepPartial<T>): T;
}
