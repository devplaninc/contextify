import {GetObjectCommand, S3Client} from "@aws-sdk/client-s3"
import {ObservationKey} from "../pb/dev_observer/api/types/observations";

export interface S3ObservationsFetcherProps {
  bucket: string
  region: string
  endpoint: string
  accessKeyId?: string
  secretAccessKey?: string
}

export interface FetchResult {
  content: string;
  metadata?: Record<string, string> | undefined;
  contentType?: string | undefined;
  etag?: string | undefined;
}

export class S3ObservationsFetcher {
  private readonly s3: S3Client
  private readonly bucket: string

  constructor(props: S3ObservationsFetcherProps) {
    const {accessKeyId, secretAccessKey, endpoint, region, bucket} = props
    this.bucket = bucket
    if (!accessKeyId || !secretAccessKey) {
      this.s3 = new S3Client({endpoint, region})
    } else {
      this.s3 = new S3Client({
        endpoint,
        region,
        credentials: {accessKeyId, secretAccessKey},
      })
    }
  }

  public async fetch(key: ObservationKey): Promise<FetchResult | undefined> {
    try {
      const response = await this.s3.send(
        new GetObjectCommand({Bucket: this.bucket, Key: key.key})
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
        if (error.name === 'NoSuchKey') {
          return undefined
        } else if (error.name === 'NoSuchBucket') {
          return undefined
        }
      }
      throw new Error(`Failed to fetch S3 object ${key.key}: ${error}`);
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
