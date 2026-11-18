from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from sklearn.metrics import (
    confusion_matrix,
    classification_report
)


def plot_confusion_matrix(y_true, y_pred, class_names, output_dir, model_name):
    cm = confusion_matrix(
        y_true,
        y_pred,
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

    plt.title(f"{model_name} - Confusion Matrix")
    plt.xlabel("Predicted Cycle Length")
    plt.ylabel("Actual Cycle Length")
    plt.xticks(rotation=30, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    plt.savefig(
        output_dir / "confusion_matrix.png",
        dpi=300
    )
    plt.close()


def plot_classification_metrics(
    y_true,
    y_pred,
    class_names,
    output_dir,
    model_name
):
    report = classification_report(
        y_true,
        y_pred,
        labels=class_names,
        output_dict=True,
        zero_division=0
    )

    metrics = []

    for class_name in class_names:
        if class_name in report:
            metrics.append({
                "Class": class_name,
                "Precision": report[class_name]["precision"],
                "Recall": report[class_name]["recall"],
                "F1-score": report[class_name]["f1-score"]
            })

    df = pd.DataFrame(metrics)

    df.to_csv(
        output_dir / "classification_metrics.csv",
        index=False
    )

    df_plot = df.set_index("Class")

    df_plot.plot(
        kind="bar",
        figsize=(12, 7),
        ylim=(0, 1)
    )

    plt.title(f"{model_name} - Per-Class Performance")
    plt.xlabel("Cycle Length Category")
    plt.ylabel("Score")
    plt.xticks(rotation=30, ha="right")
    plt.legend(loc="lower right")
    plt.tight_layout()

    plt.savefig(
        output_dir / "per_class_performance.png",
        dpi=300
    )
    plt.close()

    plt.figure(figsize=(9, 6))

    sns.heatmap(
        df_plot,
        annot=True,
        fmt=".2f",
        cmap="YlGnBu",
        vmin=0,
        vmax=1
    )

    plt.title(f"{model_name} - Classification Report Heatmap")
    plt.tight_layout()

    plt.savefig(
        output_dir / "classification_report_heatmap.png",
        dpi=300
    )
    plt.close()


def plot_prediction_distribution(
    y_true,
    y_pred,
    class_names,
    output_dir,
    model_name
):
    actual_counts = (
        pd.Series(y_true)
        .value_counts()
        .reindex(class_names, fill_value=0)
    )

    predicted_counts = (
        pd.Series(y_pred)
        .value_counts()
        .reindex(class_names, fill_value=0)
    )

    df = pd.DataFrame({
        "Actual": actual_counts,
        "Predicted": predicted_counts
    })

    df.plot(
        kind="bar",
        figsize=(12, 7)
    )

    plt.title(f"{model_name} - Actual vs Predicted Distribution")
    plt.xlabel("Cycle Length Category")
    plt.ylabel("Number of Samples")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    plt.savefig(
        output_dir / "actual_vs_predicted.png",
        dpi=300
    )
    plt.close()


def generate_model_graphs(
    y_true,
    y_pred,
    class_names,
    output_dir,
    model_name
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_confusion_matrix(
        y_true,
        y_pred,
        class_names,
        output_dir,
        model_name
    )

    plot_classification_metrics(
        y_true,
        y_pred,
        class_names,
        output_dir,
        model_name
    )

    plot_prediction_distribution(
        y_true,
        y_pred,
        class_names,
        output_dir,
        model_name
    )

    print(f"Graphs generated for {model_name}")
    print(f"Location: {output_dir}")