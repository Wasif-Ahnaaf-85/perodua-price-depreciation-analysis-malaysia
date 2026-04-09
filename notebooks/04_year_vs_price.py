import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Connect & Extract
load_dotenv()
db_pass = os.getenv('MYSQL_PASSWORD')
engine = create_engine(f"mysql+pymysql://root:{db_pass}@localhost/malaysia_car_market_db")
df = pd.read_sql("SELECT year, price, model FROM clean_car_listings;", con=engine)

# Data Prep
df = df.dropna(subset=['year', 'price', 'model'])
df['model'] = df['model'].str.title()

df = df[df['year'] >= 1994]
top_models = df['model'].value_counts().nlargest(5).index.tolist()
df_filtered = df[df['model'].isin(top_models)]

# Output Settings
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, '..', 'output')
os.makedirs(output_dir, exist_ok=True)

print(f"Generating realistic trends for: {top_models}")
plt.figure(figsize=(19.2, 10.8))

ax = sns.lineplot(data=df_filtered, x='year', y='price', hue='model',
                  linewidth=3, marker='o', markersize=8)

plt.title('Perodua Resale Value: Model-Specific Lifecycle (1994 - 2015)', fontsize=26, fontweight='bold', pad=25)
plt.xlabel('Year of Manufacture', fontsize=18)
plt.ylabel('Market Price (RM)', fontsize=18)

# Formatting
plt.xticks(range(1994, 2016, 2), fontsize=14)
plt.yticks(fontsize=14)
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
plt.grid(True, linestyle='--', alpha=0.4)
plt.legend(title="Car Model", fontsize=12, title_fontsize=14)
sns.despine()

plt.tight_layout()
plt.savefig(os.path.join(output_dir, '04_year_vs_price.png'), dpi=100, bbox_inches='tight')
plt.show()