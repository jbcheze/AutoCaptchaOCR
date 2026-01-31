from ocr.predictor import OCRPredictor

ocr = OCRPredictor(
    model_path="models/ocr_ctc_finetuned.keras"
)

image_path = "./data/all_captcha_png_shuffled/ScipD.png"  

=======
    model_path="models/ocr_ctc_robust_best.keras"
)

# image_path = "./data/all_captcha_png_shuffled/yG92T.png"  
image_path = "./notebook/data/sample/W9H5K.png"
text = ocr.predict(image_path)

print("Prediction OCR :", text)
