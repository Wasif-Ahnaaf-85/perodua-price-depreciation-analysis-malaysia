import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Connect & Extract
load_dotenv()
db_pass = os.getenv('MYSQL_PASSWORD')
engine = create_engine(f"mysql+pymysql://root:{db_pass}@localhost/malaysia_car_market_db")
df = pd.read_sql("SELECT cleaned_mileage, price, model FROM clean_car_listings;", con=engine)

# Data Prep
used_cars = df.dropna(subset=['cleaned_mileage', 'price', 'model'])
used_cars = used_cars[used_cars['cleaned_mileage'] <= 400000]
used_cars['model'] = used_cars['model'].str.title()

top_3_models = used_cars['model'].value_counts().nlargest(3).index.tolist()
print(f"Top 3 models found: {top_3_models}")

filtered_cars = used_cars[used_cars['model'].isin(top_3_models)]

# Output Paths & Dimensions
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, '..', 'output')
os.makedirs(output_dir, exist_ok=True)
fig_size, dpi_setting = (19.2, 10.8), 100

print("Generating Model-Specific Depreciation Scatter Plot...")
plt.figure(figsize=fig_size)

colors = ['coral', 'skyblue', 'mediumseagreen']

for i, model in enumerate(top_3_models):
    model_data = filtered_cars[filtered_cars['model'] == model]

    # Scatter plot
    plt.scatter(model_data['cleaned_mileage'], model_data['price'],
                alpha=0.6, color=colors[i], edgecolors='white', s=100, label=f"{model} (Data)")

    # Trendline and Depreciation Calculation
    try:
        # z[0] is the slope (change in price per km), z[1] is the intercept (starting price at 0 km)
        z = np.polyfit(model_data['cleaned_mileage'], model_data['price'], 1)
        p = np.poly1d(z)

        m, c = z[0], z[1]

        # Calculating how much value is lost every 100,000 km
        if c > 0:
            rm_lost_per_100k = abs(m) * 100000
            pct_lost_per_100k = (rm_lost_per_100k / c) * 100
            trend_label = f"{model} Trend (-{pct_lost_per_100k:.1f}% per 100k km)"
        else:
            trend_label = f"{model} Trend"

        plt.plot(model_data['cleaned_mileage'], p(model_data['cleaned_mileage']),
                 color=colors[i], linewidth=4, linestyle='-', label=trend_label)
    except Exception as e:
        print(f"Could not calculate trend for {model}: {e}")

plt.title('Price Depreciation by Mileage (Top 3 Perodua Models)', fontsize=24, fontweight='bold', pad=20)
plt.xlabel('Mileage (km)', fontsize=18)
plt.ylabel('Price (RM)', fontsize=18)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

ax = plt.gca()
ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.ylim(bottom=0)

plt.legend(fontsize=14, loc='upper right', bbox_to_anchor=(1.25, 1))
plt.tight_layout()

plt.savefig(os.path.join(output_dir, '02_mileage_vs_price.png'), dpi=dpi_setting, bbox_inches='tight')
plt.show()