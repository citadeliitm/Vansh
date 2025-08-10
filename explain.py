import shap
import pandas as pd
import joblib

model = joblib.load("eligibility_model.pkl")
# encoders = joblib.load("label_encoders.pkl")

# Proper SHAP explainer for tree-based models
explainer = shap.TreeExplainer(model)

def explain_prediction(applicant_features: dict):
    df = pd.DataFrame([applicant_features])

    # Ensure boolean columns are correct
    df["land_ownership"] = df["land_ownership"].astype(int)

    # SHAP explanation
    shap_values = explainer(df)
    feature_names = df.columns.tolist()

    # Get absolute contribution values
    contributions = dict(zip(feature_names, shap_values.values[0]))

    # Sort features by absolute importance
    sorted_contributions = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)

    # Return top 3 feature contributions as explanation
    top_features = [f"{k}: {v:.2f}" for k, v in sorted_contributions[:3]]
    return top_features
