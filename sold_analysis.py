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

# ── MORTGAGE RATE ENRICHMENT ───────────────────────────────────────────────────

# Step 1 — Fetch the MORTGAGE30US series directly from FRED (no API key required)
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']
print(f"Fetched {len(mortgage)} weekly mortgage rate observations from FRED")

# Step 2 — Resample weekly rates to monthly averages
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean().reset_index()
)
print(f"Resampled to {len(mortgage_monthly)} monthly averages")

# Step 3 — Create a matching year_month key on the sold dataset
# Keying off CloseDate since this is the sold dataset
sold['year_month'] = pd.to_datetime(sold['CloseDate']).dt.to_period('M')

# Step 4 — Merge mortgage rates onto sold dataset
sold_with_rates = sold.merge(mortgage_monthly, on='year_month', how='left')
print(f"\nSold dataset rows before merge: {len(sold)}")
print(f"Sold dataset rows after merge: {len(sold_with_rates)}")

# Step 5 — Validate the merge (rate should not be null for any row)
null_count = sold_with_rates['rate_30yr_fixed'].isnull().sum()
print(f"Null rate values after merge: {null_count}")
if null_count == 0:
    print("Validation passed — all rows have a mortgage rate!")
else:
    print("Warning — some rows are missing a mortgage rate, investigate!")

# Preview
print("\nSample of merged data:")
print(sold_with_rates[['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']].head())

# Save enriched sold dataset
sold_with_rates.to_csv('CRMLSSold_Combined.csv', index=False)
print(f"\nSaved enriched CRMLSSold_Combined.csv — {len(sold_with_rates)} rows")

# =============================================================================
# WEEKS 4-5 — DATA CLEANING 
# =============================================================================

# Before row count
print(f"Row count before cleaning: {len(sold):,}")

# 1. Convert date fields to datetime format
# Date fields are read as text (object) by default — must convert for date math
sold['CloseDate'] = pd.to_datetime(sold['CloseDate'])
sold['PurchaseContractDate'] = pd.to_datetime(sold['PurchaseContractDate'])
sold['ListingContractDate'] = pd.to_datetime(sold['ListingContractDate'])
sold['ContractStatusChangeDate'] = pd.to_datetime(sold['ContractStatusChangeDate'])

# Confirm conversion
print("\nDate field types after conversion:")
print(sold[['CloseDate', 'PurchaseContractDate',
            'ListingContractDate', 'ContractStatusChangeDate']].dtypes)

# 2. Remove unnecessary or redundant columns
# Dropping all columns flagged as >90% missing in Weeks 2-3
# These columns are empty across all records and carry no analytical value
columns_to_drop = high_missing.index.tolist()
sold_clean = sold.drop(columns=columns_to_drop)

print(f"\nShape before dropping high-missing columns: {sold.shape}")
print(f"Shape after dropping high-missing columns: {sold_clean.shape}")
print(f"Columns dropped: {columns_to_drop}")

# 3. Flag invalid numeric values
# Flagging rather than deleting to preserve raw records for reference
# ClosePrice <= 0: a home cannot sell for zero or negative dollars
sold_clean['invalid_close_price'] = sold_clean['ClosePrice'] <= 0
# LivingArea <= 0: a home cannot have zero or negative square footage
sold_clean['invalid_living_area'] = sold_clean['LivingArea'] <= 0
# DaysOnMarket < 0: a home cannot sell before it is listed
sold_clean['invalid_days_on_market'] = sold_clean['DaysOnMarket'] < 0
# Negative bedrooms/bathrooms: physically impossible
sold_clean['invalid_bedrooms'] = sold_clean['BedroomsTotal'] < 0
sold_clean['invalid_bathrooms'] = sold_clean['BathroomsTotalInteger'] < 0

print("\nInvalid numeric value counts:")
print(f"  ClosePrice <= 0:         {sold_clean['invalid_close_price'].sum():,}")
print(f"  LivingArea <= 0:         {sold_clean['invalid_living_area'].sum():,}")
print(f"  DaysOnMarket < 0:        {sold_clean['invalid_days_on_market'].sum():,}")
print(f"  Negative Bedrooms:       {sold_clean['invalid_bedrooms'].sum():,}")
print(f"  Negative Bathrooms:      {sold_clean['invalid_bathrooms'].sum():,}")

# 4. Date consistency checks
# ListingContractDate should precede PurchaseContractDate which should precede CloseDate
# Flagging violations as boolean columns for filtering in later analysis

# Close date comes before listing date — logically impossible
sold_clean['listing_after_close_flag'] = sold_clean['CloseDate'] < sold_clean['ListingContractDate']
# Close date comes before purchase contract date — logically impossible
sold_clean['purchase_after_close_flag'] = sold_clean['CloseDate'] < sold_clean['PurchaseContractDate']
# Purchase contract date comes before listing date — logically impossible
sold_clean['negative_timeline_flag'] = sold_clean['PurchaseContractDate'] < sold_clean['ListingContractDate']

print("\nDate consistency flag counts:")
print(f"  listing_after_close_flag:   {sold_clean['listing_after_close_flag'].sum():,}")
print(f"  purchase_after_close_flag:  {sold_clean['purchase_after_close_flag'].sum():,}")
print(f"  negative_timeline_flag:     {sold_clean['negative_timeline_flag'].sum():,}")

# 5. Geographic data checks
# California bounding box: Latitude 32.5-42.0, Longitude -124.5 to -114.0
# Missing coordinates — record has no lat/long at all
sold_clean['missing_coords_flag'] = (
    sold_clean['Latitude'].isnull() | sold_clean['Longitude'].isnull()
)
# Zero coordinates — sentinel null values (0,0 is in the Atlantic Ocean)
sold_clean['zero_coords_flag'] = (
    (sold_clean['Latitude'] == 0) | (sold_clean['Longitude'] == 0)
)
# Positive longitude — all California coordinates should be negative
sold_clean['positive_longitude_flag'] = sold_clean['Longitude'] > 0
# Out of state — coordinates fall outside California bounding box
sold_clean['out_of_state_flag'] = (
    (sold_clean['Latitude'] < 32.5) | (sold_clean['Latitude'] > 42.0) |
    (sold_clean['Longitude'] < -124.5) | (sold_clean['Longitude'] > -114.0)
) & ~sold_clean['missing_coords_flag']

print("\nGeographic data quality summary:")
print(f"  Missing coordinates:        {sold_clean['missing_coords_flag'].sum():,}")
print(f"  Zero coordinates:           {sold_clean['zero_coords_flag'].sum():,}")
print(f"  Positive longitude (error): {sold_clean['positive_longitude_flag'].sum():,}")
print(f"  Out of state/implausible:   {sold_clean['out_of_state_flag'].sum():,}")

# 6. Full data quality summary
print("\nFULL DATA QUALITY SUMMARY:")
print(f"  Total records: {len(sold_clean):,}")
print(f"\n  -- Invalid Numeric Values --")
print(f"  ClosePrice <= 0:            {sold_clean['invalid_close_price'].sum():,}")
print(f"  LivingArea <= 0:            {sold_clean['invalid_living_area'].sum():,}")
print(f"  DaysOnMarket < 0:           {sold_clean['invalid_days_on_market'].sum():,}")
print(f"\n  -- Date Consistency --")
print(f"  listing_after_close_flag:   {sold_clean['listing_after_close_flag'].sum():,}")
print(f"  purchase_after_close_flag:  {sold_clean['purchase_after_close_flag'].sum():,}")
print(f"  negative_timeline_flag:     {sold_clean['negative_timeline_flag'].sum():,}")
print(f"\n  -- Geographic --")
print(f"  Missing coordinates:        {sold_clean['missing_coords_flag'].sum():,}")
print(f"  Zero coordinates:           {sold_clean['zero_coords_flag'].sum():,}")
print(f"  Positive longitude:         {sold_clean['positive_longitude_flag'].sum():,}")
print(f"  Out of state:               {sold_clean['out_of_state_flag'].sum():,}")

# After row count — rows are flagged not removed, count should match
print(f"\nRow count after cleaning: {len(sold_clean):,}")
print(f"Columns before: {sold.shape[1]} | Columns after: {sold_clean.shape[1]}")

# =============================================================================
# WEEK 6 — FEATURE ENGINEERING (coming soon)
# =============================================================================


# =============================================================================
# WEEK 7 — OUTLIER DETECTION (coming soon)
# =============================================================================


# =============================================================================
# FINAL OUTPUT — Save clean CSV for Tableau
# =============================================================================

sold_clean.to_csv('CRMLSSold_Cleaned.csv', index=False)
print(f"\nSaved CRMLSSold_Cleaned.csv — {len(sold_clean):,} rows, {sold_clean.shape[1]} columns")