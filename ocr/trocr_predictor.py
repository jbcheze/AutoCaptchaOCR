import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel, TrOCRProcessor


class TrOCRPredictor:

    def __init__(self, model_path: str):

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.processor = TrOCRProcessor.from_pretrained(model_path)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_path)

        self.model.to(self.device)
        self.model.eval()

    def predict(self, image_path: str) -> str:

        image = Image.open(image_path).convert("RGB")

        pixel_values = self.processor(
            image,
            return_tensors="pt"
        ).pixel_values.to(self.device)

        with torch.no_grad():
            ids = self.model.generate(pixel_values)

        text = self.processor.batch_decode(
            ids,
            skip_special_tokens=True
        )[0]

        return text.strip()