import pandas as pd
import re
import numpy as np
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

COLUMN_MAP = {
    'Desc': 'description',
    'Link': 'link',
    'Make': 'make',
    'Model': 'model',
    'Year': 'year',
    'Engine.Cap': 'engine_cap',
    'Transm': 'transmission',
    'Mileage': 'mileage',
    'Color': 'color',
    'Car.Type': 'car_type',
    'Updated': 'updated_date',
    'Price': 'price'
}


# --- PHASE 2(1): NLP TEXT PREPROCESSING

def clean_engine_cap(engine_str):
    """Extracting numeric value from strings like '1495cc'"""
    if pd.isna(engine_str) or str(engine_str).strip() == '-':
        return np.nan

    cleaned = re.sub(r'[^\d]', '', str(engine_str))

    try:
        return int(cleaned) if cleaned else np.nan
    except ValueError:
        return np.nan


def clean_mileage(mileage_str):
    """Handling the literal 'NA' strings and cleans text"""
    if pd.isna(mileage_str) or str(mileage_str).strip().upper() == 'NA':
        return np.nan

    mileage_str = str(mileage_str).lower()
    multiplier = 1000 if 'k' in mileage_str else 1

    cleaned = re.sub(r'[^\d]', '', mileage_str)

    try:
        return int(cleaned) * multiplier if cleaned else np.nan
    except ValueError:
        return np.nan


# --- PHASE 1: EXTRACTION & WRANGLING ---

def run_preprocessing(file_path):
    print("🚀 Loading raw dataset...")
    df = pd.read_csv(file_path)

    print("🔄 Mapping and standardizing schema...")
    # Renaming columns using configuration dictionary
    df.rename(columns=COLUMN_MAP, inplace=True)

    print("🧹 Initiating NLP Text Preprocessing (Regex) and Handling Missing Data...")

    try:
        # Applying Regex functions to clean the messy columns
        df['cleaned_engine_cap'] = df['engine_cap'].apply(clean_engine_cap)
        df['cleaned_mileage'] = df['mileage'].apply(clean_mileage)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')

        print("✅ Preprocessing complete! Here is the Before & After for the target columns:\n")

        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)

        print(df[['engine_cap', 'cleaned_engine_cap', 'mileage', 'cleaned_mileage', 'price']].head(15))

        print("\n📊 Missing Data Summary:")
        print(df[['cleaned_engine_cap', 'cleaned_mileage']].isna().sum())

        print("\n🧹 Phase 3: Statistical Wrangling (Duplicates & Outliers)...")

        # 1. Drop exact duplicate rows based on the 'link' column (the unique URL)
        initial_count = len(df)
        df = df.drop_duplicates(subset=['link'])
        print(f"✅ Dropped {initial_count - len(df)} duplicate listings.")

        # 2. Drop rows where price is missing
        df = df.dropna(subset=['price'])

        # 3. Apply the IQR filter to the price column
        df = remove_outliers_iqr(df, 'price')

        print(f"\n🚀 Final Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns.")

    except KeyError as e:
        print(f"\n⚠️ CRITICAL ERROR: Column Mapping Failed!")
        print(f"The dataset is missing a mapped column: {e}")
        print(f"Current columns in CSV: {df.columns.tolist()}")

    return df

# --- PHASE 3: STATISTICAL WRANGLING ---

def remove_outliers_iqr(df, column):

    print(f"📉 Running IQR outlier detection on '{column}'...")

    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    initial_rows = len(df)
    df_clean = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    dropped_rows = initial_rows - len(df_clean)

    print(f"   -> Dropped {dropped_rows} rows as outliers. (Limits: {lower_bound} to {upper_bound})")
    return df_clean


# --- PHASE 4: DATABASE ENGINEERING (LOAD) ---

def load_to_mysql(df, table_name, db_password):
    """Pushes the clean Pandas DataFrame to a local MySQL database."""
    print(f"\n🗄️ Pushing data to MySQL database table: '{table_name}'...")

    engine = create_engine(f"mysql+pymysql://root:{db_password}@localhost/malaysia_car_market_db")

    try:
        # Pushing the dataframe. 'replace' overwrites the table if it exists.
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        print(f"✅ Successfully loaded {len(df)} rows into MySQL!")
    except Exception as e:
        print(f"⚠️ Database Error: {e}")


if __name__ == "__main__":
    # 1. Securely load environment variables from the .env file
    load_dotenv()

    # 2. Pathing
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_file = os.path.join(script_dir, '..', 'data', 'Malaysia_Final_CarList_.csv')

    print(f"🔍 Looking for dataset at: {os.path.abspath(raw_file)}\n")

    # 3. Extract & Transform (Phases 1-3)
    cleaned_data = run_preprocessing(raw_file)

    # 4. Load (Phase 4) - Fetch password securely
    mysql_password = os.getenv('MYSQL_PASSWORD')

    if not mysql_password:
        print("⚠️ CRITICAL ERROR: MYSQL_PASSWORD not found.")
        print("Please ensure your .env file exists in the root directory and contains MYSQL_PASSWORD=your_password")
    else:
        load_to_mysql(cleaned_data, table_name='clean_car_listings', db_password=mysql_password)