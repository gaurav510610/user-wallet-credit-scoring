# Aave V2 Wallet Credit Scoring

## Overview
This project develops a machine learning-based model that assigns a credit score ranging from 0 to 1000 to Ethereum wallets based on their behavior on the Aave V2 DeFi protocol.

## Objective
The goal is to identify and score wallet addresses based on how responsibly they interact with the lending and borrowing protocol. Responsible wallets receive high scores, while bot-like or risky ones are penalized.

## 📁 Dataset
[Download user-wallet-transactions.json (Google Drive)](https://drive.google.com/drive/folders/1eG43qukp23nOWZqc7HfyPI4HtQlo8V5y?usp=drive_link)


## Data Used 
  - The data comes from `user-wallet-transactions.json`.
  - It contains around 100,000 DeFi transactions.
  - Each record includes:
  - Wallet address
  - Timestamp
  - Action (deposit, borrow, repay, redeemUnderlying, liquidationCall)
  - Action amount
## Feature Engineering
From the raw data, the following wallet-level features were engineered:
- **timestamp**: action time (in seconds)
- **actionData**: a nested dict containing type, amount, etc.
- **Total deposit**
- **Total borrow**
- **Total repay**
- **Liquidations**
- **Number of transactions**
- **Active days**-Unique active dates
- **Average transactions per day**
- **Net position** = deposit + repay − borrow − redeemunderlying

These features were essential in clustering wallets based on behavior.

## Credit Scoring Method    
**1. Feature Scaling**: Used `MinMaxScaler` to normalize numerical features

**2. Clustering**: `Applied KMeans clustering` to group wallets into 5 segments based on their transaction behavior.    

**3. Score Assignment**:
  - Clusters were ranked by their total net position, repay, and deposit activity.
  - Credit scores were mapped from ranks using:
    - **Cluster 1 (Best)** — Score: **1000**
    - **Cluster 2** — Score: **750**
    - **Cluster 3** — Score: **500**
    - **Cluster 4** — Score: **250**
    - **Cluster 5 (Worst)** — Score: **100**
## output 

A CSV file wallet_credit_scores.csv with the following columns:

- `userWallet`
- `cluster`
- `credit_score_kmeans`
- 
This CSV helps compare behavior-based segmentation and creditworthiness of DeFi wallets.

## How to Run the Script 
 Run the scoring script from the terminal:

```bash
python generate_wallet_scores.py --input user-wallet-transactions.json --output wallet_credit_scores.csv
```

-  **Input file**: `user-wallet-transactions.json`
-  **Output file**: `wallet_credit_scores.csv`
-  This will generate credit scores for each wallet and save the results in a CSV file.

## Visualizations

Two plots are included in the project:

- **Credit Score Distribution** – shows number of wallets in each score bucket
- **Mean Feature Comparison by Score** – shows behavior differences

These graphs are saved as in the repository.

  - `credit_score_distribution.png`
  - `mean_features.png`

##  Repository Structure
- `user-wallet-transactions.json`- data file
- `wallet_credit_score_model.ipynb` — Exploratory notebook
- `generate_wallet_scores.py` — One-step script
- `wallet_credit_scores.csv` — Final output
- `analysis.md` - Wallet behavior analysis
- `readme.md`  - project overview and usage guide

## See Also

Please refer to `analysis.md` for deeper insights into wallet behavior and score ranges.
    
