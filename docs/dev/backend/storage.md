# Storage providers

Folium keeps object storage behind a provider boundary so the application can
use a local object store during on-prem development without coupling workflow
code to a specific cloud SDK.

## Provider selection

A storage factory selects the configured provider and returns the same
application-facing storage contract to its callers. MinIO, Azure Blob Storage,
and Amazon S3 remain isolated implementations behind that contract, so workflow
code does not need to branch on a storage vendor.

Adding a storage option means implementing the storage contract and registering
it with the factory. Existing callers continue to use the same storage boundary;
only the deployment configuration chooses the provider. This keeps future
provider additions contained and avoids spreading vendor SDK dependencies across
the backend.

## Accepting attachments

Folium stores audio and other binary attachments as objects through the storage
provider, then persists the storage key and relevant metadata with the owning
clinical record. This avoids embedding large base64-encoded payloads in
application records, which would increase database size, duplicate transport
work, and make object lifecycle management harder.

The storage key lets a workflow retrieve the object or issue a scoped download
reference without making the binary payload part of every API or workflow
contract. Attachment ownership, deletion, retention, and audit behavior remain
explicit storage concerns.

Clinical-document uploads currently validate the allowed file type and enforce
a 10 MiB request limit before writing the object. The backend currently reads
that request before handing the binary to the storage provider. Direct-to-object
or streaming uploads for larger files are future attachment-storage work: they
must preserve the same ownership, validation, metadata, and audit boundaries.

## Why MinIO is the local default

MinIO gives the local Docker environment an S3-compatible object-storage
service that teams can run inside their own network. It supports local workflow
development without requiring cloud credentials or a hosted storage account.

## Moving to hosted storage

The same storage boundary can later select Azure Blob Storage or Amazon S3.
Moving to a cloud provider changes the operating model, not just the endpoint:
identity and access control, network routes, data residency, lifecycle policy,
provider cost, and observability all need explicit implementation and
validation.

This abstraction adds a small adapter layer, but avoids rewriting callers when
the deployment model changes. It supports data sovereignty by keeping a
customer's attachment data portable between a self-hosted environment and a
chosen cloud provider, rather than binding workflows to one storage vendor.
Cloud storage remains a planned hosted capability; see
[deployment modes](../architecture/deployment-modes.md) for the deployment
context.
