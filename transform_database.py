import json
from datetime import datetime

def transform_database():
    # Load your current synthetic_data.json
    with open('synthetic_data.json', 'r') as f:
        current_data = json.load(f)
    
    # Transform to new format
    new_data = {
        "metadata": {
            "total_participants": len(current_data["applicants"]),
            "last_updated": datetime.now().isoformat(),
            "version": "1.0",
            "description": "PM-KISAN Synthetic Database"
        },
        "participants": []
    }
    
    # Transform each applicant
    for index, applicant in enumerate(current_data["applicants"]):
        new_participant = {
            "participant_id": index + 1,
            "aadhaar": applicant["aadhaar"],
            "name": applicant["name"],
            "age": applicant["age"],
            "caste": applicant["caste"],
            "income": applicant["income"],
            "land_ownership": applicant["land_ownership"],
            "housing_status": applicant["housing_status"],
            "eligible": applicant["eligible"],
            "decision_date": datetime.now().isoformat(),
            "explanation_cid": None  # Will be filled when explanations are generated
        }
        new_data["participants"].append(new_participant)
    
    # Save the transformed data
    with open('transformed_synthetic_data.json', 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print(f"✅ Transformed database saved as 'transformed_synthetic_data.json'")
    print(f"📊 Total participants: {new_data['metadata']['total_participants']}")
    print(f"🗓️ Last updated: {new_data['metadata']['last_updated']}")
    
    return new_data

if __name__ == "__main__":
    transform_database()