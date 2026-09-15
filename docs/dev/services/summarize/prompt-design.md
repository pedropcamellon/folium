# Prompt design

The clinical-note summarizer targets a SOAP layout so a reviewable output has a
consistent structure across workflows. Prompts direct the service to preserve
clinical terms, doses, dates, and measurements supplied in the source input.

They also set an intentionally concise output shape and instruct the provider
to stay grounded in the supplied transcript. Structured results give the
backend a stable validation boundary and help reviewers distinguish source
information from generated draft content.

Prompt design is not a guarantee of clinical accuracy. Changes to prompts,
models, or output structure require evaluation evidence before they are treated
as reliable platform behavior.
