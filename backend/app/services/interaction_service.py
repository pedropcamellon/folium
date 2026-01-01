"""Patient interaction service - Business logic layer"""

from app.models.interaction import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    NoteUpdateRequest,
)
from app.repositories.interaction_repository import InteractionRepository
from app.core.exceptions import InteractionNotFoundError


class InteractionService:
    """Business logic for patient interaction operations"""

    def __init__(self, repository: InteractionRepository):
        self.repository = repository

    async def get_all(self) -> list[InteractionResponse]:
        """Get all interactions"""
        interactions = await self.repository.get_all()
        return [InteractionResponse(**i) for i in interactions]

    async def get_by_id(self, interaction_id: str) -> InteractionResponse:
        """Get interaction by ID"""
        interaction = await self.repository.get_by_id(interaction_id)
        if not interaction:
            raise InteractionNotFoundError(interaction_id)
        return InteractionResponse(**interaction)

    async def get_by_patient_id(self, patient_id: str) -> list[InteractionResponse]:
        """Get all interactions for a specific patient"""
        interactions = await self.repository.get_by_patient_id(patient_id)
        # Sort by interaction date descending (most recent first)
        sorted_interactions = sorted(
            interactions, key=lambda x: x.get("interactionDate", ""), reverse=True
        )
        return [InteractionResponse(**i) for i in sorted_interactions]

    async def create(self, interaction_data: InteractionCreate) -> InteractionResponse:
        """Create new interaction"""
        # Business logic: validate patient exists, check constraints, etc.
        interaction_dict = interaction_data.model_dump()

        # Convert datetime to ISO string for storage
        if interaction_dict.get("interactionDate"):
            interaction_dict["interactionDate"] = interaction_dict["interactionDate"].isoformat()

        # Convert enum to string value
        if interaction_dict.get("type"):
            interaction_dict["type"] = interaction_dict["type"].value

        interaction = await self.repository.create(interaction_dict)
        return InteractionResponse(**interaction)

    async def update(
        self, interaction_id: str, interaction_data: InteractionUpdate
    ) -> InteractionResponse:
        """Update interaction"""
        # Verify interaction exists
        existing = await self.repository.get_by_id(interaction_id)
        if not existing:
            raise InteractionNotFoundError(interaction_id)

        # Get only fields that were provided
        update_dict = interaction_data.model_dump(exclude_unset=True)

        # Convert datetime to ISO string if present
        if update_dict.get("interactionDate"):
            update_dict["interactionDate"] = update_dict["interactionDate"].isoformat()

        # Convert enum to string value if present
        if update_dict.get("type"):
            update_dict["type"] = update_dict["type"].value

        updated = await self.repository.update(interaction_id, update_dict)
        return InteractionResponse(**updated)

    async def update_note(
        self, interaction_id: str, note_data: NoteUpdateRequest
    ) -> InteractionResponse:
        """Update just the note field of an interaction"""
        existing = await self.repository.get_by_id(interaction_id)
        if not existing:
            raise InteractionNotFoundError(interaction_id)

        updated = await self.repository.update(interaction_id, {"note": note_data.note})
        return InteractionResponse(**updated)

    async def delete(self, interaction_id: str) -> bool:
        """Delete interaction"""
        existing = await self.repository.get_by_id(interaction_id)
        if not existing:
            raise InteractionNotFoundError(interaction_id)

        return await self.repository.delete(interaction_id)
