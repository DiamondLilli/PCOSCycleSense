import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "datasetpcos.csv"

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found at {DATA_PATH}. Check that you copied the CSV."
    )

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("PCOS CYCLESENSE DATASET INSPECTION")
print("=" * 60)

print(f"\nNumber of rows: {df.shape[0]}")
print(f"Number of columns: {df.shape[1]}")

print("\nCOLUMN NAMES")
for column in df.columns:
    print(f"- {column}")

print("\nFIRST FIVE ROWS")
print(df.head().to_string())

print("\nDATA TYPES")
print(df.dtypes.to_string())

print("\nMISSING VALUES")
print(df.isnull().sum().to_string())

print("\nDUPLICATE ROWS")
print(df.duplicated().sum())

print("\nDATASET INSPECTION COMPLETE")