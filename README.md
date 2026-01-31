#  Automated CAPTCHA Solver  
**Web Scraping • Computer Vision • FastAPI**


## Project Objective

The goal of this project is to design a **robust web scraping system capable of bypassing visual CAPTCHAs**, relying on three main components:

1. **Web scraping using Selenium**
2. **Deep learning model for CAPTCHA recognition (letters & digits)**
3. **REST API to orchestrate and industrialize the full pipeline using FastAPI**



## Project Architecture

The system is composed of three independent but connected modules:

### Web Scraping (Selenium)
- Automated navigation on websites protected by visual CAPTCHAs
- Detection and extraction of CAPTCHA images
- Robust browser configuration (headless mode, waits, retries)

### CAPTCHA Recognition Model
- Supervised deep learning model (CNN / BILSTM)
- Recognition of **letters and digits** (not reCAPTCHA)
- Image preprocessing and evaluation metrics
- Trained on open-source CAPTCHA datasets

### API Orchestration (FastAPI)
- Centralized control of scraping and prediction
- REST endpoints for:
  - triggering scraping
  - solving CAPTCHAs
  - monitoring system health
- Designed for scalability and production-like deployment


## 📁 Project Structure

```text
Captchas-Automatic-Resolution/
│
├── README.md
├── requirements.txt
│
├── api/
│   ├── main.py
│   ├── routes/
│   └── services/
│
├── scraper/
│   ├── scrape_captcha.py
│   └── utils.py
│
├── captcha_model/
│   ├── model.py
│   ├── preprocess.py
│   ├── decoder.py
│   ├── predictor.py
│   ├── ctc_layer.py
│   └── vocab.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
│
├── models/
│   └── *.keras
│
├── notebooks/
│   └── *.ipynb
│
├── reports/
│   └── projet_mosef.pdf
│
├── scripts/
│   └── demo.py
│
├── tests/
│   └── test_ocr.py
│
└── deepseek_ocr/          # submodule (optionnel)
```



## Installation

This project uses **Poetry** for dependency management.

```bash
git clone https://github.com/aasavel/Captchas-Automatic-Resolution.git
cd captcha-solver-project
poetry install
poetry shell

```

## Running the API

```bash
uvicorn api.app.main:app --reload

```
                /\_/\ 
               ( o.o )
                > ^ <
             __/|___|\__
            /  /     \  \
           /__/       \__\
           \  \  ___  /  /
            \__\/___\/__/
               /  |  \
              /___|___\
               (__) (__)

## OCR Model Performance

The OCR model was evaluated on independent **validation** and **test** datasets using standard character-level and sequence-level metrics.

### Validation Set

- **Character Error Rate (CER)**: 0.0211  
- **Character Accuracy**: 97.89%  
- **Exact Match Accuracy**: 90.27%  
- **Number of samples**: 12,248  

### Test Set

- **Character Error Rate (CER)**: 0.0201  
- **Character Accuracy**: 97.99%  
- **Exact Match Accuracy**: 90.76%  
- **Number of samples**: 12,250  

### Interpretation

- The low CER (≈2%) indicates strong character-level recognition performance.  
- Character accuracy close to 98% demonstrates robust generalization on unseen CAPTCHA images.  
- Exact Match Accuracy above 90% confirms the model’s ability to correctly solve entire CAPTCHA sequences, which is critical for real-world scraping scenarios.  
- The consistency between validation and test results suggests limited overfitting and stable model behavior.




**Collaborateurs :**

- Anastasiia Sevolka
- Jean-Baptiste CHEZE
- Théo Linale
