# Folium Documentation

Folium is an on-prem-first engineering sandbox for synthetic, reviewable
clinical chart-support workflows. It is not a complete EHR or a generic
document-processing SaaS.

This documentation has two lanes:

- **[User guide](user-guide/index.md)**: supported, task-focused workflows for
  synthetic patients, interactions, voice-note processing, and clinician-reviewed
  chart-review drafts.
- **[Developer guide](dev/index.md)**: local runtime, service contracts,
  validation, offline evaluation, MLflow evidence, Temporal audit, observability,
  and safe extension practices.

## Implemented agentic lane

```text
synthetic context -> bounded draft agent -> structured validation
  -> offline evaluation -> MLflow evidence -> Temporal audit -> human review
```

The output is draft support only. Folium does not support real patient data,
diagnosis, treatment recommendations, or autonomous action.

## Planned work

Broader retrieval, confidence calibration, dedicated local serving performance,
Azure/AWS providers, and cloud deployment are planned until implementation and
validation evidence exists. They are not supported user workflows.

## Local entry point

From the repository root:

- [AIOps Architecture](dev/aiops-architecture.md) - Shared AIOps ownership
  boundaries and package direction
- [Offline Evaluation](dev/aiops-offline-evaluation.md) - Pre-release staging
  qualification, evidence, gates, and performance baselines
- [Online Evaluation](dev/aiops-online-evaluation.md) - Asynchronous served
  model observation, delayed labels, shadow, and canary policy
- [Chart-Review Evaluation](dev/chart-review-evaluation.md) - Synthetic
  encounter benchmark, workflow protocol, trace, and deterministic rubric
- [Chart-Review Experiments](dev/chart-review-experiments.md) - Immutable
  evaluation setups and durable outcome summaries
- [Chart Review Agent Lessons](dev/chart-review-agent.md) - Local operations and bounded retrieval constraints
- [Local LLM Build Compatibility](dev/local-llm-builds.md) - A Linux ARM build
  lesson and the portable local-summarizer default
- [Clinical Data Model](dev/clinical-data-model.md) - Typed clinical-record
  relationships, migration conventions, and deferred scope
- [Clinical Data Migration](dev/clinical-data-migration.md) - Retired-record
  mapping and synthetic development-data reset procedure

```bash
uv run folium
```

The local runtime documentation covers prerequisites, Compose services, and
synthetic-data safeguards.
