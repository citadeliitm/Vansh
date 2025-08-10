import pandas as pd
import joblib

model = joblib.load("eligibility_model.pkl")
encoders = joblib.load("label_encoders.pkl")

def run_prediction(data):
	df = pd.DataFrame([data])
	df["land_ownership"] = df["land_ownership"].astype(int)
	for col in ["caste", "housing_status"]:
		df[col] = encoders[col].transform(df[col])
	X = df[["age", "caste", "income", "land_ownership", "housing_status"]]
	return bool(model.predict(X)[0])