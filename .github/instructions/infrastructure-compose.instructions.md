---
applyTo: "{**/*.tf,**/{docker-compose*,compose*}.{yml,yaml}}"
description: "Use when editing Terraform or Docker Compose configuration in Folium."
---

- Deploy locally with Docker Compose, use GitHub Actions for CI/CD, Terraform for infrastructure as code, and support the project's Azure and AWS targets.
- Use TF modules to organize and reuse Terraform code effectively.
- Keep Docker Compose files minimal and environment-specific; avoid hardcoding secrets, use `.env` files instead.