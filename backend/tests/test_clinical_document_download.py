from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.api.v1.endpoints.clinical_documents import download_attachment


@pytest.mark.asyncio
async def test_download_attachment_returns_bytes_from_storage() -> None:
    document_id = uuid4()
    attachment_id = uuid4()
    attachment = SimpleNamespace(storage_key="documents/test/image.jpg", mime_type="image/jpeg")
    service = SimpleNamespace(get_attachment=AsyncMock(return_value=attachment))
    storage = SimpleNamespace(download=AsyncMock(return_value=b"image-bytes"))

    response = await download_attachment(
        document_id=document_id,
        attachment_id=attachment_id,
        _=None,
        service=service,
        storage=storage,
    )

    service.get_attachment.assert_awaited_once_with(document_id, attachment_id)
    storage.download.assert_awaited_once_with(attachment.storage_key)
    assert response.body == b"image-bytes"
    assert response.media_type == "image/jpeg"
    assert response.headers["content-disposition"] == "inline"
    assert response.headers["cache-control"] == "private, no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
