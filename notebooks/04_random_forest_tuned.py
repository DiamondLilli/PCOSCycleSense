from sklearn.ensemble import RandomForestClassifier

from common_model_utils import evaluate_model


model = RandomForestClassifier(
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

if __name__ == "__main__":

    evaluate_model(
        "Random Forest (tuned)",
        model,
    )