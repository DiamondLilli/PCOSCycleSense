from pathlib import Path
import sys

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results"
GRAPH_DIR = RESULTS_DIR / "graphs" / "dummy_baseline"

GRAPH_DIR.mkdir(parents=True, exist_ok=True)

# Find the saved Dummy Baseline predictions.
prediction_files = list(
    RESULTS_DIR.glob("predictions_*dummy*baseline*.csv")
)

if not prediction_files:
    print("No Dummy Baseline predictions found.")
    print("Run the Dummy Baseline model first:")
    print("python notebooks/01_dummy_baseline.py")
    sys.exit(1)

df = pd.read_csv(prediction_files[0])

actual_column = "Actual cycle category"
predicted_column = "Predicted cycle category"

if actual_column not in df.columns or predicted_column not in df.columns:
    raise ValueError(
        f"Unexpected prediction CSV columns: {df.columns.tolist()}"
    )

actual = df[actual_column]
predicted = df[predicted_column]

class_names = sorted(actual.unique())

# 1. Confusion Matrix
from sklearn.metrics import confusion_matrix

cm = confusion_matrix(
    actual,
    predicted,
    labels=class_names
)

plt.figure(figsize=(10, 7))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=class_names,
    yticklabels=class_names
)

plt.title("Dummy Baseline - Confusion Matrix")
plt.xlabel("Predicted Cycle Category")
plt.ylabel("Actual Cycle Category")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

plt.savefig(GRAPH_DIR / "confusion_matrix.png", dpi=300)
plt.close()

# 2. Actual vs Predicted Distribution
comparison = pd.DataFrame({
    "Actual": actual.value_counts(),
    "Predicted": predicted.value_counts()
}).fillna(0)

comparison = comparison.reindex(class_names, fill_value=0)

comparison.plot(kind="bar", figsize=(11, 6))

plt.title("Dummy Baseline - Actual vs Predicted Distribution")
plt.xlabel("Cycle Category")
plt.ylabel("Number of Samples")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

plt.savefig(GRAPH_DIR / "actual_vs_predicted.png", dpi=300)
plt.close()

# 3. Classification Metrics
from sklearn.metrics import classification_report

report = classification_report(
    actual,
    predicted,
    labels=class_names,
    output_dict=True,
    zero_division=0
)

metrics = pd.DataFrame({
    category: {
        "Precision": report[category]["precision"],
        "Recall": report[category]["recall"],
        "F1-score": report[category]["f1-score"]
    }
    for category in class_names
}).T

metrics.to_csv(GRAPH_DIR / "classification_metrics.csv")

metrics.plot(kind="bar", figsize=(11, 6), ylim=(0, 1))

plt.title("Dummy Baseline - Per-Class Performance")
plt.xlabel("Cycle Category")
plt.ylabel("Score")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

plt.savefig(GRAPH_DIR / "per_class_performance.png", dpi=300)
plt.close()

print("\nDummy Baseline graphs generated successfully!")
print("Saved to:", GRAPH_DIR)
print("\nGenerated files:")
for file in GRAPH_DIR.iterdir():
    print(file.name)