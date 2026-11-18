import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from xgboost import XGBClassifier
from catboost import CatBoostClassifier

from common_model_utils import (
    evaluate_model,
    RESULTS_DIR,
)


MODELS = [

    (
        "Dummy Baseline",
        DummyClassifier(
            strategy="prior"
        ),
    ),

    (
        "Logistic Regression",
        LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            random_state=42,
        ),
    ),

    (
        "Random Forest (original)",
        RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=1,
        ),
    ),

    (
        "Random Forest (tuned)",
        RandomForestClassifier(
            n_estimators=200,
            max_depth=5,
            min_samples_split=6,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight="balanced_subsample",
            criterion="gini",
            random_state=42,
            n_jobs=1,
        ),
    ),

    (
        "XGBoost",
        XGBClassifier(
            n_estimators=150,
            max_depth=2,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=2,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=1,
            verbosity=0,
        ),
    ),

    (
        "CatBoost",
        CatBoostClassifier(
            iterations=150,
            depth=3,
            learning_rate=0.03,
            loss_function="MultiClass",
            verbose=False,
            random_seed=42,
            thread_count=1,
            allow_writing_files=False,
        ),
    ),

]


def main():

    results = []

    for name, model in MODELS:

        print(f"\nRunning {name}...")

        try:

            result = evaluate_model(
                name,
                model,
            )

            results.append(result)

        except Exception as error:

            print(
                f"Error running {name}: {error}"
            )

    if not results:

        raise RuntimeError(
            "No models completed successfully."
        )

    df = pd.DataFrame(results)

    df = df.sort_values(
        by="CV Macro F1 Mean",
        ascending=False,
    )

    csv_path = (
        RESULTS_DIR
        / "all_models_comparison.csv"
    )

    df.to_csv(
        csv_path,
        index=False,
    )

    print("\n" + "=" * 90)
    print("FINAL MODEL COMPARISON")
    print("=" * 90)

    print(
        df.round(3).to_string(index=False)
    )

    # Sort by CV macro F1 for plotting.
    plot_df = df.sort_values(
        "CV Macro F1 Mean",
        ascending=True,
    ).reset_index(drop=True)

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(17, 7),
    )

    x = list(range(len(plot_df)))
    width = 0.24

    # --------------------------------------------------------
    # GRAPH 1: CROSS-VALIDATION METRICS
    # --------------------------------------------------------

    metrics = [
        (
            "CV Accuracy Mean",
            "CV Accuracy Std",
            "Accuracy",
        ),
        (
            "CV Balanced Accuracy Mean",
            "CV Balanced Accuracy Std",
            "Balanced Accuracy",
        ),
        (
            "CV Macro F1 Mean",
            "CV Macro F1 Std",
            "Macro F1",
        ),
    ]

    for i, (
        mean_col,
        std_col,
        label,
    ) in enumerate(metrics):

        positions = [
            value + (i - 1) * width
            for value in x
        ]

        axes[0].bar(
            positions,
            plot_df[mean_col],
            width,
            yerr=plot_df[std_col],
            capsize=3,
            label=label,
        )

    axes[0].set_xticks(x)

    axes[0].set_xticklabels(
        plot_df["Model"],
        rotation=35,
        ha="right",
    )

    axes[0].set_ylim(0, 1)

    axes[0].set_ylabel("Score")

    axes[0].set_title(
        "Cross-Validation Model Comparison"
    )

    axes[0].legend()

    axes[0].grid(
        axis="y",
        alpha=0.25,
    )

    # --------------------------------------------------------
    # GRAPH 2: OUT-OF-FOLD METRICS
    # --------------------------------------------------------

    oof_metrics = [
        ("OOF Accuracy", "Accuracy"),
        (
            "OOF Balanced Accuracy",
            "Balanced Accuracy",
        ),
        ("OOF Macro F1", "Macro F1"),
    ]

    for i, (
        metric,
        label,
    ) in enumerate(oof_metrics):

        positions = [
            value + (i - 1) * width
            for value in x
        ]

        axes[1].bar(
            positions,
            plot_df[metric],
            width,
            label=label,
        )

    axes[1].set_xticks(x)

    axes[1].set_xticklabels(
        plot_df["Model"],
        rotation=35,
        ha="right",
    )

    axes[1].set_ylim(0, 1)

    axes[1].set_ylabel("Score")

    axes[1].set_title(
        "Out-of-Fold Prediction Comparison"
    )

    axes[1].legend()

    axes[1].grid(
        axis="y",
        alpha=0.25,
    )

    fig.suptitle(
        "PCOS CycleSense: Model Comparison",
        fontsize=15,
    )

    fig.text(
        0.5,
        0.01,
        "Exploratory cycle-category classification. "
        "This is not next-period date forecasting.",
        ha="center",
        fontsize=9,
    )

    fig.tight_layout(
        rect=[0, 0.04, 1, 0.94]
    )

    png_path = (
        RESULTS_DIR
        / "model_comparison_metrics.png"
    )

    pdf_path = (
        RESULTS_DIR
        / "model_comparison_metrics.pdf"
    )

    fig.savefig(
        png_path,
        dpi=200,
        bbox_inches="tight",
    )

    fig.savefig(
        pdf_path,
        bbox_inches="tight",
    )

    plt.close(fig)

    print("\nSaved comparison table:")
    print(csv_path)

    print("\nSaved comparative graph:")
    print(png_path)

    print("\nSaved graph as PDF:")
    print(pdf_path)


if __name__ == "__main__":
    main()