# Service boundaries

Folium separates services where the work has different operational needs. The
goal is to keep the clinical application understandable and secure while
allowing specialized workloads to evolve, scale, and deploy independently.

## One platform, different concerns

The backend is the policy and data boundary: it controls access, validates
requests and results, and coordinates workflows. The frontend is optimized for
task-focused user experiences and communicates through centralized API
configuration. Keeping those concerns separate makes UI iteration independent
of data and workflow policy.

Transcription and summarization are isolated because their runtime profiles
differ from the backend. They can need model initialization, CPU or accelerator
capacity, longer processing windows, and separate scaling rules. Isolating them
prevents a burst of processing work from competing with interactive clinical
workflows.

## Future capacity choices

The local runtime is the current baseline. If measured workload needs justify
it, a focused processing service can later run with dedicated accelerator-backed
capacity or an independently scaled hosted instance. That change should remain
within the service boundary: the backend and frontend continue to use the same
typed contract, while capacity, runtime, and provider decisions are evaluated
for the owning service.

## Provider encapsulation

Each specialized service exposes a typed contract and keeps provider-specific
configuration behind that contract. The rest of Folium does not depend on a
particular model host, storage implementation, or cloud SDK. This makes a local
runtime the default while preserving a deliberate path to provider-backed
deployments when Azure or AWS hosting is implemented and validated.

Workers receive approved, scoped input rather than unrestricted database access.
That limits the data boundary, makes failures easier to inspect, and keeps
provider replacement from changing application policy.

## Shared foundations

`folium-core` contains stable contracts and pure runtime primitives used by at
least two consumers. It must not become a catch-all layer for business rules,
provider code, or workflow policy. MLflow and Temporal remain shared evidence
and orchestration infrastructure, not ownership layers for product behavior.

For worker-runtime tradeoffs, see [Temporal runtime](../operations/temporal-runtime.md).
For deployment choices, see [deployment modes](deployment-modes.md).
