import pandas as pd
from sqlalchemy import create_engine
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("walmart_pipeline")


# EXTRACT: read the messy CSV
df = pd.read_csv("/Users/pranavkumarkaparthi/Desktop/Practice Datasets/walmart_pipeline/data/raw/Walmart_Sales_Messy.csv")
logger.info("Loaded messy data:", df.shape)

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
logger.info("Cleaned data:", df.shape)


# SAVE: write the clean data to its own file (raw stays untouched)
os.makedirs("/Users/pranavkumarkaparthi/Desktop/Practice Datasets/walmart_pipeline/data/processed", exist_ok=True)
missing = df["Weekly_Sales"].isna().sum()
negative=(df["Weekly_Sales"]<0).sum()
stores=(df["Store"]).nunique()
logger.info(f"Validation: missing={missing}, negative={negative}, stores={stores}")
if missing>0: 
    raise ValueError(f"Validation failed:{missing} roes with missing sales")
if negative > 0:
    raise ValueError(f"Validation failed: {negative} rows with negative sales")
if stores != 45:
    raise ValueError(f"Validation failed: expected 45 stores, found {stores}")
logger.info("All validation checks passed")



df.to_csv("/Users/pranavkumarkaparthi/Desktop/Practice Datasets/walmart_pipeline/data/processed/walmart_clean.csv", index=False)
logger.info("Saved walmart_clean.csv")

# LOAD: push into the SQLite database
engine = create_engine("postgresql+psycopg2://pranavkumarkaparthi@localhost/walmart")
df.to_sql("weekly_sales", engine, if_exists="replace", index=False)
logger.info("Loaded to database:", len(df), "rows")



# VALIDATE: prove the data is healthy
# CONFIRM: verify the load landed
loaded = pd.read_sql("SELECT COUNT(*) FROM weekly_sales", engine).iloc[0, 0]
logger.info(f"Rows in database: {loaded}")

engine.dispose()
logger.info("Pipeline complete!")
