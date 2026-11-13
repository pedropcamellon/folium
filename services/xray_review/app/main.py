"""Self-hosted, research-only chest X-ray classification adapter."""

import hashlib
import io
import os
import secrets
from contextlib import asynccontextmanager

import torch
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from huggingface_hub import hf_hub_download
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel
from safetensors.torch import load_file
from torchvision import models, transforms

MODEL_REPOSITORY = "itsomk/chexpert-densenet121"
MODEL_REVISION = "81be45e4d43011e8f50e17d002190c76cb069edd"
MODEL_FILENAME = "pytorch_model.safetensors"
MODEL_SHA256 = "f6fa96434c2b4822b0e1f6c3ea4f236466788e49749c05fd5c30a83a263450f2"
MODEL_SIZE = 28_298_128
MAX_IMAGE_BYTES = 10 * 1024 * 1024
SERVICE_TOKEN = os.environ.get("XRAY_REVIEW_TOKEN", "")
LABELS = [
    "No Finding",
    "Enlarged Cardiomediastinum",
    "Cardiomegaly",
    "Lung Opacity",
    "Lung Lesion",
    "Edema",
    "Consolidation",
    "Pneumonia",
    "Atelectasis",
    "Pneumothorax",
    "Pleural Effusion",
    "Pleural Other",
    "Fracture",
    "Support Devices",
]
PREPROCESS = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


class Finding(BaseModel):
    label: str
    score: float


class AnalysisResponse(BaseModel):
    findings: list[Finding]
    model_repository: str
    model_revision: str
    review_required: bool = True
    disclaimer: str = (
        "Research-only output. Scores are not calibrated probabilities or a diagnosis. "
        "This classifier does not locate nodules. Provider review is required."
    )


class CheXpertClassifier(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.densenet = models.densenet121(weights=None)
        self.densenet.classifier = torch.nn.Linear(self.densenet.classifier.in_features, len(LABELS))

    def forward(self, image: torch.Tensor) -> torch.Tensor:
        return self.densenet(image)


def load_model() -> CheXpertClassifier:
    model_path = hf_hub_download(
        repo_id=MODEL_REPOSITORY,
        filename=MODEL_FILENAME,
        revision=MODEL_REVISION,
    )
    digest = hashlib.sha256()
    with open(model_path, "rb") as model_file:
        for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != MODEL_SHA256 or os.path.getsize(model_path) != MODEL_SIZE:
        raise RuntimeError("Downloaded chest X-ray model failed integrity verification")

    model = CheXpertClassifier()
    model.load_state_dict(load_file(model_path), strict=True)
    model.eval()
    return model


@asynccontextmanager
async def lifespan(_: FastAPI):
    app.state.model = load_model()
    yield


app = FastAPI(title="Folium X-ray Review Adapter", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ready" if hasattr(app.state, "model") else "loading"}


async def require_service_token(
    token: str | None = Header(None, alias="X-Review-Service-Token"),
) -> None:
    if not SERVICE_TOKEN:
        raise HTTPException(status_code=503, detail="Service authentication is not configured")
    if token is None or not secrets.compare_digest(token, SERVICE_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid service credential")


@app.post("/v1/analyze", response_model=AnalysisResponse)
async def analyze(
    file: UploadFile = File(...),
    _: None = Depends(require_service_token),
) -> AnalysisResponse:
    if file.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(status_code=415, detail="Only JPEG and PNG images are supported")
    image_bytes = await file.read(MAX_IMAGE_BYTES + 1)
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds the 10 MB limit")
    try:
        with Image.open(io.BytesIO(image_bytes)) as decoded:
            if decoded.width * decoded.height > 32_000_000:
                raise HTTPException(status_code=413, detail="Image dimensions exceed the limit")
            image = decoded.convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid image") from exc

    with torch.inference_mode():
        scores = torch.sigmoid(app.state.model(PREPROCESS(image).unsqueeze(0))).squeeze(0)
    return AnalysisResponse(
        findings=[
            Finding(label=label, score=float(score))
            for label, score in zip(LABELS, scores.tolist(), strict=True)
        ],
        model_repository=MODEL_REPOSITORY,
        model_revision=MODEL_REVISION,
    )
