import time
from pathlib import Path
import shutil
from src.webscraping.captcha_solver import CaptchaSolver
from api.app.services.ocr_service import OCRService
from ocr.easyocr_predictor import EasyOCRPredictor

# ============================================================
# Racine du projet
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

# ============================================================
# Registre des modèles OCR (SOURCE UNIQUE DE VÉRITÉ)
# ============================================================

MODEL_REGISTRY = {
    "a_jb_t": {
        "type": "ctc",
        "label": "Anastasiia JB Théo Model",
        "path": str(BASE_DIR / "models" / "ANASTASIIA_JB_THEO_9B2_PLUS_SITE_INFER.keras"),
        "description": "Modèle robuste entraîné sur ensemble de captchas équilibré",
        "default": True,
    },
    "robust": {
        "type": "ctc",
        "label": "Robust Model",
        "path": str(BASE_DIR / "models" / "ocr_ctc_robust_best.keras"),
        "description": "Modèle robuste entraîné sur captchas variés",
        "default": False,
    },
    "light": {
        "type": "ctc",
        "label": "Light Model",
        "path": str(BASE_DIR / "models" / "ocr_ctc_finetuned.keras"),
        "description": "Modèle plus rapide mais moins robuste",
        "default": False,
    },
    "easyocr": {
        "type": "easyocr",
        "label": "EasyOCR",
        "path": None,
        "description": "OCR générique basé sur EasyOCR (baseline externe)",
        "default": False,
    },
}

# ============================================================
# Factory OCR (POINT D’ENTRÉE UNIQUE OCR)
# ============================================================

def get_ocr_predictor(model_key: str):
    cfg = MODEL_REGISTRY.get(model_key)

    if not cfg:
        return None

    if cfg["type"] == "ctc":
        return OCRService(model_path=cfg["path"])

    if cfg["type"] == "easyocr":
        return EasyOCRPredictor()

    return None


# ============================================================
# API principale : résolution + soumission du captcha
# ============================================================

def solve_and_submit_captcha(url: str, model: str) -> dict:
    start = time.time()
    solver = CaptchaSolver()
    captcha_path = None

    try:
        # Charger la page
        solver.driver.get(url)
        solver.wait.until(lambda d: d.find_element("tag name", "body"))

        # Détecter le CAPTCHA
        if not solver.extract_captcha():
            return {
                "status": "error",
                "reason": "captcha_not_found",
                "duration_sec": round(time.time() - start, 2),
            }

        # Sauvegarder l’image
        captcha_path = solver.save_captcha_image()
        if not captcha_path:
            return {
                "status": "error",
                "reason": "captcha_save_failed",
                "duration_sec": round(time.time() - start, 2),
            }

        # Sélection du modèle OCR
        model_key = (model or "").strip().lower()
        cfg = MODEL_REGISTRY.get(model_key)

        if not cfg:
            return {
                "status": "error",
                "reason": "unknown_model",
                "duration_sec": round(time.time() - start, 2),
            }

        # OCR
        predictor = get_ocr_predictor(model_key)
        if predictor is None:
            return {
                "status": "error",
                "reason": "ocr_initialization_failed",
                "duration_sec": round(time.time() - start, 2),
            }
        shutil.copy(captcha_path, "/tmp/api_raw.png")
        prediction = predictor.predict(captcha_path)

        # Soumission du CAPTCHA
        result = solver.solve_captcha_complete(
            url=url,
            solution=prediction,
        )

        success = result.get("success")

        if success is True:
            status = "success"
            reason = "accepted_by_site"
        elif success is False:
            status = "rejected"
            reason = "captcha_incorrect"
        else:
            status = "uncertain"
            reason = "no_confirmation_from_site"

        return {
            "url": url,
            "model": model_key,
            "model_label": cfg["label"],
            "captcha_path": captcha_path,
            "prediction": prediction,
            "status": status,
            "reason": reason,
            "success": success,
            "duration_sec": round(time.time() - start, 2),
        }

    except Exception as e:
        return {
            "status": "error",
            "reason": str(e),
            "duration_sec": round(time.time() - start, 2),
        }

    finally:
        solver.close()


# ============================================================
# Infos modèles (pour l’API / UI)
# ============================================================

def get_model_info():
    return {
        "models": [
            {
                "key": key,
                "label": cfg["label"],
                "description": cfg["description"],
                "default": cfg["default"],
                "type": cfg["type"],
            }
            for key, cfg in MODEL_REGISTRY.items()
        ]
    }