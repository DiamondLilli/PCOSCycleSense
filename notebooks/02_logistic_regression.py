from sklearn.linear_model import LogisticRegression

from common_model_utils import evaluate_model


model = LogisticRegression(
    max_iter=3000,
    class_weight="balanced",
    random_state=42,
)

if __name__ == "__main__":

    evaluate_model(
        "Logistic Regression",
        model,
    )