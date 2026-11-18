from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from backend.cycle_tracker import router as cycle_tracker_router

# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "cycle_length_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.joblib"


# --------------------------------------------------
# LOAD TRAINED MODEL
# --------------------------------------------------

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

if not METADATA_PATH.exists():
    raise FileNotFoundError(f"Metadata not found: {METADATA_PATH}")

model = joblib.load(MODEL_PATH)
metadata = joblib.load(METADATA_PATH)

FEATURE_COLUMNS = metadata["feature_columns"]
TARGET_CLASSES = metadata["target_classes"]


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="CycleSense API",
    description="PCOS cycle-length classification API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(cycle_tracker_router)

# --------------------------------------------------
# REQUEST SCHEMA
# --------------------------------------------------

class CycleAssessment(BaseModel):
    # This endpoint accepts the model's actual feature
    # names. Optional values are allowed for features
    # not yet collected by the frontend.

    features: dict[str, object] = Field(
        ...,
        description="Feature names and values expected by the model",
    )


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "CycleSense API is running",
        "model_loaded": True,
        "target": metadata["target_column"],
        "available_categories": TARGET_CLASSES,
    }


# --------------------------------------------------
# MODEL INFORMATION
# --------------------------------------------------

@app.get("/api/model-info")
def model_info():
    return {
        "target": metadata["target_column"],
        "feature_columns": FEATURE_COLUMNS,
        "available_categories": TARGET_CLASSES,
        "training_records": metadata["training_records"],
    }


# --------------------------------------------------
# PREDICTION ENDPOINT
# --------------------------------------------------

@app.post("/api/predict")
def predict_cycle(assessment: CycleAssessment):
    supplied_features = assessment.features

    # Reject unexpected feature names.
    unexpected = set(supplied_features) - set(FEATURE_COLUMNS)

    if unexpected:
        return {
            "error": "Unexpected feature names",
            "unexpected_features": sorted(unexpected),
        }

    # Build a single-row dataframe with the same feature
    # names and order used during training.
    row = {
        feature: supplied_features.get(feature, None)
        for feature in FEATURE_COLUMNS
    }

    input_df = pd.DataFrame([row], columns=FEATURE_COLUMNS)

    # Run the saved preprocessing and classifier pipeline.
    prediction = int(model.predict(input_df)[0])

    classifier = model.named_steps["classifier"]

    probabilities = model.predict_proba(input_df)[0]

    predicted_category = TARGET_CLASSES[prediction]

    probability_by_class = {
        TARGET_CLASSES[int(class_id)]: round(float(probability), 4)
        for class_id, probability in zip(
            classifier.classes_,
            probabilities,
        )
    }

    return {
        "predicted_cycle_category": predicted_category,
        "class_probabilities": probability_by_class,
        "model_type": "Tuned Random Forest",
        "disclaimer": (
            "This is an experimental machine-learning estimate "
            "of the reported cycle-length category, not a medical "
            "diagnosis or a prediction of the next period date."
        ),
    }