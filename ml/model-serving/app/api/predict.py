from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.predictor import Predictor

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def predict(req: PredictionRequest, request: Request) -> PredictionResponse:
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded; check MODEL_PATH and that the training service has produced a model.",
        )
    model_version = request.app.state.settings.model_version
    predictor = Predictor(model=model, model_version=model_version)
    return predictor.predict(req)
