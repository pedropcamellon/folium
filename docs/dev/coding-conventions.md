# Coding conventions

Conventions that apply across the backend, independent of any single service.
This list stays minimal: entries are added only after a pattern recurs across
the codebase, not as an exhaustive style guide.

## Coding Style

Never return `None`. Use a bare `return` for early exits instead of
`return None`, and prefer raising, an empty collection, or a sentinel/`Result`
type over a `None` return that callers must remember to check. See
[python.instructions.md](https://github.com/pedropcamellon/folium/blob/main/.github/instructions/python.instructions.md)
for the enforced rule.

## Handling Errors

Prefer `logger.exception(...)` inside an `except` block over
`logger.error(..., exc_info=True)`. `logger.exception` always attaches the
traceback and reads as the intent at the call site.

```python
try:
    process_audio(path)
except AudioProcessingError:
    logger.exception("Audio processing failed for %s", path)
```
