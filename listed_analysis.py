import pandas as pd

# =============================================================================
# WEEK 1 — LISTINGS DATASET CONCATENATION
# =============================================================================

# Load all monthly listing files (January 2024 through March 2026)
listings_files = [
    'CRMLSListing202401.csv', 'CRMLSListing202402.csv', 'CRMLSListing202403.csv',
    'CRMLSListing202404.csv', 'CRMLSListing202405.csv', 'CRMLSListing202406.csv',
    'CRMLSListing202407.csv', 'CRMLSListing202408.csv', 'CRMLSListing202409.csv',
    'CRMLSListing202410.csv', 'CRMLSListing202411.csv', 'CRMLSListing202412.csv',
    'CRMLSListing202501.csv', 'CRMLSListing202502.csv', 'CRMLSListing202503.csv',
    'CRMLSListing202504.csv', 'CRMLSListing202505.csv', 'CRMLSListing202506.csv',
    'CRMLSListing202507.csv', 'CRMLSListing202508.csv', 'CRMLSListing202509.csv',
    'CRMLSListing202510.csv', 'CRMLSListing202511.csv', 'CRMLSListing202512.csv',
    'CRMLSListing202601.csv', 'CRMLSListing202602.csv', 'CRMLSListing202603.csv'
]

# Load each file and concatenate into one combined dataset
listings_dfs = []
for file in listings_files:
    df = pd.read_csv(file, low_memory=False)
    listings_dfs.append(df)
    print(f"Loaded {file}: {len(df)} rows")

listings = pd.concat(listings_dfs, ignore_index=True)

# Row count BEFORE Residential filter
print(f"\nLISTINGS - Total rows after concatenation (all property types): {len(listings)}")

# Filter to Residential only
listings = listings[listings['PropertyType'] == 'Residential']

# Row count AFTER Residential filter
print(f"LISTINGS - Total rows after Residential filter: {len(listings)}")

# =============================================================================
# WEEKS 2-3 — EDA & VALIDATION
# =============================================================================

import matplotlib.pyplot as plt

# ── DATASET UNDERSTANDING ─────────────────────────────────────────────────────

print(f"LISTINGS dataset shape: {listings.shape}")

print("\nColumn data types:")
print(listings.dtypes.to_string())

# ── MISSING VALUE ANALYSIS ────────────────────────────────────────────────────

missing = pd.DataFrame({
    'missing_count': listings.isnull().sum(),
    'missing_pct': (listings.isnull().sum() / len(listings) * 100).round(2)
})
missing = missing.sort_values('missing_pct', ascending=False)

print("\nMissing value report (all columns):")
print(missing.to_string())

high_missing = missing[missing['missing_pct'] > 90]
print(f"\nColumns with >90% missing values ({len(high_missing)} total):")
print(high_missing.to_string())

# ── NUMERIC DISTRIBUTION SUMMARY ─────────────────────────────────────────────

numeric_fields = ['ListPrice', 'OriginalListPrice', 'LivingArea',
                  'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger',
                  'DaysOnMarket', 'YearBuilt']

print("\nNumeric distribution summary:")
print(listings[numeric_fields].describe(percentiles=[.10, .25, .50, .75, .90, .95, .99]).to_string())

# Histograms
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
fig.suptitle('Numeric Field Distributions - Listings Dataset', fontsize=16)

for i, field in enumerate(numeric_fields):
    ax = axes[i//4, i%4]
    listings[field].dropna().plot(kind='hist', bins=50, ax=ax, color='steelblue', edgecolor='white')
    ax.set_title(field)

plt.tight_layout()
plt.savefig('listings_distributions.png')
print("\nSaved listings_distributions.png")

# ── SUGGESTED INTERN QUESTIONS ────────────────────────────────────────────────

# Median and average list prices
print(f"\nMedian list price: ${listings['ListPrice'].median():,.0f}")
print(f"Average list price: ${listings['ListPrice'].mean():,.0f}")

# Top 10 counties by median list price
print("\nTop 10 counties by median list price:")
print(listings.groupby('CountyOrParish')['ListPrice'].median()
      .sort_values(ascending=False).head(10)
      .apply(lambda x: f"${x:,.0f}"))

# Days on market distribution
print(f"\nDays on Market median: {listings['DaysOnMarket'].median():.0f} days")
print(f"Days on Market average: {listings['DaysOnMarket'].mean():.1f} days")
print(f"Negative DaysOnMarket (bad data): {(listings['DaysOnMarket'] < 0).sum()}")
print(f"DaysOnMarket over 365: {(listings['DaysOnMarket'] > 365).sum()}")

# ── DATE CONSISTENCY CHECKS ───────────────────────────────────────────────────

listings['ListingContractDate'] = pd.to_datetime(listings['ListingContractDate'])
listings['CloseDate'] = pd.to_datetime(listings['CloseDate'])
listings['PurchaseContractDate'] = pd.to_datetime(listings['PurchaseContractDate'])

listings['listing_after_close_flag'] = listings['CloseDate'] < listings['ListingContractDate']
listings['purchase_after_close_flag'] = listings['CloseDate'] < listings['PurchaseContractDate']

print(f"\nClose date before listing date: {listings['listing_after_close_flag'].sum()}")
print(f"Close date before purchase contract date: {listings['purchase_after_close_flag'].sum()}")

# ── PROPERTY TYPE BREAKDOWN ───────────────────────────────────────────────────

sample = pd.read_csv('CRMLSListing202603.csv', low_memory=False)
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

listings.to_csv('CRMLSListing_Combined.csv', index=False)
print(f"\nSaved CRMLSListing_Combined.csv — {len(listings)} rows")