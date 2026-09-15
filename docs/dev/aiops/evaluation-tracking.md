# Evaluation tracking

Folium needs a repeatable way to understand whether a workflow change improves
or regresses behavior before that change is treated as reliable. The evidence
also needs to remain useful for teams running the platform locally.

MLflow is the first evaluation record. Offline runs capture committed cases
along with model, prompt, and dataset context, giving the team a comparable
history instead of a collection of one-off examples.

This introduces a local service and asks for disciplined evaluation work, but
it makes changes easier to compare and review. Cloud-hosted tracking,
unversioned evaluation data, and claims based only on manual examples remain
deferred or rejected.
