
## Storage Architecture

### Multi-Cloud Storage Flexibility

**Design Philosophy**: True cloud-agnostic architecture using Abstract Factory pattern with native SDKs for each provider. No vendor lock-in, seamless provider switching via configuration.

**Benefits**:

- **Native SDK performance**: Use optimal client library for each cloud (boto3 for AWS, azure-storage-blob for Azure)
- **Vendor flexibility**: Switch providers via environment variable without code changes
- **Local development**: MinIO runs in Docker with full S3-compatible feature parity
- **Cost optimization**: Choose optimal storage per region/workload/compliance requirement
- **Disaster recovery**: Multi-cloud replication and failover strategies
- **Future-proof**: Easily add new providers (GCS, Cloudflare R2, Backblaze B2) via plugin pattern

### Architecture Pattern: Abstract Factory

**Implementation**: `app/services/storage/` module

The storage system uses SOLID principles with Abstract Base Class + Factory pattern:

#### **Abstract Interface** (`base.py`)

- `ObjectStorageProvider` ABC defining 7 core operations
- `StorageConfig` dataclass for provider-specific configuration
- Fully async interface for non-blocking I/O

**Core Methods**:

- `initialize()`: Setup provider client and ensure bucket/container exists
- `upload(key, data, content_type)`: Upload file with metadata
- `download(key)`: Download file by storage key
- `delete(key)`: Remove file from storage
- `exists(key)`: Check file existence
- `get_presigned_url(key, expiration)`: Generate temporary signed URL
- `list_objects(prefix)`: List objects with optional prefix filter

#### **Provider Implementations**

**AWSStorage** (`aws_storage.py`):

- Uses native boto3 S3 client
- S3-specific features: Intelligent-Tiering, Glacier transitions
- Returns CloudFront CDN URLs when configured
- Auto-creates buckets with region-specific configuration

**AzureStorage** (`azure_storage.py`):

- Uses native async `azure-storage-blob` SDK
- Azure Blob-specific features: Hot/Cool/Archive tiers, SAS tokens
- Returns Azure CDN URLs when configured
- Supports both connection string and account key authentication

**MinIOStorage** (`minio_storage.py`):

- Uses boto3 S3-compatible API (MinIO implements S3 protocol)
- Full feature parity with AWS S3 for local development
- Ideal for on-premise deployments and air-gapped environments
- Auto-creates buckets on initialization

#### **Factory Pattern** (`factory.py`)

```python
# Configuration-driven provider selection
config = StorageConfig(
    provider='minio',  # 'aws', 'azure', 'minio'
    bucket='folium-dev',
    region='us-east-1',
    endpoint_url='http://minio:9000',  # Required for MinIO/Azure
    access_key='minioadmin',
    secret_key='minioadmin'
)

storage = StorageProviderFactory.create(config)
await storage.initialize()
```

**Singleton Pattern**: `get_storage()` function provides app-wide singleton instance based on environment configuration.

**Extensibility**: Register custom providers:

```python
StorageProviderFactory.register_provider('gcs', GoogleCloudStorage)
StorageProviderFactory.register_provider('r2', CloudflareR2Storage)
```

### Environment Configurations

**Configuration Reference**: See `.env.example` for complete configuration templates.

**Provider Selection**: Set `STORAGE_PROVIDER` environment variable to `aws`, `azure`, or `minio`.

**Local Development (MinIO)**:

```env
STORAGE_PROVIDER=minio
STORAGE_ENDPOINT=http://minio:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin
STORAGE_BUCKET=folium-dev
STORAGE_REGION=us-east-1
```

**AWS Production (S3 + CloudFront)**:

```env
STORAGE_PROVIDER=aws
STORAGE_ENDPOINT=  # Leave empty (uses default AWS endpoints)
STORAGE_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
STORAGE_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
STORAGE_BUCKET=folium-prod-us-east-1
STORAGE_REGION=us-east-1
STORAGE_CDN_URL=https://d111111abcdef8.cloudfront.net
```

**Azure Production (Blob Storage + CDN)**:

```env
STORAGE_PROVIDER=azure
STORAGE_ENDPOINT=https://folium.blob.core.windows.net
AZURE_STORAGE_ACCOUNT_NAME=folium
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
STORAGE_BUCKET=documents
STORAGE_REGION=eastus
STORAGE_CDN_URL=https://folium.azureedge.net
```

**On-Premise Enterprise (MinIO Cluster)**:

```env
STORAGE_PROVIDER=minio
STORAGE_ENDPOINT=https://minio.company.internal
STORAGE_ACCESS_KEY=<enterprise_access_key>
STORAGE_SECRET_KEY=<enterprise_secret_key>
STORAGE_BUCKET=emr-documents
STORAGE_REGION=us-east-1
```

### Multi-Cloud Storage Patterns

**1. Hybrid Storage (Hot/Warm/Cold Tiers)**:

- Hot data (recent documents): AWS S3 Standard or Azure Hot Blob
- Warm data (6-12 months): S3 Infrequent Access or Azure Cool Blob
- Cold data (archives): S3 Glacier or Azure Archive Blob
- Lifecycle policies automate tiering

**2. Geographic Distribution**:

- US patients: S3 us-east-1 or Azure East US
- EU patients: S3 eu-west-1 or Azure West Europe (GDPR compliance)
- APAC patients: S3 ap-southeast-1 or Azure Southeast Asia
- Single codebase handles all regions via `STORAGE_REGION` config

**3. Disaster Recovery**:

- Primary: AWS S3 with cross-region replication (us-east-1 → us-west-2)
- Secondary: Azure Blob Storage as failover (different cloud = true DR)
- Tertiary: MinIO on-premise for critical subset of data
- Application detects primary failure, switches endpoint automatically

**4. Cost Optimization**:

- Image files: Compress with WebP/AVIF before upload
- Large PDFs: Multi-part upload with compression
- S3 Intelligent-Tiering: Auto-moves data based on access patterns
- Azure lifecycle management: Automate hot→cool→archive transitions

**5. Performance Optimization**:

- CDN integration: CloudFront (AWS) or Azure CDN for global distribution
- Multi-part uploads: Parallel chunks for files >100MB (medical images)
- Presigned URLs: Direct browser→storage (bypass backend bottleneck)
- Transfer acceleration: S3 Transfer Acceleration for slow networks

**6. Security & Compliance**:

- Encryption at rest: AES-256 (all three support it)
- Encryption in transit: HTTPS/TLS 1.3
- Access logging: S3 Access Logs or Azure Storage Analytics
- HIPAA compliance: AWS BAA or Azure Healthcare API compliance

### Additional Storage Features

**Smart File Classification**:
Route files to optimal storage paths based on file extension:

- Medical imaging (`.dcm`, `.nii`) → `imaging/{uuid}/` prefix
- Documents (`.pdf`) → `documents/{uuid}/` prefix
- Audio (`.wav`, `.mp3`, `.webm`) → `audio/{uuid}/` prefix
- Other uploads → `uploads/{uuid}/` prefix

**Deduplication Strategy**:
Use SHA-256 hash checking to avoid duplicate uploads:

1. Calculate file hash
2. Check if hash-based key exists using `head_object()`
3. Skip upload if file already stored
4. Upload only new files

**DICOM Storage for Medical Imaging**:

- Specialized storage class for DICOM files with metadata extraction
- Tag extraction: Patient ID, Study Date, Modality, Body Part
- Integration with PACS (Picture Archiving and Communication System)
- MinIO works great for self-hosted PACS replacement

**Streaming & Progressive Loading**:

- Range requests for large files (skip to timestamp in audio)
- Progressive JPEG/WebP for faster image loading
- Chunked uploads for real-time recording (audio streaming)

**Version Control**:

- S3 versioning enabled for document history
- Track who uploaded which version (audit trail)
- Restore previous versions (regulatory compliance)

**Search & Indexing**:

- Index metadata in Elasticsearch or Azure Cognitive Search
- Full-text search across PDFs using OCR
- Tag-based search for medical images

### Storage Migration Toolkit

**Purpose**: Migrate data between AWS S3, Azure Blob, and MinIO using provider-agnostic interface.

**Implementation Strategy**:

1. **Source and Destination Providers**: Instantiate two provider instances with different configs
2. **List and Transfer**: Use `list_objects(prefix)` to enumerate, `download()` from source, `upload()` to destination
3. **Metadata Preservation**: Transfer content type and custom metadata during migration
4. **Progress Tracking**: Log each object transfer with size and timing metrics

**Migration Example**:

```python
# AWS → Azure migration
source = StorageProviderFactory.create(StorageConfig(
    provider='aws',
    bucket='source-bucket',
    ...
))

dest = StorageProviderFactory.create(StorageConfig(
    provider='azure',
    bucket='dest-container',
    ...
))

await source.initialize()
await dest.initialize()

for key in await source.list_objects():
    data = await source.download(key)
    await dest.upload(key, data, content_type='application/octet-stream')
```

**Migration Scenarios**:

1. **AWS → Azure**: Switch cloud providers for cost/compliance requirements
2. **Cloud → MinIO**: Migrate to on-premise for data sovereignty regulations
3. **MinIO → AWS/Azure**: Scale from self-hosted to managed cloud storage
4. **Multi-cloud Replication**: Sync primary storage to secondary cloud for disaster recovery
5. **Cross-Region**: Move data between regions within same provider (e.g., US → EU for GDPR)

**Implementation Phases**:

- **Phase 1 (MVP)**: MinIO in docker-compose for local development
- **Phase 2 (Production)**: AWS S3 or Azure Blob with CDN integration
- **Phase 3 (Enterprise)**: Active-active multi-cloud replication with automatic failover

### SOLID Principles Compliance

**Single Responsibility**: Each provider class handles only one cloud's API  
**Open/Closed**: Add new providers without modifying existing code  
**Liskov Substitution**: All providers interchangeable through common interface  
**Interface Segregation**: Minimal 7-method interface, no bloat  
**Dependency Inversion**: Application depends on `ObjectStorageProvider` abstraction, not concrete implementations

### Adding New Providers

To add Google Cloud Storage, Cloudflare R2, or other S3-compatible services:

1. **Create Provider Class** (`gcs_storage.py`):

```python
from .base import ObjectStorageProvider

class GCSStorage(ObjectStorageProvider):
    async def initialize(self): ...
    async def upload(self, key, data, content_type): ...
    # Implement remaining methods
```

2. **Register Provider**:

```python
from app.services.storage import StorageProviderFactory
from .gcs_storage import GCSStorage

StorageProviderFactory.register_provider('gcs', GCSStorage)
```

3. **Configure**:

```env
STORAGE_PROVIDER=gcs
STORAGE_BUCKET=my-gcs-bucket
```

No changes to calling code required - factory handles instantiation.
