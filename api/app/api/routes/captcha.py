from fastapi import APIRouter, Query
from pydantic import HttpUrl

from api.app.services.captcha_solver_service import solve_and_submit_captcha
from api.app.services.captcha_solver_service import get_model_info
from api.app.schemas.captcha import OCRModel

router = APIRouter(prefix="/captcha", tags=["captcha"])


@router.get("/model-info")
def model_info():
    return get_model_info()


@router.post("/solve-and-submit")
def solve(
    url: HttpUrl,
    model: OCRModel = Query(default=OCRModel.a_jb_t)
):

    return solve_and_submit_captcha(
        url=str(url),
        model=model.value
    )