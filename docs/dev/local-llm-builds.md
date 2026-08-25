# Local LLM Build Compatibility

**Audience:** Folium maintainers and coding agents. This is a developer note,
not a user-facing setup guide.

## What Happened

Raised on 2026-08-25 while building the local summarizer image with Python 3.13
on Linux ARM. `llama-cpp-python` failed during compilation of host-specific
NEON CPU variants. The GGUF model was correctly excluded from the root Compose
build context, so model handling was not the cause.

## What We Changed

The summarizer Dockerfile now sets these CMake options before frozen dependency
installation:

```text
CMAKE_ARGS=-DGGML_NATIVE=OFF -DGGML_CPU_ALL_VARIANTS=OFF
```

This makes GGML portable instead of choosing CPU flags for the build machine.
It is the local-provider default because developers build Folium on different
architectures.

## Tradeoff and Boundaries

- We choose reliable builds over CPU-specific optimization.
- The GGUF model is mounted at runtime under `/models`; it is not copied into
  the image and must remain untracked.
- Do not replace the portable default with native tuning unless every target
  architecture is tested and there is a clear deployment reason.

## For Future Changes

Build the image from the repository root after changing the summarizer runtime
or its dependencies:

```bash
docker compose build folium-summarize
```

If compilation fails, record the full `llama-cpp-python` output, platform, and
Python version. Treat model mounting as a separate problem unless compilation
has already completed.
