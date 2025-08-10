from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import pandas as pd
import joblib
import shap
import json
import requests
import numpy as np
import google.generativeai as genai
from web3 import Web3

from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import os
from datetime import datetime
import traceback

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model & encoders
model = joblib.load("eligibility_model.pkl")
encoders = joblib.load("label_encoders.pkl")

# Configure Gemini API
genai.configure(api_key="AIzaSyAcKQM2cEqbO2ve4-eDj9IBap2zDxgYA28")

# Pinata Configuration
PINATA_API_KEY = "32ec36acb17859795347"
PINATA_SECRET_KEY = "3ad5126b238e0f3daf92d2bbe5ba10aac942f1a50af1cebe80788b0827e9051f"
PINATA_HEADERS = {
    "pinata_api_key": PINATA_API_KEY,
    "pinata_secret_api_key": PINATA_SECRET_KEY
}

 # Web3 config (Hardhat Localhost)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

# Load contract ABI
with open("../artifacts/contracts/PMKisan.sol/PMKisanRegistry.json") as f:
    contract_abi = json.load(f)["abi"]

contract = w3.eth.contract(address=contract_address, abi=contract_abi)
deployer_account = w3.eth.accounts[0]

# Replace with your actual CID from the transformed database
CURRENT_DATABASE_CID = "QmVYS13RPiaxHiRjvXLAjxBBN2yhvNWkMLzj4x8pCL7rmU"

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

class Applicant(BaseModel):
    aadhaar: int
    name: str
    age: int
    caste: str
    income: float
    land_ownership: bool
    housing_status: str

def fetch_database_from_ipfs(cid: str) -> Dict[str, Any]:
    """Fetch the current database from IPFS"""
    try:
        response = requests.get(f"https://gateway.pinata.cloud/ipfs/{cid}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching database from IPFS: {e}")
        # Return empty database structure if fetch fails
        return {
            "metadata": {
                "total_participants": 0,
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            },
            "participants": []
        }

def upload_to_pinata(data: Dict[str, Any], filename: str) -> str:
    """Upload data to Pinata and return CID"""
    try:
        # Save to temporary file
        with open(filename, "w") as f:
            json.dump(data, f, cls=NumpyEncoder, indent=2)
        
        # Upload to Pinata
        with open(filename, "rb") as f:
            files = {'file': (filename, f)}
            response = requests.post(
                "https://api.pinata.cloud/pinning/pinFileToIPFS",
                files=files,
                headers=PINATA_HEADERS
            )
        
        response.raise_for_status()
        cid = response.json()["IpfsHash"]
        
        # Clean up temporary file
        os.remove(filename)
        
        return cid
    except Exception as e:
        print(f"Error uploading to Pinata: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload to IPFS: {str(e)}")

def generate_explanation_text(features: Dict[str, Any], shap_values: list, prediction_bool: bool) -> str:
    """Generate human-readable explanation using Gemini"""
    prompt = f"""
Explain in plain language the eligibility decision for PM-KISAN scheme.

Applicant Details:
- Age: {features['age']} years
- Caste: {features['caste']}
- Annual Income: ₹{features['income']:,}
- Land Ownership: {"Yes" if features['land_ownership'] else "No"}
- Housing Status: {features['housing_status']}

Decision: {"ELIGIBLE" if prediction_bool else "NOT ELIGIBLE"}

SHAP Feature Importance Scores:
{shap_values}

Provide a clear, simple explanation in 2-3 sentences about why this decision was made based on the PM-KISAN eligibility criteria.
"""
    try:
        model_gemini = genai.GenerativeModel("models/gemini-2.0-flash")
        response = model_gemini.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating explanation: {e}")
        return f"Decision: {'Eligible' if prediction_bool else 'Not Eligible'} based on model prediction."

@app.post("/predict")
def predict_eligibility(applicant: Applicant):
    try:

        global CURRENT_DATABASE_CID
        # 1. Prepare input for prediction
        input_data = pd.DataFrame([{
            "age": applicant.age,
            "caste": applicant.caste,
            "income": applicant.income,
            "land_ownership": int(applicant.land_ownership),
            "housing_status": applicant.housing_status
        }])
        
        # Encode categorical features
        input_data['caste'] = input_data['caste'].map({"SC": 0, "ST": 1, "OBC": 2, "General": 3})
        input_data['housing_status'] = input_data['housing_status'].map({"kutcha": 0, "semi-pucca": 1, "pucca": 2})

        # 2. Make prediction
        prediction = model.predict(input_data)[0]
        prediction_bool = bool(prediction)
        confidence = float(np.max(model.predict_proba(input_data)[0]))

        # 3. Generate SHAP explanation
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(input_data)
        shap_val = shap_values[1] if isinstance(shap_values, list) and len(shap_values) > 1 else shap_values
        expected_val = explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value

        shap_array = np.array(shap_val)  # safe conversion
        shap_row = shap_array[0] if shap_array.ndim == 2 else shap_array
        if shap_row.ndim != 1:
            shap_row = shap_row.flatten()


        contributions = {}
        for col, val in zip(input_data.columns.tolist(), shap_row):
            contributions[col] = float(val) if np.isscalar(val) else float(np.array(val).flatten()[0])

        # 4. Create explanation dictionary
        explanation_dict = {
            "applicant_info": {
                "aadhaar": applicant.aadhaar,
                "name": applicant.name,
                "age": applicant.age,
                "caste": applicant.caste,
                "income": applicant.income,
                "land_ownership": applicant.land_ownership,
                "housing_status": applicant.housing_status
            },
            "prediction": {
                "eligible": prediction_bool,
                "confidence": confidence
            },
            "explanation": {
                "feature_names": input_data.columns.tolist(),
                "shap_values": shap_row.tolist(),

                "base_value": float(expected_val) if np.isscalar(expected_val) else float(expected_val[0]),

                "feature_contributions": contributions

            },
            "timestamp": datetime.now().isoformat()
        }

        # Generate LLM explanation
        explanation_text = generate_explanation_text(
            explanation_dict["applicant_info"],
            explanation_dict["explanation"]["feature_contributions"],
            prediction_bool
        )
        explanation_dict["explanation"]["llm_explanation"] = explanation_text

# 5. Upload explanation to IPFS
        explanation_cid = upload_to_pinata(explanation_dict, f"explanation_{applicant.aadhaar}.json")

        # 🔗 Call the smart contract to store record on-chain
        tx_hash = contract.functions.storeDecision(
            CURRENT_DATABASE_CID,  # databaseCID
            explanation_cid,       # explanationCID
            "Eligible" if prediction_bool else "Not Eligible",
            int(applicant.aadhaar) % (10**6)  # mock participantId (or better from database)
        ).transact({"from": deployer_account})

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)      
        print("✅ Stored decision on blockchain, tx hash:", receipt.transactionHash.hex())


        # 6. Fetch current database from IPFS
        current_database = fetch_database_from_ipfs(CURRENT_DATABASE_CID)
        
        # 7. Add new participant to database
        new_participant_id = len(current_database["participants"]) + 1
        
        new_participant = {
            "participant_id": new_participant_id,
            "aadhaar": applicant.aadhaar,
            "name": applicant.name,
            "age": applicant.age,
            "caste": applicant.caste,
            "income": applicant.income,
            "land_ownership": applicant.land_ownership,
            "housing_status": applicant.housing_status,
            "eligible": prediction_bool,
            "decision_date": datetime.now().isoformat(),
            "explanation_cid": explanation_cid,
            "confidence": confidence
        }
        
        current_database["participants"].append(new_participant)
        
        # Update metadata
        current_database["metadata"]["total_participants"] = len(current_database["participants"])
        current_database["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # 8. Upload updated database to IPFS
        updated_database_cid = upload_to_pinata(current_database, f"database_updated_{new_participant_id}.json")
        
        # Update the global current database CID for next request
        
        CURRENT_DATABASE_CID = updated_database_cid

       

        
        # 9. Return response with both CIDs
        return {
            "eligible": prediction_bool,
            "confidence": confidence,
            "explanation": explanation_text,
            "feature_contributions": contributions,
            "participant_id": new_participant_id,
            "database_cid": updated_database_cid,
            "explanation_cid": explanation_cid,
            "total_participants": current_database["metadata"]["total_participants"]
        }
        
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/database/{cid}")
def get_database_info(cid: str):
    """Get information about the database from IPFS"""
    try:
        database = fetch_database_from_ipfs(cid)
        return {
            "metadata": database["metadata"],
            "participants": database["participants"],
            "ipfs_link": f"https://gateway.pinata.cloud/ipfs/{cid}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch database: {str(e)}")

@app.get("/stats")
def get_stats():
    """Get overall statistics from current database"""
    try:
        database = fetch_database_from_ipfs(CURRENT_DATABASE_CID)
        eligible_count = sum(1 for p in database["participants"] if p.get("eligible", False))
        not_eligible_count = len(database["participants"]) - eligible_count
        
        return {
            "total_participants": len(database["participants"]),
            "eligible_count": eligible_count,
            "not_eligible_count": not_eligible_count,
            "current_database_cid": CURRENT_DATABASE_CID,
            "last_updated": database["metadata"]["last_updated"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/participant/{participant_id}")
def get_participant_info(participant_id: int):
    """Get specific participant information"""
    try:
        database = fetch_database_from_ipfs(CURRENT_DATABASE_CID)
        participant = next((p for p in database["participants"] if p["participant_id"] == participant_id), None)
        
        if not participant:
            raise HTTPException(status_code=404, detail="Participant not found")
        
        return participant
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get participant: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)










































































