# import json
# import pandas as pd
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
# import shap
# import joblib

# # Load data from synthetic JSON
# with open('synthetic_data.json') as f:
#     data = json.load(f)

# # Convert to DataFrame
# df = pd.DataFrame(data)

# # Example schema: modify to match your dataset
# # 'name', 'aadhaar_verified', 'land_size_acres', 'is_govt_employee', 'income_level', 'eligible'

# # Encode categorical variables if needed
# df['aadhaar_verified'] = df['aadhaar_verified'].astype(int)
# df['is_govt_employee'] = df['is_govt_employee'].astype(int)

# # Define features and label
# features = ['aadhaar_verified', 'land_size_acres', 'is_govt_employee', 'income_level']
# label = 'eligible'

# X = df[features]
# y = df[label]

# # Split data
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # Train model
# model = RandomForestClassifier(n_estimators=100, random_state=42)
# model.fit(X_train, y_train)

# # Save model
# joblib.dump(model, 'model.pkl')
# print("✅ Model saved as model.pkl")

# # Generate SHAP explanations for 1 sample
# explainer = shap.TreeExplainer(model)
# shap_values = explainer.shap_values(X_test)

# # Save SHAP explanation for the first applicant
# explanation = {
#     'base_value': explainer.expected_value[1],
#     'feature_values': X_test.iloc[0].to_dict(),
#     'shap_values': dict(zip(features, shap_values[1][0].tolist()))
# }

# with open('shap_values.json', 'w') as f:
#     json.dump(explanation, f, indent=2)

# print("✅ SHAP explanation saved as shap_values.json")

import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Load JSON data
with open('synthetic_data.json') as f:
    data = json.load(f)['applicants']  # Assuming data is under 'applicants' key

# Convert to DataFrame
df = pd.DataFrame(data)

# Encode categorical variables
label_encoders = {}
categorical_cols = ['caste', 'housing_status']

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le  # Save encoder for future use

# Define features and target
features = ['age', 'caste', 'income', 'land_ownership', 'housing_status']
target = 'eligible'

X = df[features]
y = df[target]

# Convert boolean to int (if needed)
X['land_ownership'] = X['land_ownership'].astype(int)

# Split data into train/test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42
)

# Initialize and train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
model.fit(X_train, y_train)

# Save model and encoders
joblib.dump(model, 'eligibility_model.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')

# Print success message
print("Model trained and saved successfully.")
print(f"Model accuracy: {model.score(X_test, y_test):.2f}")