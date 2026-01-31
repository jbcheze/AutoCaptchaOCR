# CaptchaVision  
**Automated CAPTCHA Recognition & Web Scraping Framework**  
*Computer Vision • OCR • FastAPI • Selenium*

---

## Project Objective

This project aims to design a **robust automated system capable of solving visual CAPTCHA challenges** in real-world scraping scenarios.

The system combines:

1. Automated web scraping
2. Deep learning OCR for CAPTCHA recognition
3. API orchestration for scalable deployment
4. End-to-end pipeline integration

The system was trained and evaluated on visual CAPTCHA datasets and tested in real scraping conditions.

Target scraping environment used for training & testing:

https://rutracker.org/forum/profile.php?mode=register

---

## System Architecture

The framework is composed of independent but interoperable modules:

### Web Scraping Layer (Selenium)

- Automated navigation of CAPTCHA-protected websites
- CAPTCHA detection & extraction
- Retry logic and headless execution
- Robust waiting strategies

### OCR Engine

- Custom deep learning model trained from scratch
- Character-level sequence recognition
- CNN + sequence decoding architecture
- Optimized for distorted CAPTCHA text
- Supports letters and digits

### API Orchestration (FastAPI)

- REST interface to control scraping + OCR
- Prediction endpoints
- Health monitoring
- Designed for production-like usage

### Frontend (Streamlit)

- Lightweight UI for demo & testing
- Image upload + CAPTCHA solving
- API integration

---

## 📁 Project Structure

```text
CaptchaVision/
│
├── app/                    # Streamlit frontend
│   └── main.py
│
├── api/                    # FastAPI backend
│   ├── main.py
│   ├── routes/
│   └── services/
│
├── ocr/                    # OCR engine
│   ├── models/
│   ├── preprocessing/
│   ├── decoding/
│   ├── inference/
│   └── vocab/
│
├── scraper/
├── webscraping/
│
├── models/                 # trained weights
│   └── ANASTASIIA_JB_THEO_9B2_PLUS_SITE.keras
│
├── notebooks/              # experiments & training
├── data/                   # datasets (not included)
├── tests/
│
├── README.md
└── requirements.txt
```

---

## Installation

```bash
git clone https://github.com/<user>/CaptchaVision.git
cd CaptchaVision
pip install -r requirements.txt
```

---

## Running the System

### Start API

```bash
uvicorn api.main:app --reload
```

### Start Streamlit UI

```bash
streamlit run app/main.py
```

---

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
```

---

## OCR Model Performance

Two OCR approaches were benchmarked:

| Model | Character Error Rate (CER) | Exact Match Accuracy | Time / image |
|------|----------------------------|---------------------|-------------|
| **OCR From Scratch (Fine-Tuned)** | **0.12** | **67%** | **1.45 sec** |
| TR-OCR Fine-Tune | 0.26 | 39% | 0.59 sec |

---

### Interpretation

- The custom OCR model significantly outperforms the fine-tuned TR-OCR baseline
- Lower CER indicates more accurate character prediction
- Higher exact match rate confirms better sequence reconstruction
- Trade-off: higher inference time for improved accuracy
- Custom model is better suited for CAPTCHA distortion patterns

---

## Research Highlights

- CAPTCHA-specific OCR architecture
- Sequence decoding with CTC
- Robust preprocessing pipeline
- Real-world scraping validation
- API industrialization
- Modular ML system design

---

## Collaborators

- Anastasiia Sevolka
- Jean-Baptiste Cheze
- Théo Linale