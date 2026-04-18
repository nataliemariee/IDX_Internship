import pandas as pd

# =============================================================================
# WEEK 1 — SOLD DATASET CONCATENATION
# =============================================================================

# Load all monthly sold files (January 2024 through March 2026)
sold_files = [
    'CRMLSSold202401.csv', 'CRMLSSold202402.csv', 'CRMLSSold202403.csv',
    'CRMLSSold202404.csv', 'CRMLSSold202405.csv', 'CRMLSSold202406.csv',
    'CRMLSSold202407.csv', 'CRMLSSold202408.csv', 'CRMLSSold202409.csv',
    'CRMLSSold202410.csv', 'CRMLSSold202411.csv', 'CRMLSSold202412.csv',
    'CRMLSSold202501.csv', 'CRMLSSold202502.csv', 'CRMLSSold202503.csv',
    'CRMLSSold202504.csv', 'CRMLSSold202505.csv', 'CRMLSSold202506.csv',
    'CRMLSSold202507.csv', 'CRMLSSold202508.csv', 'CRMLSSold202509.csv',
    'CRMLSSold202510.csv', 'CRMLSSold202511.csv', 'CRMLSSold202512.csv',
    'CRMLSSold202601.csv', 'CRMLSSold202602.csv', 'CRMLSSold202603.csv'
]

# Load each file and concatenate into one combined dataset
sold_dfs = []
for file in sold_files:
    df = pd.read_csv(file, low_memory=False)
    sold_dfs.append(df)
    print(f"Loaded {file}: {len(df)} rows")

sold = pd.concat(sold_dfs, ignore_index=True)

# Row count BEFORE Residential filter
print(f"\nSOLD - Total rows after concatenation (all property types): {len(sold)}")

# Filter to Residential only
sold = sold[sold['PropertyType'] == 'Residential']

# Row count AFTER Residential filter
print(f"SOLD - Total rows after Residential filter: {len(sold)}")

# =============================================================================
# WEEKS 2-3 — EDA & VALIDATION
# =============================================================================

import matplotlib.pyplot as plt

# ── DATASET UNDERSTANDING ─────────────────────────────────────────────────────

# Shape: rows and columns
print(f"SOLD dataset shape: {sold.shape}")

# Column data types
print("\nColumn data types:")
print(sold.dtypes.to_string())

# ── MISSING VALUE ANALYSIS ────────────────────────────────────────────────────

# Calculate missing counts and percentages per column
missing = pd.DataFrame({
    'missing_count': sold.isnull().sum(),
    'missing_pct': (sold.isnull().sum() / len(sold) * 100).round(2)
})
missing = missing.sort_values('missing_pct', ascending=False)

print("\nMissing value report (all columns):")
print(missing.to_string())

# Flag columns above 90% missing
high_missing = missing[missing['missing_pct'] > 90]
print(f"\nColumns with >90% missing values ({len(high_missing)} total):")
print(high_missing.to_string())

# ── NUMERIC DISTRIBUTION SUMMARY ─────────────────────────────────────────────

numeric_fields = ['ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea',
                  'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger',
                  'DaysOnMarket', 'YearBuilt']

print("\nNumeric distribution summary:")
print(sold[numeric_fields].describe(percentiles=[.10, .25, .50, .75, .90, .95, .99]).to_string())

# Histograms for all numeric fields
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
fig.suptitle('Numeric Field Distributions - Sold Dataset', fontsize=16)

for i, field in enumerate(numeric_fields):
    ax = axes[i//3, i%3]
    sold[field].dropna().plot(kind='hist', bins=50, ax=ax, color='steelblue', edgecolor='white')
    ax.set_title(field)

plt.tight_layout()
plt.savefig('sold_distributions.png')
print("\nSaved sold_distributions.png")

# ── SUGGESTED INTERN QUESTIONS ────────────────────────────────────────────────

# Median and average close prices
print(f"\nMedian close price: ${sold['ClosePrice'].median():,.0f}")
print(f"Average close price: ${sold['ClosePrice'].mean():,.0f}")

# Homes sold above vs below list price
sold['sold_above_list'] = sold['ClosePrice'] >= sold['ListPrice']
pct_above = sold['sold_above_list'].mean() * 100
print(f"\nHomes sold at or above list price: {pct_above:.1f}%")
print(f"Homes sold below list price: {100 - pct_above:.1f}%")

# Top 10 counties by median close price
print("\nTop 10 counties by median close price:")
print(sold.groupby('CountyOrParish')['ClosePrice'].median()
      .sort_values(ascending=False).head(10)
      .apply(lambda x: f"${x:,.0f}"))

# Days on market distribution
print(f"\nDays on Market median: {sold['DaysOnMarket'].median():.0f} days")
print(f"Days on Market average: {sold['DaysOnMarket'].mean():.1f} days")
print(f"Negative DaysOnMarket (bad data): {(sold['DaysOnMarket'] < 0).sum()}")
print(f"DaysOnMarket over 365: {(sold['DaysOnMarket'] > 365).sum()}")

# ── DATE CONSISTENCY CHECKS ───────────────────────────────────────────────────

# Convert date fields from text to datetime
sold['CloseDate'] = pd.to_datetime(sold['CloseDate'])
sold['ListingContractDate'] = pd.to_datetime(sold['ListingContractDate'])
sold['PurchaseContractDate'] = pd.to_datetime(sold['PurchaseContractDate'])

# Flag date consistency violations
sold['listing_after_close_flag'] = sold['CloseDate'] < sold['ListingContractDate']
sold['purchase_after_close_flag'] = sold['CloseDate'] < sold['PurchaseContractDate']

print(f"\nClose date before listing date: {sold['listing_after_close_flag'].sum()}")
print(f"Close date before purchase contract date: {sold['purchase_after_close_flag'].sum()}")

# ── PROPERTY TYPE BREAKDOWN ───────────────────────────────────────────────────

# Load a single raw monthly file to show property type share before filtering
sample = pd.read_csv('CRMLSSold202603.csv', low_memory=False)
print("\nProperty type breakdown (sample from March 2026):")
print(sample['PropertyType'].value_counts())
print(f"\nResidential share: {sample['PropertyType'].value_counts(normalize=True).get('Residential', 0)*100:.1f}%")

# =============================================================================
# WEEKS 4-5 — DATA CLEANING (coming soon)
# =============================================================================


# =============================================================================
# WEEK 6 — FEATURE ENGINEERING (coming soon)
# =============================================================================


# =============================================================================
# WEEK 7 — OUTLIER DETECTION (coming soon)
# =============================================================================


# =============================================================================
# FINAL OUTPUT — Save clean CSV for Tableau
# =============================================================================

sold.to_csv('CRMLSSold_Combined.csv', index=False)
print(f"\nSaved CRMLSSold_Combined.csv — {len(sold)} rows")