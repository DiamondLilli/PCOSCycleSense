import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

# --------------------------------------------------
# 1. LOAD DATASET
# --------------------------------------------------

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "datasetpcos.csv"
)

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("PCOS CYCLESENSE: EXPLORATORY DATA ANALYSIS")
print("=" * 60)

print("\nDataset shape:", df.shape)

# --------------------------------------------------
# 2. CLEAN COLUMN NAMES
# --------------------------------------------------

df.columns = df.columns.str.strip()

# Remove exact duplicate rows
print("\nDuplicate rows before cleaning:", df.duplicated().sum())

df = df.drop_duplicates().reset_index(drop=True)

print("Dataset shape after removing duplicates:", df.shape)

# --------------------------------------------------
# 3. NORMALIZE CATEGORICAL VALUES
# --------------------------------------------------

for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].str.strip()

# --------------------------------------------------
# 4. PCOS DISTRIBUTION
# --------------------------------------------------

print("\nPCOS distribution:")
print(df["PCOS"].value_counts(dropna=False))

print("\nPCOS percentages:")
print(
    (df["PCOS"].value_counts(normalize=True, dropna=False) * 100)
    .round(2)
)

# --------------------------------------------------
# 5. CYCLE LENGTH DISTRIBUTION
# --------------------------------------------------

print("\nCycle length distribution:")
print(df["Cycle Length"].value_counts(dropna=False))

print("\nCycle length by PCOS status:")
print(
    pd.crosstab(
        df["PCOS"],
        df["Cycle Length"],
        margins=True
    )
)

# --------------------------------------------------
# 6. PERIOD LENGTH DISTRIBUTION
# --------------------------------------------------

print("\nPeriod length distribution:")
print(df["Period Length"].value_counts(dropna=False))

# --------------------------------------------------
# 7. IRREGULAR PERIODS
# --------------------------------------------------

print("\nIrregular or missed periods by PCOS status:")
print(
    pd.crosstab(
        df["PCOS"],
        df["irregular or missed periods"],
        normalize="index"
    ).round(3)
)

# --------------------------------------------------
# 8. VISUALIZE CYCLE LENGTH CATEGORIES
# --------------------------------------------------

cycle_counts = (
    df.groupby(["Cycle Length", "PCOS"])
    .size()
    .unstack(fill_value=0)
)

cycle_counts.plot(kind="bar", figsize=(10, 6))

plt.title("Reported Cycle Length Categories by PCOS Status")
plt.xlabel("Reported Cycle Length")
plt.ylabel("Number of Respondents")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.show()

# --------------------------------------------------
# 9. CHECK FOR MISSING VALUES
# --------------------------------------------------

print("\nMissing values:")
print(
    df.isnull()
    .sum()
    .sort_values(ascending=False)
    .head(15)
)

print("\nAnalysis complete.")