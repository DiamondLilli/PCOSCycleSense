# PCOSCycleSense 

**PCOSCycleSense** is a machine learning-based menstrual cycle prediction platform designed to help women diagnosed with Polycystic Ovary Syndrome (PCOS) understand and anticipate their menstrual cycles. Unlike conventional cycle prediction approaches that often rely on average cycle lengths, this project explores the challenges of predicting cycles using irregular, sparse, and variable menstrual history data.

## Overview

Menstrual cycle prediction can be particularly challenging for women with PCOS due to variations in cycle duration and irregular patterns. PCOSCycleSense investigates how machine learning models can learn from individual cycle characteristics to provide more informed predictions.

The project evaluates multiple classification algorithms and explores the role of cycle variability, class imbalance, and evaluation strategies in building reliable prediction models.

## Key Features

- **Machine Learning-Based Prediction:** Implements Logistic Regression, Random Forest, XGBoost, and CatBoost for menstrual cycle pattern prediction.
- **Comparative Model Evaluation:** Compares models using accuracy, balanced accuracy, and macro F1-score.
- **Irregular Cycle Analysis:** Investigates the challenges of learning from sparse and irregularly sampled menstrual history data.
- **Data Collection:** Uses consent-based data collection to address the limited availability of PCOS-specific menstrual cycle datasets.
- **Interactive Web Application:** Provides a web-based interface for cycle assessment, prediction insights, and cycle history management.

## Machine Learning Approach

The project explores multiple classification models:

- Logistic Regression
- Random Forest
- XGBoost
- CatBoost

Stratified cross-validation and macro F1-based hyperparameter selection are used to evaluate model performance while accounting for class imbalance.

Random Forest achieved the best performance among the evaluated models on the available dataset.

## Research Motivation

A central research question behind PCOSCycleSense is:

*Can individual menstrual cycle intervals and patterns provide more reliable predictions than conventional approaches based primarily on average cycle length?*

The project explores the limitations of existing prediction approaches when applied to irregular menstrual cycles and investigates the potential of data-driven methods for more personalized cycle prediction.

## Tech Stack

- **Programming:** Python
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** Scikit-learn, XGBoost, CatBoost
- **Visualization:** Matplotlib
- **Frontend:** React.js
- **Backend:** FastAPI

## Disclaimer

PCOSCycleSense is an academic research project and is not intended to diagnose PCOS, replace medical advice, or serve as a clinically validated medical prediction system.
