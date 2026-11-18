from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)


RANDOM_STATE = 42

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "datasetpcos.csv"
RESULTS_DIR = ROOT / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "Cycle Length"
PCOS_COLUMN = "PCOS"

EXCLUDED_COLUMNS = [
    "Cycle Length",
    "PCOS",
    "PCOS_from",
    "City",
    "relocated city",
    "irregular or missed periods",
]


def load_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    df.columns = df.columns.str.strip()

    df = df.drop_duplicates().copy()

    for col in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        df[col] = df[col].apply(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

    df[PCOS_COLUMN] = (
        df[PCOS_COLUMN]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    df = df[
        df[PCOS_COLUMN].isin(["yes", "y"])
    ].copy()

    df = df.dropna(subset=[TARGET]).copy()

    # Normalize only clear formatting variants.
    df[TARGET] = df[TARGET].replace({
        "29-35": "29-35 days",
        "36+": "36+ days",
        "25-28": "25-28 days",
    })

    counts = df[TARGET].value_counts()

    # Three-fold stratified CV needs at least three
    # observations in each included category.
    rare_classes = counts[counts < 3].index.tolist()

    if rare_classes:
        print(
            "Excluding classes with fewer than "
            "3 records:",
            rare_classes,
        )

        df = df[
            ~df[TARGET].isin(rare_classes)
        ].copy()

    counts = df[TARGET].value_counts()

    if len(counts) < 2 or counts.min() < 3:
        raise ValueError(
            "Insufficient samples for stratified "
            "cross-validation."
        )

    X = df.drop(
        columns=[
            col
            for col in EXCLUDED_COLUMNS
            if col in df.columns
        ]
    ).copy()

    X = X.reset_index(drop=True)

    y_text = (
        df[TARGET]
        .astype(str)
        .reset_index(drop=True)
    )

    label_encoder = LabelEncoder()

    y = label_encoder.fit_transform(y_text)

    numeric_features = []
    categorical_features = []

    # Detect numeric columns even if pandas imported
    # some of their values as strings.
    for col in X.columns:

        converted = pd.to_numeric(
            X[col],
            errors="coerce",
        )

        observed = X[col].notna().sum()

        fraction = (
            converted.notna().sum() / observed
            if observed
            else 0
        )

        if fraction >= 0.80:

            X[col] = converted

            numeric_features.append(col)

        else:

            X[col] = X[col].astype("object")

            categorical_features.append(col)

    return (
        X,
        y,
        y_text,
        label_encoder,
        numeric_features,
        categorical_features,
    )


def create_preprocessor(
    numeric_features,
    categorical_features,
):

    numeric_pipeline = Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="median"),
        )
    ])

    categorical_pipeline = Pipeline([
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            ),
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False,
            ),
        ),
    ])

    preprocessor = ColumnTransformer([
        (
            "numeric",
            numeric_pipeline,
            numeric_features,
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features,
        ),
    ])

    return preprocessor


def evaluate_model(model_name, classifier):

    (
        X,
        y,
        y_text,
        label_encoder,
        numeric_features,
        categorical_features,
    ) = load_data()

    preprocessor = create_preprocessor(
        numeric_features,
        categorical_features,
    )

    n_splits = min(
        3,
        int(y_text.value_counts().min()),
    )

    cv = StratifiedKFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    splits = list(cv.split(X, y))

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier),
    ])

    # Out-of-fold predictions.
    predictions = cross_val_predict(
        pipeline,
        X,
        y,
        cv=splits,
        method="predict",
        n_jobs=1,
    )

    fold_accuracy = []
    fold_balanced_accuracy = []
    fold_macro_f1 = []

    for train_idx, test_idx in splits:

        fold_pipeline = Pipeline([
            (
                "preprocessor",
                create_preprocessor(
                    numeric_features,
                    categorical_features,
                ),
            ),
            ("classifier", classifier),
        ])

        fold_pipeline.fit(
            X.iloc[train_idx],
            y[train_idx],
        )

        fold_predictions = fold_pipeline.predict(
            X.iloc[test_idx]
        )

        fold_accuracy.append(
            accuracy_score(
                y[test_idx],
                fold_predictions,
            )
        )

        fold_balanced_accuracy.append(
            balanced_accuracy_score(
                y[test_idx],
                fold_predictions,
            )
        )

        fold_macro_f1.append(
            f1_score(
                y[test_idx],
                fold_predictions,
                average="macro",
                zero_division=0,
            )
        )

    result = {
        "Model": model_name,

        "CV Accuracy Mean":
            np.mean(fold_accuracy),

        "CV Accuracy Std":
            np.std(fold_accuracy),

        "CV Balanced Accuracy Mean":
            np.mean(fold_balanced_accuracy),

        "CV Balanced Accuracy Std":
            np.std(fold_balanced_accuracy),

        "CV Macro F1 Mean":
            np.mean(fold_macro_f1),

        "CV Macro F1 Std":
            np.std(fold_macro_f1),

        "OOF Accuracy":
            accuracy_score(y, predictions),

        "OOF Balanced Accuracy":
            balanced_accuracy_score(
                y,
                predictions,
            ),

        "OOF Macro F1":
            f1_score(
                y,
                predictions,
                average="macro",
                zero_division=0,
            ),
    }

    print("\n" + "=" * 65)
    print(model_name)
    print("=" * 65)

    for metric, value in result.items():

        if metric != "Model":
            print(f"{metric}: {value:.3f}")

    print("\nClassification report:")

    print(
        classification_report(
            y,
            predictions,
            labels=np.arange(
                len(label_encoder.classes_)
            ),
            target_names=label_encoder.classes_,
            zero_division=0,
        )
    )

    matrix = confusion_matrix(
        y,
        predictions,
        labels=np.arange(
            len(label_encoder.classes_)
        ),
    )

    safe_name = (
        model_name.lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
    )

    matrix_df = pd.DataFrame(
        matrix,
        index=label_encoder.classes_,
        columns=label_encoder.classes_,
    )

    matrix_df.to_csv(
        RESULTS_DIR
        / f"confusion_matrix_{safe_name}.csv"
    )

    prediction_df = pd.DataFrame({
        "Actual cycle category": y_text,

        "Predicted cycle category":
            label_encoder.inverse_transform(
                predictions
            ),
    })

    prediction_df.to_csv(
        RESULTS_DIR
        / f"predictions_{safe_name}.csv",
        index=False,
    )

    return result