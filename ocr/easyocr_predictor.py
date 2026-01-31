import easyocr


class EasyOCRPredictor:
    def __init__(self, languages=None):
        if languages is None:
            languages = ["en"]

        self.reader = easyocr.Reader(
            languages,
            gpu=False  # True si CUDA
        )

    def predict(self, image_path: str) -> str:
        """
        Retourne le texte OCR détecté par EasyOCR
        """
        results = self.reader.readtext(
            image_path,
            detail=0,
            paragraph=False
        )

        if not results:
            return ""

        # Concaténation simple (captchas courts)
        return "".join(results)
