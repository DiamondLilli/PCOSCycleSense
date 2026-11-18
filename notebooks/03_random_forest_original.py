from sklearn.ensemble import RandomForestClassifier

from common_model_utils import evaluate_model


model = RandomForestClassifier(
    n_estimators=300,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42,
    n_jobs=1,
)

if __name__ == "__main__":

    evaluate_model(
        "Random Forest (original)",
        model,
    )