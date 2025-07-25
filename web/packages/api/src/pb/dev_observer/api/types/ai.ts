// Code generated by protoc-gen-ts_proto. DO NOT EDIT.
// versions:
//   protoc-gen-ts_proto  v2.7.5
//   protoc               v5.28.3
// source: dev_observer/api/types/ai.proto

/* eslint-disable */
import { BinaryReader, BinaryWriter } from "@bufbuild/protobuf/wire";

export const protobufPackage = "dev_observer.api.types.ai";

export interface PromptConfig {
  model: ModelConfig | undefined;
}

export interface ModelConfig {
  provider: string;
  modelName: string;
  temperature: number;
}

export interface SystemMessage {
  text: string;
}

export interface UserMessage {
  text?: string | undefined;
  imageUrl?: string | undefined;
}

export interface PromptTemplate {
  system?: SystemMessage | undefined;
  user?: UserMessage | undefined;
  config: PromptConfig | undefined;
}

function createBasePromptConfig(): PromptConfig {
  return { model: undefined };
}

export const PromptConfig: MessageFns<PromptConfig> = {
  encode(message: PromptConfig, writer: BinaryWriter = new BinaryWriter()): BinaryWriter {
    if (message.model !== undefined) {
      ModelConfig.encode(message.model, writer.uint32(10).fork()).join();
    }
    return writer;
  },

  decode(input: BinaryReader | Uint8Array, length?: number): PromptConfig {
    const reader = input instanceof BinaryReader ? input : new BinaryReader(input);
    const end = length === undefined ? reader.len : reader.pos + length;
    const message = createBasePromptConfig();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1: {
          if (tag !== 10) {
            break;
          }

          message.model = ModelConfig.decode(reader, reader.uint32());
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

  fromJSON(object: any): PromptConfig {
    return { model: isSet(object.model) ? ModelConfig.fromJSON(object.model) : undefined };
  },

  toJSON(message: PromptConfig): unknown {
    const obj: any = {};
    if (message.model !== undefined) {
      obj.model = ModelConfig.toJSON(message.model);
    }
    return obj;
  },

  create(base?: DeepPartial<PromptConfig>): PromptConfig {
    return PromptConfig.fromPartial(base ?? {});
  },
  fromPartial(object: DeepPartial<PromptConfig>): PromptConfig {
    const message = createBasePromptConfig();
    message.model = (object.model !== undefined && object.model !== null)
      ? ModelConfig.fromPartial(object.model)
      : undefined;
    return message;
  },
};

function createBaseModelConfig(): ModelConfig {
  return { provider: "", modelName: "", temperature: 0 };
}

export const ModelConfig: MessageFns<ModelConfig> = {
  encode(message: ModelConfig, writer: BinaryWriter = new BinaryWriter()): BinaryWriter {
    if (message.provider !== "") {
      writer.uint32(10).string(message.provider);
    }
    if (message.modelName !== "") {
      writer.uint32(18).string(message.modelName);
    }
    if (message.temperature !== 0) {
      writer.uint32(29).float(message.temperature);
    }
    return writer;
  },

  decode(input: BinaryReader | Uint8Array, length?: number): ModelConfig {
    const reader = input instanceof BinaryReader ? input : new BinaryReader(input);
    const end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseModelConfig();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1: {
          if (tag !== 10) {
            break;
          }

          message.provider = reader.string();
          continue;
        }
        case 2: {
          if (tag !== 18) {
            break;
          }

          message.modelName = reader.string();
          continue;
        }
        case 3: {
          if (tag !== 29) {
            break;
          }

          message.temperature = reader.float();
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

  fromJSON(object: any): ModelConfig {
    return {
      provider: isSet(object.provider) ? gt.String(object.provider) : "",
      modelName: isSet(object.modelName) ? gt.String(object.modelName) : "",
      temperature: isSet(object.temperature) ? gt.Number(object.temperature) : 0,
    };
  },

  toJSON(message: ModelConfig): unknown {
    const obj: any = {};
    if (message.provider !== "") {
      obj.provider = message.provider;
    }
    if (message.modelName !== "") {
      obj.modelName = message.modelName;
    }
    if (message.temperature !== 0) {
      obj.temperature = message.temperature;
    }
    return obj;
  },

  create(base?: DeepPartial<ModelConfig>): ModelConfig {
    return ModelConfig.fromPartial(base ?? {});
  },
  fromPartial(object: DeepPartial<ModelConfig>): ModelConfig {
    const message = createBaseModelConfig();
    message.provider = object.provider ?? "";
    message.modelName = object.modelName ?? "";
    message.temperature = object.temperature ?? 0;
    return message;
  },
};

function createBaseSystemMessage(): SystemMessage {
  return { text: "" };
}

export const SystemMessage: MessageFns<SystemMessage> = {
  encode(message: SystemMessage, writer: BinaryWriter = new BinaryWriter()): BinaryWriter {
    if (message.text !== "") {
      writer.uint32(10).string(message.text);
    }
    return writer;
  },

  decode(input: BinaryReader | Uint8Array, length?: number): SystemMessage {
    const reader = input instanceof BinaryReader ? input : new BinaryReader(input);
    const end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseSystemMessage();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1: {
          if (tag !== 10) {
            break;
          }

          message.text = reader.string();
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

  fromJSON(object: any): SystemMessage {
    return { text: isSet(object.text) ? gt.String(object.text) : "" };
  },

  toJSON(message: SystemMessage): unknown {
    const obj: any = {};
    if (message.text !== "") {
      obj.text = message.text;
    }
    return obj;
  },

  create(base?: DeepPartial<SystemMessage>): SystemMessage {
    return SystemMessage.fromPartial(base ?? {});
  },
  fromPartial(object: DeepPartial<SystemMessage>): SystemMessage {
    const message = createBaseSystemMessage();
    message.text = object.text ?? "";
    return message;
  },
};

function createBaseUserMessage(): UserMessage {
  return { text: undefined, imageUrl: undefined };
}

export const UserMessage: MessageFns<UserMessage> = {
  encode(message: UserMessage, writer: BinaryWriter = new BinaryWriter()): BinaryWriter {
    if (message.text !== undefined) {
      writer.uint32(10).string(message.text);
    }
    if (message.imageUrl !== undefined) {
      writer.uint32(18).string(message.imageUrl);
    }
    return writer;
  },

  decode(input: BinaryReader | Uint8Array, length?: number): UserMessage {
    const reader = input instanceof BinaryReader ? input : new BinaryReader(input);
    const end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseUserMessage();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1: {
          if (tag !== 10) {
            break;
          }

          message.text = reader.string();
          continue;
        }
        case 2: {
          if (tag !== 18) {
            break;
          }

          message.imageUrl = reader.string();
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

  fromJSON(object: any): UserMessage {
    return {
      text: isSet(object.text) ? gt.String(object.text) : undefined,
      imageUrl: isSet(object.imageUrl) ? gt.String(object.imageUrl) : undefined,
    };
  },

  toJSON(message: UserMessage): unknown {
    const obj: any = {};
    if (message.text !== undefined) {
      obj.text = message.text;
    }
    if (message.imageUrl !== undefined) {
      obj.imageUrl = message.imageUrl;
    }
    return obj;
  },

  create(base?: DeepPartial<UserMessage>): UserMessage {
    return UserMessage.fromPartial(base ?? {});
  },
  fromPartial(object: DeepPartial<UserMessage>): UserMessage {
    const message = createBaseUserMessage();
    message.text = object.text ?? undefined;
    message.imageUrl = object.imageUrl ?? undefined;
    return message;
  },
};

function createBasePromptTemplate(): PromptTemplate {
  return { system: undefined, user: undefined, config: undefined };
}

export const PromptTemplate: MessageFns<PromptTemplate> = {
  encode(message: PromptTemplate, writer: BinaryWriter = new BinaryWriter()): BinaryWriter {
    if (message.system !== undefined) {
      SystemMessage.encode(message.system, writer.uint32(10).fork()).join();
    }
    if (message.user !== undefined) {
      UserMessage.encode(message.user, writer.uint32(18).fork()).join();
    }
    if (message.config !== undefined) {
      PromptConfig.encode(message.config, writer.uint32(26).fork()).join();
    }
    return writer;
  },

  decode(input: BinaryReader | Uint8Array, length?: number): PromptTemplate {
    const reader = input instanceof BinaryReader ? input : new BinaryReader(input);
    const end = length === undefined ? reader.len : reader.pos + length;
    const message = createBasePromptTemplate();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1: {
          if (tag !== 10) {
            break;
          }

          message.system = SystemMessage.decode(reader, reader.uint32());
          continue;
        }
        case 2: {
          if (tag !== 18) {
            break;
          }

          message.user = UserMessage.decode(reader, reader.uint32());
          continue;
        }
        case 3: {
          if (tag !== 26) {
            break;
          }

          message.config = PromptConfig.decode(reader, reader.uint32());
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

  fromJSON(object: any): PromptTemplate {
    return {
      system: isSet(object.system) ? SystemMessage.fromJSON(object.system) : undefined,
      user: isSet(object.user) ? UserMessage.fromJSON(object.user) : undefined,
      config: isSet(object.config) ? PromptConfig.fromJSON(object.config) : undefined,
    };
  },

  toJSON(message: PromptTemplate): unknown {
    const obj: any = {};
    if (message.system !== undefined) {
      obj.system = SystemMessage.toJSON(message.system);
    }
    if (message.user !== undefined) {
      obj.user = UserMessage.toJSON(message.user);
    }
    if (message.config !== undefined) {
      obj.config = PromptConfig.toJSON(message.config);
    }
    return obj;
  },

  create(base?: DeepPartial<PromptTemplate>): PromptTemplate {
    return PromptTemplate.fromPartial(base ?? {});
  },
  fromPartial(object: DeepPartial<PromptTemplate>): PromptTemplate {
    const message = createBasePromptTemplate();
    message.system = (object.system !== undefined && object.system !== null)
      ? SystemMessage.fromPartial(object.system)
      : undefined;
    message.user = (object.user !== undefined && object.user !== null)
      ? UserMessage.fromPartial(object.user)
      : undefined;
    message.config = (object.config !== undefined && object.config !== null)
      ? PromptConfig.fromPartial(object.config)
      : undefined;
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
