from sklearn.dummy import DummyClassifier

from common_model_utils import evaluate_model


model = DummyClassifier(
    strategy="prior"
)

if __name__ == "__main__":

    evaluate_model(
        "Dummy Baseline",
        model,
    )