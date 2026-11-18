from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from plot_model_graphs import generate_model_graphs
from common_model_utils import load_pcos_data

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"

X, y, class_names = load_pcos_data()

# Update these paths and column names to match the prediction
# CSV produced by your logistic regression script.
PREDICTIONS_FILE = RESULTS / "logistic_regression" / "oof_predictions.csv"

df = __import__("pandas").read_csv(PREDICTIONS_FILE)

generate_model_graphs(
    y_true=df["actual"],
    y_pred=df["predicted"],
    class_names=class_names,
    output_dir=RESULTS / "graphs" / "logistic_regression",
    model_name="Logistic Regression"
)