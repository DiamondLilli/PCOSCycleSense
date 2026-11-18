from xgboost import XGBClassifier

from common_model_utils import evaluate_model


model = XGBClassifier(
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
)

if __name__ == "__main__":

    evaluate_model(
        "XGBoost",
        model,
    )