from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from plot_model_graphs import generate_model_graphs
from common_model_utils import load_pcos_data

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"

X, y, class_names = load_pcos_data()

PREDICTIONS_FILE = RESULTS / "random_forest_original" / "oof_predictions.csv"

df = pd.read_csv(PREDICTIONS_FILE)

generate_model_graphs(
    y_true=df["actual"],
    y_pred=df["predicted"],
    class_names=class_names,
    output_dir=RESULTS / "graphs" / "random_forest_original",
    model_name="Random Forest Original"
)