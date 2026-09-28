import pandas as pd
import sqlite3
import os

# EXTRACT: read the messy CSV
df = pd.read_csv("/Users/pranavkumarkaparthi/Desktop/Practice Datasets/walmart_pipeline/data/raw/Walmart_Sales_Messy.csv")
print("Loaded messy data:", df.shape)

# TRANSFORM: clean it, one fix at a time
df["Store"] = df["Store"].astype(str).str.strip()
df["Holiday_Flag"] = df["Holiday_Flag"].replace({"Y": "1", "N": "0"}).astype(int)
df["Weekly_Sales"] = df["Weekly_Sales"].str.replace(",", "", regex=False)
df = df.dropna(subset=["Weekly_Sales"])
df["Weekly_Sales"] = df["Weekly_Sales"].astype(float)
df = df[df["Weekly_Sales"] >= 0]
df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True)
df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
df = df.drop_duplicates()
print("Cleaned data:", df.shape)


# SAVE: write the clean data to its own file (raw stays untouched)
os.makedirs("/Users/pranavkumarkaparthi/Desktop/Practice Datasets/walmart_pipeline/data/processed", exist_ok=True)
df.to_csv("/Users/pranavkumarkaparthi/Desktop/Practice Datasets/walmart_pipeline/data/processed/walmart_clean.csv", index=False)
print("Saved walmart_clean.csv")

# LOAD: push into the SQLite database
conn = sqlite3.connect("/Users/pranavkumarkaparthi/Desktop/Practice Datasets/walmart_pipeline/walmart.db")
conn.execute("DROP TABLE IF EXISTS weekly_sales")
df.to_sql("weekly_sales", conn, if_exists="replace", index=False)
conn.commit()
print("Loaded to database:", len(df), "rows")



# VALIDATE: prove the data is healthy
print("Check 1 - missing sales (expect 0):")
print(pd.read_sql("SELECT COUNT(*) FROM weekly_sales WHERE Weekly_Sales IS NULL", conn))
print("Check 2 - negative sales (expect 0):")
print(pd.read_sql("SELECT COUNT(*) FROM weekly_sales WHERE Weekly_Sales < 0", conn))
print("Check 3 - distinct stores (expect 45):")
print(pd.read_sql("SELECT COUNT(DISTINCT Store) FROM weekly_sales", conn))

conn.close()
print("Pipeline complete!")
