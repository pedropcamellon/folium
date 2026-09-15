# Developer guide

Folium is an on-prem-first engineering sandbox for a bounded, reviewable agentic
lane. Start here before changing runtime behavior or publishing a new claim.

## Implemented lane

```text
synthetic context
  -> bounded draft agent
  -> structured validation
  -> offline evaluation
  -> MLflow evidence
  -> Temporal audit
  -> human review
```

The lane is draft support only. It does not diagnose, recommend treatment, or
take autonomous action.

## Developer topics

- [Local Docker runtime](local-development.md)
- [Bounded chart-review agent](chart-review-agent.md)
- [Validation and offline evaluation](validation-and-evals.md)
- [MLflow evidence and Temporal audit](mlflow-and-temporal.md)
- [Observability](observability.md)
- [Safe extension](safe-extension.md)

The [clinical data model](clinical-data-model.md), [migration guide](clinical-data-migration.md),
and [local LLM build note](local-llm-builds.md) record narrower implementation
contracts and lessons.
