from catboost import CatBoostClassifier

from common_model_utils import evaluate_model


model = CatBoostClassifier(
    iterations=150,
    depth=3,
    learning_rate=0.03,
    loss_function="MultiClass",
    verbose=False,
    random_seed=42,
    thread_count=1,
    allow_writing_files=False,
)

if __name__ == "__main__":

    evaluate_model(
        "CatBoost",
        model,
    )