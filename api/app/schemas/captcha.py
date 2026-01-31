from enum import Enum
from pydantic import BaseModel, HttpUrl, Field


class OCRModel(str, Enum):
    a_jb_t = "a_jb_t"
    easyocr = "easyocr"
    trocr_custom = "trocr_custom"


class CaptchaRequest(BaseModel):

    url: HttpUrl = Field(
        ...,
        description="URL of the page with captcha",
        examples=["https://example.com"]
    )

    model: OCRModel = Field(
        default=OCRModel.a_jb_t,
        description="OCR model to use"
    )