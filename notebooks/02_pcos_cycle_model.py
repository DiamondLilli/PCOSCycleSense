import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    make_scorer,
)
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    cross_val_predict,
    cross_validate,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

warnings.filterwarnings("ignore")


# ============================================================
# 1. CONFIGURATION
# ============================================================

RANDOM_STATE = 42

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "datasetpcos.csv"
RESULTS_DIR = ROOT / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "Cycle Length"
PCOS_COLUMN = "PCOS"

# Exclude features that may reveal information closely related
# to the target.
EXCLUDED_COLUMNS = [
    "PCOS",
    "PCOS_from",
    "City",
    "relocated city",
    "Cycle Length",
    "irregular or missed periods",
]


# ============================================================
# 2. LOAD AND CLEAN DATA
# ============================================================

print("=" * 70)
print("PCOS CYCLESENSE - RANDOM FOREST TUNING")
print("=" * 70)

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

df.columns = df.columns.str.strip()

# Remove exact duplicates.
df = df.drop_duplicates().copy()

# Clean whitespace in textual values.
for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = df[col].apply(
        lambda value: value.strip()
        if isinstance(value, str)
        else value
    )

# Filter participants reporting PCOS.
df[PCOS_COLUMN] = (
    df[PCOS_COLUMN]
    .astype("string")
    .str.strip()
    .str.lower()
)

df = df[df[PCOS_COLUMN].isin(["yes", "y"])].copy()

# Standardize only clear formatting variants.
label_mapping = {
    "29-35": "29-35 days",
    "36+": "36+ days",
    "25-28": "25-28 days",
}

df[TARGET] = df[TARGET].replace(label_mapping)

# Exclude records without target labels.
df = df.dropna(subset=[TARGET]).copy()

print(f"\nPCOS-labelled participants: {len(df)}")

print("\nOriginal target distribution:")
print(df[TARGET].value_counts())


# ============================================================
# 3. PREPARE FEATURES AND TARGET
# ============================================================

class_counts = df[TARGET].value_counts()

# Classes with fewer than two observations cannot support
# stratified cross-validation.
rare_classes = class_counts[class_counts < 2].index.tolist()

if rare_classes:
    print("\nExcluding classes with fewer than two observations:")
    print(rare_classes)

    df = df[~df[TARGET].isin(rare_classes)].copy()

X = df.drop(
    columns=[
        col for col in EXCLUDED_COLUMNS
        if col in df.columns
    ]
).copy()

y_text = df[TARGET].astype(str)

encoder = LabelEncoder()
y = encoder.fit_transform(y_text)

class_counts = y_text.value_counts()

print("\nFinal target distribution:")
print(class_counts)

print(f"\nNumber of features: {X.shape[1]}")
print(f"Number of participants: {len(X)}")
print(f"Number of classes: {len(encoder.classes_)}")

if class_counts.min() < 3:
    raise ValueError(
        "At least three observations per class are required "
        "for this exploratory tuning procedure."
    )


# ============================================================
# 4. IDENTIFY NUMERICAL AND CATEGORICAL FEATURES
# ============================================================

numeric_features = []
categorical_features = []

for col in X.columns:

    converted = pd.to_numeric(X[col], errors="coerce")

    non_missing = X[col].notna().sum()

    if non_missing > 0:
        numeric_fraction = converted.notna().sum() / non_missing
    else:
        numeric_fraction = 0

    if numeric_fraction >= 0.80:
        X[col] = converted
        numeric_features.append(col)
    else:
        X[col] = X[col].astype("object")
        categorical_features.append(col)

print("\nNumeric features:", numeric_features)
print("\nCategorical features:", categorical_features)


# ============================================================
# 5. PREPROCESSING
# ============================================================

numeric_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median"))
    ]
)

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent"),
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False,
            ),
        ),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", numeric_pipeline, numeric_features),
        (
            "categorical",
            categorical_pipeline,
            categorical_features,
        ),
    ],
    remainder="drop",
)


# ============================================================
# 6. RANDOM FOREST PIPELINE
# ============================================================

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            RandomForestClassifier(
                random_state=RANDOM_STATE,
                n_jobs=1,
            ),
        ),
    ]
)


# ============================================================
# 7. HYPERPARAMETER SEARCH
# ============================================================

# We deliberately use a relatively small search space because
# the dataset is small and large searches can overfit.

parameter_grid = {
    "classifier__n_estimators": [200, 500],
    "classifier__max_depth": [None, 3, 5],
    "classifier__min_samples_split": [2, 4, 6],
    "classifier__min_samples_leaf": [2, 3, 5],
    "classifier__max_features": ["sqrt", 0.5],
    "classifier__class_weight": [
        None,
        "balanced",
        "balanced_subsample",
    ],
    "classifier__criterion": ["gini", "entropy"],
}

n_splits = min(3, int(class_counts.min()))

cv = StratifiedKFold(
    n_splits=n_splits,
    shuffle=True,
    random_state=RANDOM_STATE,
)

shared_splits = list(cv.split(X, y))

search = GridSearchCV(
    estimator=pipeline,
    param_grid=parameter_grid,
    scoring="f1_macro",
    cv=shared_splits,
    n_jobs=-1,
    refit=True,
    verbose=1,
    return_train_score=True,
    error_score="raise",
)

print("\nStarting hyperparameter search...")
print("Selection metric: Macro F1")
print(f"Cross-validation folds: {n_splits}")

search.fit(X, y)


# ============================================================
# 8. BEST HYPERPARAMETERS
# ============================================================

print("\n" + "=" * 70)
print("BEST RANDOM FOREST CONFIGURATION")
print("=" * 70)

print("\nBest parameters:")

for parameter, value in search.best_params_.items():
    print(f"{parameter}: {value}")

print(
    f"\nBest cross-validation macro F1: "
    f"{search.best_score_:.3f}"
)

best_model = search.best_estimator_


# ============================================================
# 9. CROSS-VALIDATED EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("CROSS-VALIDATED EVALUATION")
print("=" * 70)

# Evaluate the selected configuration using the same folds.
# These scores are exploratory because those folds also guided
# hyperparameter selection. They are not an independent test.

cv_results = cross_validate(
    best_model,
    X,
    y,
    cv=shared_splits,
    scoring={
        "accuracy": "accuracy",
        "balanced_accuracy": "balanced_accuracy",
        "macro_f1": "f1_macro",
    },
    n_jobs=1,
)

for metric in ["accuracy", "balanced_accuracy", "macro_f1"]:

    values = cv_results[f"test_{metric}"]

    print(
        f"{metric}: {values.mean():.3f} "
        f"+/- {values.std():.3f}"
    )


# ============================================================
# 10. OUT-OF-FOLD PREDICTIONS
# ============================================================

predictions = cross_val_predict(
    best_model,
    X,
    y,
    cv=shared_splits,
    n_jobs=1,
)

print("\nOut-of-fold accuracy:", round(
    accuracy_score(y, predictions), 3
))

print("Out-of-fold balanced accuracy:", round(
    balanced_accuracy_score(y, predictions), 3
))

print("Out-of-fold macro F1:", round(
    f1_score(
        y,
        predictions,
        average="macro",
        zero_division=0,
    ),
    3,
))


# ============================================================
# 11. CLASSIFICATION REPORT
# ============================================================

print("\nClassification report:")

print(
    classification_report(
        y,
        predictions,
        labels=np.arange(len(encoder.classes_)),
        target_names=encoder.classes_,
        zero_division=0,
    )
)


# ============================================================
# 12. CONFUSION MATRIX
# ============================================================

matrix = confusion_matrix(
    y,
    predictions,
    labels=np.arange(len(encoder.classes_)),
)

matrix_df = pd.DataFrame(
    matrix,
    index=encoder.classes_,
    columns=encoder.classes_,
)

print("\nConfusion matrix:")
print(matrix_df)

matrix_df.to_csv(
    RESULTS_DIR / "tuned_rf_confusion_matrix.csv"
)


# ============================================================
# 13. SAVE RESULTS
# ============================================================

results_df = pd.DataFrame(
    search.cv_results_
).sort_values(
    by="mean_test_score",
    ascending=False,
)

results_df.to_csv(
    RESULTS_DIR / "random_forest_tuning_results.csv",
    index=False,
)

prediction_df = pd.DataFrame(
    {
        "Actual Cycle Length": y_text.to_numpy(),
        "Predicted Cycle Length": encoder.inverse_transform(
            predictions
        ),
    }
)

prediction_df.to_csv(
    RESULTS_DIR / "tuned_rf_predictions.csv",
    index=False,
)

print("\nSaved files:")
print(RESULTS_DIR / "random_forest_tuning_results.csv")
print(RESULTS_DIR / "tuned_rf_confusion_matrix.csv")
print(RESULTS_DIR / "tuned_rf_predictions.csv")

print("\nRandom Forest tuning complete!")