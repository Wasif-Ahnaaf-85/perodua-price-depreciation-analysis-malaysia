import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Connect & Extract
load_dotenv()
db_pass = os.getenv('MYSQL_PASSWORD')
engine = create_engine(f"mysql+pymysql://root:{db_pass}@localhost/malaysia_car_market_db")
df = pd.read_sql("SELECT year, price, model FROM clean_car_listings;", con=engine)

# Data Prep & Filtering
df = df.dropna(subset=['year', 'price', 'model'])
df['model'] = df['model'].str.title()
top_5_models = df['model'].value_counts().nlargest(5).index.tolist()

summary_data = []

for model in top_5_models:
    model_df = df[df['model'] == model]

    max_yr, min_yr = model_df['year'].max(), model_df['year'].min()
    p_newest = model_df[model_df['year'] == max_yr]['price'].mean()
    p_oldest = model_df[model_df['year'] == min_yr]['price'].mean()

    age_gap = max_yr - min_yr

    if age_gap > 0:
        total_rm_drop = p_newest - p_oldest
        annual_rm_drop = total_rm_drop / age_gap

        total_pct_drop = (total_rm_drop / p_newest) * 100
        annual_pct_drop = total_pct_drop / age_gap

        summary_data.append({
            'Model': model,
            'Years (Age Gap)': age_gap,  # RENAMED HERE
            'Price (New)': p_newest,
            'Annual Drop (RM)': annual_rm_drop,
            'Annual Drop (%)': annual_pct_drop
        })

summary_df = pd.DataFrame(summary_data).sort_values('Annual Drop (RM)', ascending=False)

# --- Visualization ---
plt.figure(figsize=(16, 9))
sns.set_style("whitegrid")

ax = sns.barplot(data=summary_df, hue='Model', y='Annual Drop (RM)', palette='magma', legend=False)

for i, p in enumerate(ax.patches):
    rm_val = summary_df.iloc[i]['Annual Drop (RM)']
    pct_val = summary_df.iloc[i]['Annual Drop (%)']

    ax.annotate(f"RM {rm_val:,.0f}/yr\n({pct_val:.1f}% /yr)",
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 20),
                textcoords='offset points', fontsize=12, fontweight='bold')

plt.title('Annual Price Depreciation', fontsize=24, fontweight='bold', pad=30)
plt.ylabel('Average Loss Per Year (RM)', fontsize=16)
plt.xlabel('Car Model', fontsize=16)
plt.ylim(0, summary_df['Annual Drop (RM)'].max() * 1.3)
sns.despine()

output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
os.makedirs(output_dir, exist_ok=True)
plt.savefig(os.path.join(output_dir, '05_depreciation_summary_plot.png'), dpi=100, bbox_inches='tight')

display_df = summary_df.copy()
display_df['Annual Drop (RM)'] = display_df['Annual Drop (RM)'].apply(lambda x: f"RM {x:,.0f}")
display_df['Annual Drop (%)'] = display_df['Annual Drop (%)'].apply(lambda x: f"{x:.2f}%")

print("\n" + "=" * 60)
print(" FINAL DEPRECIATION SUMMARY (Segmented by Model History) ")
print("=" * 60)
print(display_df[['Model', 'Years (Age Gap)', 'Annual Drop (RM)', 'Annual Drop (%)']].to_string(index=False))

plt.show()