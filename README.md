🌾 PM-KISAN Eligibility Platform
This project is a full-stack decentralized application (dApp) for checking and recording eligibility for the PM-KISAN scheme. It integrates a Machine Learning (ML) backend, a React-based dashboard frontend, and Ethereum smart contracts for transparent, tamper-proof record-keeping. The platform leverages an ML model to predict eligibility based on user-provided data, and these decisions are then stored on the Ethereum blockchain and IPFS for public transparency.

✨ Features

Eligibility Prediction – Uses a trained ML model to predict PM-KISAN eligibility based on user-provided data.

Blockchain Storage – Records eligibility decisions and explanations on the Ethereum blockchain via smart contracts, ensuring data integrity and permanence.

IPFS Integration – Stores detailed decision data and explanations on IPFS (InterPlanetary File System) for public accessibility and transparency.

Admin Dashboard – A React-based interface for administrators to manage records, view system statistics, and perform administrative operations.

Automation Scripts – Includes scripts for synthetic data generation, data transformation, and smart contract deployment, streamlining the development and testing process.

📂 Project Structure
```
Vansh/
├── backend/                     # FastAPI backend with ML model and API
│   └── main.py
├── contracts/                   # Solidity smart contracts
│   ├── Lock.sol
│   └── PMKisan.sol
├── frontend/dashboard/          # React frontend dashboard
│   ├── public/
│   └── src/
├── scripts/                     # Deployment and interaction scripts
│   ├── deploy.js
│   └── interact.js
├── test/                        # Contract tests
├── synthetic_data.json          # Synthetic participant data
├── transformed_synthetic_data.json
├── predictions.csv               # Model predictions
├── eligibility_model.pkl         # Trained ML model
├── label_encoders.pkl            # Encoders for categorical features
├── explain.py                    # XAI explanation script
├── generate_data.py              # Data generation script
├── predict.py                    # Prediction script
├── predict_eligibility.py        # API for eligibility prediction
├── train_model.py                # Model training script
├── transform_database.py         # Data transformation script
├── xai_explanation.json          # Example XAI output
├── hardhat.config.js             # Hardhat Ethereum configuration
├── package.json                  # Node.js dependencies
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation

```
🚀 Getting Started
To get the project up and running, follow these steps.

📌 Prerequisites
Ensure you have the following installed before proceeding:

Node.js (v16+)

Python (3.10+)

Hardhat (Ethereum development environment)

MetaMask (browser wallet for interaction)

Ganache or a Hardhat local node (for local testing)

1️⃣ Install Dependencies
First, install the required dependencies for each part of the project.

Backend (Python):
```
Bash

cd backend
pip install -r ../requirements.txt
```
Frontend (React):
```
Bash

cd frontend/dashboard
npm install
```
Contracts / Hardhat:
```
Bash

npm install
```
2️⃣ Train Model & Prepare Data
Run the following scripts to train the ML model and prepare the necessary data files.
```
Bash

python train_model.py
python generate_data.py
python transform_database.py
```
3️⃣ Start Backend API
Navigate to the backend directory and start the FastAPI server.
```
Bash

cd backend
uvicorn main:app --reload
```
4️⃣ Deploy Smart Contracts
In a new terminal, start the Hardhat local node. Keep this terminal running.
```
Bash

npx hardhat node
//(In another terminal, deploy the smart contracts to the local network.)
```
```
Bash

npx hardhat run scripts/deploy.js --network localhost
```
5️⃣ Start Frontend
Start the React development server for the dashboard.
```
Bash

cd frontend/dashboard
npm start
```
Visit http://localhost:3000 in your browser to access the dashboard.

🖥 Usage
After setting up, use the dashboard to check participant eligibility. The system will provide:

The ML prediction result.

A SHAP-based explanation for the prediction.

The blockchain transaction hash for the record.

An IPFS CID link to the explanation JSON file.

The Admin Dashboard allows for file management, viewing statistics, and system optimization.

📜 Smart Contracts
PMKisan.sol – The primary registry for storing eligibility records on the blockchain.

Lock.sol – An example template contract included for Hardhat's default configuration.

⚙ Scripts
deploy.js – A script to deploy the smart contracts to a specified network.

interact.js – A script to demonstrate interaction with the deployed contracts.

🧪 Testing
To ensure the project components are working correctly, run the provided tests.

Contracts:
```
Bash

npx hardhat test
```
Frontend:
```
Bash

cd frontend/dashboard
npm test
```
📄 License
This project is released under the MIT License, making it open for research and development use.