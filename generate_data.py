from faker import Faker
import random
import json

fake = Faker()

def generate_applicant():
    caste_options = ['SC', 'ST', 'OBC', 'General']
    housing_status_options = ['kutcha', 'semi-pucca', 'pucca']
    age = random.randint(18, 80)
    caste = random.choice(caste_options)
    income = random.randint(10000, 100000)
    land_ownership = random.choice([True, False])
    housing_status = random.choice(housing_status_options)

    # Define eligibility logic
    eligible = (
        income < 60000 and
        land_ownership == False and
        housing_status != 'pucca'
    )

    return {
        "aadhaar": fake.unique.random_number(digits=12, fix_len=True),
        "name": fake.name(),
        "age": age,
        "caste": caste,
        "income": income,
        "land_ownership": land_ownership,
        "housing_status": housing_status,
        "eligible": eligible
    }

def generate_dataset(n=100):
    return {"applicants": [generate_applicant() for _ in range(n)]}

if __name__ == "__main__":
    data = generate_dataset(100)
    with open("pmay_synthetic_data.json", "w") as f:
        json.dump(data, f, indent=2)