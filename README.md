# Bank Customer Churn Prediction

## Overview
A machine learning project that predicts bank customer churn and assigns risk categories to customers.

## Objectives
- Explore customer churn patterns.
- Engineer relevant predictive features.
- Compare classification models.
- Select a classification threshold using validation data.
- Generate customer-level churn risk scores.
- Visualize risk distribution through a Streamlit dashboard.

## Model
Random Forest Classifier.

## Risk Categories
- Low: Below 30%
- Moderate: 30% to below 50%
- High: 50% to below 70%
- Critical: 70% and above

## Technologies
- Python
- Pandas and NumPy
- Scikit-learn
- Matplotlib and Seaborn
- Streamlit

## Repository Contents
- Bank_Customer_Churn_Analysis.ipynb: Complete analysis and modeling workflow.
- app.py: Streamlit dashboard.
- bank_churn_model.pkl: Trained model and configuration.
- requirements.txt: Project dependencies.

## Limitations
The model's predictions are analytical estimates, not guarantees of customer behavior. Further validation, probability calibration, and fairness assessment are necessary before real-world banking use.
