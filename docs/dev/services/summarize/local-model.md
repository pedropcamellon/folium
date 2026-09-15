# Local model artifact

Folium's local runner pins a verified `MediPhi-Clinical.Q4_K_S.gguf` artifact
for the summarization service and the chart-review worker that calls it. The
runner verifies its expected size and SHA-256 checksum before placing it at the
mounted local model path.

A verified artifact makes the local environment reproducible: developers and
evaluation runs use the same model file rather than a changing download. Both
services use the shared `LOCAL_MODEL_NAME` configuration, which defaults to
`mediphi-clinical`. The `Q4_K_S` artifact is approximately 2.04 GiB, making it
a practical local baseline for the current runtime.

This choice is an operational default, not a clinical-performance claim or a
recommendation for every deployment. Changing the model artifact, quantization,
or runtime configuration requires compatible build testing and evaluation
evidence before it becomes the new local default.

### MediPhi-Clinical

**Why MediPhi over other open-source models?**

- **Domain-specific training**: Fine-tuned on 2.5M clinical instructions, PubMed, medical guidelines
- **Better clinical accuracy**: 95%+ on medical NLP benchmarks vs 85-90% for general models
- **Smaller size**: 2.3GB vs 5GB (faster loading, less memory)
- **Larger context**: 128k tokens (handles full patient histories)
- **Superior ICD coding**: Outperforms GPT-4 by 14% on ICD-10 classification
- **MIT licensed**: No restrictions on commercial use

**Clinical Benchmark Results (CLUE+)**:

- Medical NLI: 71.0% accuracy
- RRS QA: 61.6% accuracy
- ICD-10 CM: 54.9% accuracy (vs GPT-4: 40.9%)
- Clinical Information Extraction: 43.5% F1

### Local-First Strategy

**Rationale**:

- HIPAA compliance out-of-box (no BAA required)
- No per-request costs (infrastructure only)
- Data sovereignty (PHI never leaves environment)
- Offline capability (no network dependency)
- Clinical specialization (MediPhi trained on medical data)

**Trade-offs**:

- Slower processing (5-10s vs 2-5s with cloud)
- Limited to CPU inference (GPU support requires CUDA)

**Mitigation**:

- Use quantized models (Q4_K_M) for speed
- MediPhi's clinical training compensates for size difference
- 128k context handles most clinical documents

See [local LLM build compatibility](../../local-llm-builds.md) for the
portable build constraint and [evaluation tracking](../../aiops/evaluation-tracking.md)
for the evidence boundary.
