from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health(request: Request) -> dict[str, str]:
    model_loaded = getattr(request.app.state, "model", None) is not None
    return {"status": "ok", "model": "loaded" if model_loaded else "missing"}
