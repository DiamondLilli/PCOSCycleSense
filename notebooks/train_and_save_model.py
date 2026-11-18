from pathlib import Path
import sys
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

# Make the shared utilities available.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "notebooks"))

from common_model_utils import (
    load_data,
    create_preprocessor,
)

# Paths
MODEL_DIR = PROJECT_ROOT / "backend" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "cycle_length_model.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.joblib"


def main():
    print("=" * 60)
    print("TRAINING CYCLESENSE RANDOM FOREST")
    print("=" * 60)

    (
        X,
        y,
        y_text,
        label_encoder,
        numeric_features,
        categorical_features,
    ) = load_data()

    print(f"\nNumber of records: {len(X)}")
    print(f"Number of input features: {X.shape[1]}")
    print(f"Numerical features: {len(numeric_features)}")
    print(f"Categorical features: {len(categorical_features)}")
    print(f"Target categories: {list(label_encoder.classes_)}")

    # Use the same tuned configuration as your existing experiment.
    classifier = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        min_samples_split=6,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced_subsample",
        criterion="gini",
        random_state=42,
        n_jobs=1,
    )

    preprocessor = create_preprocessor(
        numeric_features,
        categorical_features,
    )

    # Save preprocessing and classification as one pipeline.
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier),
    ])

    print("\nFitting the pipeline on the available dataset...")

    pipeline.fit(X, y)

    # Save the entire fitted pipeline.
    joblib.dump(pipeline, MODEL_PATH)

    # Store information needed to prepare API requests.
    metadata = {
        "feature_columns": list(X.columns),
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "target_classes": list(label_encoder.classes_),
        "target_column": "Cycle Length",
        "training_records": len(X),
    }

    joblib.dump(metadata, METADATA_PATH)

    print("\nMODEL SAVED SUCCESSFULLY")
    print(f"Model: {MODEL_PATH}")
    print(f"Metadata: {METADATA_PATH}")

    print("\nExpected input features:")
    for feature in X.columns:
        print(f"  - {feature}")

    print("\nAvailable prediction categories:")
    for category in label_encoder.classes_:
        print(f"  - {category}")

    print("\nIMPORTANT:")
    print(
        "This pipeline was fitted on the available dataset. "
        "Its training fit is not an estimate of generalization "
        "performance. Evaluate it on held-out data before "
        "making performance claims."
    )


if __name__ == "__main__":
    main()