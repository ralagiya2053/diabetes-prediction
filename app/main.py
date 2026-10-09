import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schema import DiabetesInput, PredictionOutput

BASE = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE / "model"

model = joblib.load(MODEL_DIR / "model.pkl")
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
encoder = joblib.load(MODEL_DIR / "encoder.pkl")
feature_order = json.load(open(MODEL_DIR / "feature_order.json"))

NUM_COLS = ["age", "bmi", "HbA1c_level", "blood_glucose_level"]
CAT_COLS = ["gender", "smoking_history"]

app = FastAPI(title="Diabetes Predictor API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionOutput)
def predict(payload: DiabetesInput):
    raw = payload.model_dump()
    df = pd.DataFrame([raw])

    df[NUM_COLS] = scaler.transform(df[NUM_COLS])

    encoded = pd.DataFrame(
        encoder.transform(df[CAT_COLS]),
        columns=encoder.get_feature_names_out(CAT_COLS),
        index=df.index,
    )
    df = df.drop(columns=CAT_COLS).join(encoded)

    df = df[feature_order]

    pred = int(model.predict(df)[0])
    prob = float(model.predict_proba(df)[0][1])

    return {"prediction": pred, "probability": prob}