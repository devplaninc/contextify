import {GetObjectCommand, S3Client} from "@aws-sdk/client-s3"
import {Storage} from "@google-cloud/storage"
import {ObservationKey} from "../pb/dev_observer/api/types/observations";

export interface S3Config {
  type: "s3"
  bucket: string
  region: string
  endpoint: string
  accessKeyId: string
  secretAccessKey: string
}

export interface GCSConfig {
  type: "gcs"
  bucket: string
}

export type ObservationsFetcherConfig = S3Config | GCSConfig

export interface FetchResult {
  content: string;
  metadata?: Record<string, string> | undefined;
  contentType?: string | undefined;
  etag?: string | undefined;
}

export class ObservationsFetcher {
  private readonly config: ObservationsFetcherConfig
  private readonly s3?: S3Client
  private readonly gcs?: Storage

  constructor(config: ObservationsFetcherConfig) {
    this.config = config

    if (config.type === "s3") {
      const {accessKeyId, secretAccessKey, endpoint, region} = config
      this.s3 = new S3Client({
        endpoint,
        region,
        credentials: {accessKeyId, secretAccessKey},
      })
    } else {
      this.gcs = new Storage()
    }
  }

  public async fetch(key: ObservationKey): Promise<FetchResult | undefined> {
    if (this.config.type === "s3") {
      return this.fetchFromS3(key)
    } else {
      return this.fetchFromGCS(key)
    }
  }

  private async fetchFromS3(key: ObservationKey): Promise<FetchResult | undefined> {
    if (!this.s3) throw new Error("S3 client not initialized")

    try {
      const response = await this.s3.send(
        new GetObjectCommand({Bucket: this.config.bucket, Key: key.key})
      );

      if (!response.Body) {
        return undefined
      }

      const content: string = await response.Body.transformToString();

      return {
        content,
        metadata: response.Metadata,
        contentType: response.ContentType,
        etag: response.ETag,
      };
    } catch (error) {
      if (isNamedError(error)) {
        if (error.name === 'NoSuchKey' || error.name === 'NoSuchBucket') {
          return undefined
        }
      }
      throw new Error(`Failed to fetch S3 object ${key.key}: ${error}`);
    }
  }

  private async fetchFromGCS(key: ObservationKey): Promise<FetchResult | undefined> {
    if (!this.gcs) throw new Error("GCS client not initialized")

    try {
      const file = this.gcs.bucket(this.config.bucket).file(key.key)
      const [content] = await file.download()
      const [metadata] = await file.getMetadata()

      // Convert GCS metadata to string-only record
      const stringMetadata = metadata.metadata
        ? Object.fromEntries(
          Object.entries(metadata.metadata).map(([k, v]) => [k, String(v)])
        )
        : undefined

      return {
        content: content.toString('utf-8'),
        metadata: stringMetadata,
        contentType: metadata.contentType,
        etag: metadata.etag,
      }
    } catch (error) {
      if (isNamedError(error) && (error as any).code === 404) {
        return undefined
      }
      throw new Error(`Failed to fetch GCS object ${key.key}: ${error}`)
    }
  }
}

function isNamedError(error: unknown): error is { name: string } {
  return (
    typeof error === "object" &&
    error !== null &&
    "name" in error &&
    typeof error.name === "string"
  );
}
