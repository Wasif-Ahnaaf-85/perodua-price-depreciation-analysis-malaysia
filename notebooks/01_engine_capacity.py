import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Connect & Extract
load_dotenv()
db_pass = os.getenv('MYSQL_PASSWORD')
engine = create_engine(f"mysql+pymysql://root:{db_pass}@localhost/malaysia_car_market_db")
df = pd.read_sql("SELECT cleaned_engine_cap FROM clean_car_listings;", con=engine)
engine_data = df['cleaned_engine_cap'].dropna()

# Output Paths & Dimensions
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, '..', 'output')
os.makedirs(output_dir, exist_ok=True)
fig_size, dpi_setting = (19.2, 10.8), 100

print("Generating Engine Capacity Chart...")

# Calculate the exact count for each unique engine capacity
engine_counts = engine_data.value_counts().sort_index()

plt.figure(figsize=fig_size)

# Convert capacities to strings.
plt.bar(engine_counts.index.astype(int).astype(str) + ' cc',
        engine_counts.values,
        color='skyblue',
        edgecolor='black',
        width=0.6)

plt.title('Distribution of Engine Capacities in Malaysia', fontsize=24, fontweight='bold', pad=20)
plt.xlabel('Engine Capacity', fontsize=18)
plt.ylabel('Number of Listings', fontsize=18)
plt.xticks(fontsize=14, rotation=0)
plt.yticks(fontsize=14)

# Adding data labels
for i, v in enumerate(engine_counts.values):
    plt.text(i, v + 20, str(v), ha='center', fontsize=14, fontweight='bold', color='darkblue')

# Removing the top and right spines.
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)

plt.savefig(os.path.join(output_dir, '01_engine_capacity.png'), dpi=dpi_setting, bbox_inches='tight')
plt.show()