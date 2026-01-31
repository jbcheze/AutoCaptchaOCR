from fastapi import APIRouter
from pydantic import BaseModel

from api.app.services.captcha_solver_service import solve_and_submit_captcha
from api.app.services.captcha_solver_service import get_model_info

router = APIRouter(prefix="/captcha", tags=["captcha"])


class SolveRequest(BaseModel):
    url: str
    model: str


@router.get("/model-info")
def model_info():
    return get_model_info()


@router.post("/solve-and-submit")
def solve_and_submit(payload: SolveRequest):
    return solve_and_submit_captcha(
        url=payload.url,
        model=payload.model,
    )
