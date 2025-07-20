import pandas as pd
import json 
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns

# Load the JSON data
with open("user-wallet-transactions.json", 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Convert timestamp to datetime
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

# Extract amount in ETH from actionData
df['amount'] = df['actionData'].apply(lambda x: float(x.get('amount', 0)) / 1e18 if isinstance(x, dict) else 0)

# Create pivot table of actions per wallet
action_pivot = df.pivot_table(
    index='userWallet',
    columns='action',
    values='amount',
    aggfunc='sum',
    fill_value=0
).reset_index()

# Time-based features
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
df['date'] = df['timestamp'].dt.date

wallet_time = df.groupby("userWallet").agg(
    first_tx=("timestamp", "min"),
    last_tx=("timestamp", "max"),
    tx_count=("timestamp", "count"),
    active_days=("date", "nunique")
).reset_index()

wallet_time["avg_tx_per_day"] = wallet_time["tx_count"] / wallet_time["active_days"]

# Merge action and time features
features_df = action_pivot.merge(wallet_time, on="userWallet", how="left")

# Net position feature
features_df["net_position"] = (
    features_df.get("deposit", 0) +
    features_df.get("repay", 0) -
    features_df.get("borrow", 0) -
    features_df.get("redeemUnderlying", 0)
)

# Select features for clustering
model_features = features_df[[
    "deposit", "repay", "borrow", "liquidationcall",
    "net_position", "active_days", "avg_tx_per_day"
]]

# Normalize features
scaler = MinMaxScaler()
scaled_features = scaler.fit_transform(model_features)

# Apply KMeans clustering
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
features_df["cluster"] = kmeans.fit_predict(scaled_features)

# Cluster summary and ranking
score_summary = features_df.groupby("cluster").agg({
    "deposit": "sum",
    "repay": "sum",
    "borrow": "sum",
    "liquidationcall": "sum",
    "net_position": "sum"
})

score_summary["score_metric"] = (
    score_summary["deposit"] +
    score_summary["repay"] -
    score_summary["borrow"] -
    score_summary["liquidationcall"] +
    score_summary["net_position"]
).round(2)

score_summary["rank"] = score_summary["score_metric"].rank(ascending=False, method='min').astype(int)

# Map rank to credit score
rank_to_score = {
    1: 1000,
    2: 750,
    3: 500,
    4: 250,
    5: 100
}
cluster_to_rank = score_summary["rank"].to_dict()

features_df["credit_score_kmeans"] = features_df["cluster"].map(
    lambda c: rank_to_score[cluster_to_rank[c]]
)

# Save credit scores
wallet_scores = features_df[["userWallet", "credit_score_kmeans", "cluster"]]
wallet_scores.to_csv("wallet_credit_scores.csv", index=False)
print(wallet_scores.head())

# Print value counts of credit scores
print(features_df[["cluster", "credit_score_kmeans"]].value_counts().sort_index())
print(features_df["credit_score_kmeans"].value_counts().sort_index())

# Plot credit score distribution
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.countplot(
    data=features_df,
    x='credit_score_kmeans',
    hue='credit_score_kmeans',
    palette='viridis',
    order=sorted(features_df['credit_score_kmeans'].unique(), reverse=True)
)
plt.title("Credit Score Distribution (KMeans-based)", fontsize=16)
plt.xlabel("Credit Score")
plt.ylabel("Number of Wallets")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("credit_score_distribution.png", dpi=300)
plt.show()

# Plot cluster-wise feature means
cluster_means = features_df.groupby('credit_score_kmeans')[
    ['borrow', 'deposit', 'repay', 'net_position', 'tx_count']
].mean()

cluster_means.T.plot(kind='bar', figsize=(12, 6))
plt.title('Mean Feature Values by Cluster')
plt.ylabel('Average Value')
plt.xlabel('Features')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig("cluster_feature_means.png", dpi=300)
plt.show()
