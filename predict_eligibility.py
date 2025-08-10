import json
import pandas as pd
import joblib
from pathlib import Path

def load_model_and_encoders():
    """Load trained model and label encoders"""
    try:
        model = joblib.load('eligibility_model.pkl')
        label_encoders = joblib.load('label_encoders.pkl')
        return model, label_encoders
    except FileNotFoundError as e:
        print(f"Error: {e}. Please train the model first.")
        exit(1)

def load_applicant_data(input_path='synthetic_data.json'):
    """Load applicant data from JSON file"""
    try:
        with open(input_path) as f:
            data = json.load(f)['applicants']
        return pd.DataFrame(data)
    except (FileNotFoundError, KeyError) as e:
        print(f"Error loading data: {e}")
        exit(1)

def preprocess_data(df, label_encoders):
    """Preprocess data for prediction"""
    # Encode categorical fields
    for col in ['caste', 'housing_status']:
        if col in df.columns:
            df[col] = label_encoders[col].transform(df[col])
    
    # Convert boolean to int if exists
    if 'land_ownership' in df.columns:
        df['land_ownership'] = df['land_ownership'].astype(int)
    
    return df

def predict_eligibility(model, df):
    """Make eligibility predictions"""
    features = ['age', 'caste', 'income', 'land_ownership', 'housing_status']
    
    # Check if all required features exist
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        print(f"Warning: Missing features {missing_features} - using available features")
        features = [f for f in features if f in df.columns]
    
    X = df[features]
    return model.predict(X)

def main():
    # Load model and encoders
    model, label_encoders = load_model_and_encoders()
    
    # Load data
    df = load_applicant_data()
    
    # Preprocess data
    processed_df = preprocess_data(df.copy(), label_encoders)
    
    # Make predictions
    predictions = predict_eligibility(model, processed_df)
    df['predicted_eligibility'] = predictions
    
    # Save results
    output_file = 'predictions.csv'
    df[['name', 'aadhaar', 'predicted_eligibility']].to_csv(output_file, index=False)
    
    print(f"Predictions complete. Results saved to {output_file}")
    print("\nSample predictions:")
    print(df[['name', 'aadhaar', 'predicted_eligibility']].head().to_string(index=False))

if __name__ == "__main__":
    main()