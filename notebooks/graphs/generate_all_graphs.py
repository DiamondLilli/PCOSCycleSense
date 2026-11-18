from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
)

# Project directories
ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results"
GRAPH_DIR = RESULTS_DIR / "graphs"

GRAPH_DIR.mkdir(parents=True, exist_ok=True)


def generate_graphs(prediction_file, model_name):

    prediction_file = Path(prediction_file)

    if not prediction_file.exists():
        print(f"\nSKIPPING {model_name}")
        print(f"Prediction file not found: {prediction_file}")
        return

    df = pd.read_csv(prediction_file)

    actual_column = "Actual cycle category"
    predicted_column = "Predicted cycle category"

    if (
        actual_column not in df.columns
        or predicted_column not in df.columns
    ):
        print(f"\nSKIPPING {model_name}")
        print("Unexpected columns:", df.columns.tolist())
        return

    actual = df[actual_column].astype(str)
    predicted = df[predicted_column].astype(str)

    classes = sorted(set(actual) | set(predicted))

    output_dir = GRAPH_DIR / model_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------
    # 1. CONFUSION MATRIX
    # ------------------------------------------------

    cm = confusion_matrix(
        actual,
        predicted,
        labels=classes
    )

    plt.figure(figsize=(10, 7))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=classes,
        yticklabels=classes
    )

    plt.title(f"{model_name} - Confusion Matrix")
    plt.xlabel("Predicted Cycle Category")
    plt.ylabel("Actual Cycle Category")
    plt.xticks(rotation=30, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    plt.savefig(
        output_dir / "confusion_matrix.png",
        dpi=300
    )

    plt.close()

    # ------------------------------------------------
    # 2. ACTUAL VS PREDICTED DISTRIBUTION
    # ------------------------------------------------

    comparison = pd.DataFrame({
        "Actual": actual.value_counts(),
        "Predicted": predicted.value_counts()
    }).reindex(classes, fill_value=0)

    comparison.plot(
        kind="bar",
        figsize=(11, 6)
    )

    plt.title(
        f"{model_name} - Actual vs Predicted Distribution"
    )

    plt.xlabel("Cycle Category")
    plt.ylabel("Number of Samples")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    plt.savefig(
        output_dir / "actual_vs_predicted.png",
        dpi=300
    )

    plt.close()

    # ------------------------------------------------
    # 3. PER-CLASS PRECISION, RECALL AND F1
    # ------------------------------------------------

    report = classification_report(
        actual,
        predicted,
        labels=classes,
        output_dict=True,
        zero_division=0
    )

    metrics = pd.DataFrame({
        category: {
            "Precision": report[category]["precision"],
            "Recall": report[category]["recall"],
            "F1-score": report[category]["f1-score"]
        }
        for category in classes
    }).T

    metrics.to_csv(
        output_dir / "classification_metrics.csv"
    )

    metrics.plot(
        kind="bar",
        figsize=(12, 7),
        ylim=(0, 1)
    )

    plt.title(
        f"{model_name} - Per-Class Performance"
    )

    plt.xlabel("Cycle Category")
    plt.ylabel("Score")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    plt.savefig(
        output_dir / "per_class_performance.png",
        dpi=300
    )

    plt.close()

    # ------------------------------------------------
    # 4. CLASSIFICATION REPORT HEATMAP
    # ------------------------------------------------

    plt.figure(figsize=(9, 6))

    sns.heatmap(
        metrics,
        annot=True,
        fmt=".2f",
        cmap="YlGnBu",
        vmin=0,
        vmax=1
    )

    plt.title(
        f"{model_name} - Classification Report"
    )

    plt.tight_layout()

    plt.savefig(
        output_dir / "classification_report_heatmap.png",
        dpi=300
    )

    plt.close()

    print(f"\nSUCCESS: {model_name}")

    for file in output_dir.iterdir():
        print("  ", file.name)


# ----------------------------------------------------
# RUN FOR ALL MODELS
# ----------------------------------------------------

models = {
    "dummy_baseline":
        "predictions_dummy_baseline.csv",

    "logistic_regression":
        "predictions_logistic_regression.csv",

    "random_forest_original":
        "predictions_random_forest_original.csv",

    "random_forest_tuned":
        "predictions_random_forest_tuned.csv",

    "xgboost":
        "predictions_xgboost.csv",

    "catboost":
        "predictions_catboost.csv",
}

for model_name, filename in models.items():

    prediction_file = RESULTS_DIR / filename

    generate_graphs(
        prediction_file=prediction_file,
        model_name=model_name
    )

print("\nGraph generation finished.")
print("Output directory:", GRAPH_DIR)