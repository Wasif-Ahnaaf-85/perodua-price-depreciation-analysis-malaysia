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
df = pd.read_sql("SELECT cleaned_mileage, price FROM clean_car_listings;", con=engine)

# If mileage is 0 or NaN, categorizing as 'New/Near-New', else 'Used'
df['condition'] = df['cleaned_mileage'].apply(lambda x: 'New' if (pd.isna(x) or x == 0) else 'Used')

# Output Paths & Dimensions
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, '..', 'output')
os.makedirs(output_dir, exist_ok=True)
fig_size, dpi_setting = (19.2, 10.8), 100

print("Generating Price Boxplot (New vs Used)...")
plt.figure(figsize=fig_size)
sns.set_theme(style="white")

# Creating the boxplot
ax = sns.boxplot(data=df, x='condition', y='price', hue='condition',
                 palette={'New': '#72bcd4', 'Used': '#ffb347'},
                 linewidth=2.5, fliersize=2)

plt.title('Market Price Spread: New vs. Used Peroduas', fontsize=24, fontweight='bold', pad=20)
plt.xlabel('Vehicle Condition', fontsize=18)
plt.ylabel('Price (RM)', fontsize=18)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

sns.despine()

plt.savefig(os.path.join(output_dir, '03_price.png'), dpi=dpi_setting, bbox_inches='tight')
plt.show()