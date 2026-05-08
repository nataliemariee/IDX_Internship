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

# Step 3 — Create a matching year_month key on the listings dataset
# Keying off ListingContractDate since this is the listings dataset
listings['year_month'] = pd.to_datetime(listings['ListingContractDate']).dt.to_period('M')

# Step 4 — Merge mortgage rates onto listings dataset
listings_with_rates = listings.merge(mortgage_monthly, on='year_month', how='left')
print(f"\nListings dataset rows before merge: {len(listings)}")
print(f"Listings dataset rows after merge: {len(listings_with_rates)}")

# Step 5 — Validate the merge (rate should not be null for any row)
null_count = listings_with_rates['rate_30yr_fixed'].isnull().sum()
print(f"Null rate values after merge: {null_count}")
if null_count == 0:
    print("Validation passed — all rows have a mortgage rate!")
else:
    print("Warning — some rows are missing a mortgage rate, investigate!")

# Preview
print("\nSample of merged data:")
print(listings_with_rates[['ListingContractDate', 'year_month', 'ListPrice', 'rate_30yr_fixed']].head())

# Save enriched listings dataset
listings_with_rates.to_csv('CRMLSListing_Combined.csv', index=False)
print(f"\nSaved enriched CRMLSListing_Combined.csv — {len(listings_with_rates)} rows")


# =============================================================================
# WEEKS 4-5 — DATA CLEANING (coming soon)
# =============================================================================

# =============================================================================
# WEEKS 4-5 — DATA CLEANING AND PREPARATION
# =============================================================================

# Before row count
print(f"Row count before cleaning: {len(listings):,}")

# 1. Convert date fields to datetime format
# Date fields are read as text (object) by default — must convert for date math
listings['CloseDate'] = pd.to_datetime(listings['CloseDate'])
listings['PurchaseContractDate'] = pd.to_datetime(listings['PurchaseContractDate'])
listings['ListingContractDate'] = pd.to_datetime(listings['ListingContractDate'])
listings['ContractStatusChangeDate'] = pd.to_datetime(listings['ContractStatusChangeDate'])

# Confirm conversion
print("\nDate field types after conversion:")
print(listings[['CloseDate', 'PurchaseContractDate',
                 'ListingContractDate', 'ContractStatusChangeDate']].dtypes)

# 2. Remove unnecessary or redundant columns
# Dropping all columns flagged as >90% missing in Weeks 2-3
# These columns are empty across all records and carry no analytical value
columns_to_drop = high_missing.index.tolist()
listings_clean = listings.drop(columns=columns_to_drop, errors='ignore')

print(f"\nShape before dropping high-missing columns: {listings.shape}")
print(f"Shape after dropping high-missing columns: {listings_clean.shape}")
print(f"Columns dropped: {columns_to_drop}")

# 3. Flag invalid numeric values
# Flagging rather than deleting to preserve raw records for reference
# ListPrice <= 0: a home cannot be listed for zero or negative dollars
listings_clean['invalid_list_price'] = listings_clean['ListPrice'] <= 0
# LivingArea <= 0: a home cannot have zero or negative square footage
listings_clean['invalid_living_area'] = listings_clean['LivingArea'] <= 0
# DaysOnMarket < 0: a home cannot sell before it is listed
listings_clean['invalid_days_on_market'] = listings_clean['DaysOnMarket'] < 0
# Negative bedrooms/bathrooms: physically impossible
listings_clean['invalid_bedrooms'] = listings_clean['BedroomsTotal'] < 0
listings_clean['invalid_bathrooms'] = listings_clean['BathroomsTotalInteger'] < 0

print("\nInvalid numeric value counts:")
print(f"  ListPrice <= 0:          {listings_clean['invalid_list_price'].sum():,}")
print(f"  LivingArea <= 0:         {listings_clean['invalid_living_area'].sum():,}")
print(f"  DaysOnMarket < 0:        {listings_clean['invalid_days_on_market'].sum():,}")
print(f"  Negative Bedrooms:       {listings_clean['invalid_bedrooms'].sum():,}")
print(f"  Negative Bathrooms:      {listings_clean['invalid_bathrooms'].sum():,}")

# 4. Date consistency checks
# ListingContractDate should precede PurchaseContractDate which should precede CloseDate
# Flagging violations as boolean columns for filtering in later analysis

# Close date comes before listing date — logically impossible
listings_clean['listing_after_close_flag'] = listings_clean['CloseDate'] < listings_clean['ListingContractDate']
# Close date comes before purchase contract date — logically impossible
listings_clean['purchase_after_close_flag'] = listings_clean['CloseDate'] < listings_clean['PurchaseContractDate']
# Purchase contract date comes before listing date — logically impossible
listings_clean['negative_timeline_flag'] = listings_clean['PurchaseContractDate'] < listings_clean['ListingContractDate']

print("\nDate consistency flag counts:")
print(f"  listing_after_close_flag:   {listings_clean['listing_after_close_flag'].sum():,}")
print(f"  purchase_after_close_flag:  {listings_clean['purchase_after_close_flag'].sum():,}")
print(f"  negative_timeline_flag:     {listings_clean['negative_timeline_flag'].sum():,}")

# 5. Geographic data checks
# California bounding box: Latitude 32.5-42.0, Longitude -124.5 to -114.0
# Missing coordinates — record has no lat/long at all
listings_clean['missing_coords_flag'] = (
    listings_clean['Latitude'].isnull() | listings_clean['Longitude'].isnull()
)
# Zero coordinates — sentinel null values (0,0 is in the Atlantic Ocean)
listings_clean['zero_coords_flag'] = (
    (listings_clean['Latitude'] == 0) | (listings_clean['Longitude'] == 0)
)
# Positive longitude — all California coordinates should be negative
listings_clean['positive_longitude_flag'] = listings_clean['Longitude'] > 0
# Out of state — coordinates fall outside California bounding box
listings_clean['out_of_state_flag'] = (
    (listings_clean['Latitude'] < 32.5) | (listings_clean['Latitude'] > 42.0) |
    (listings_clean['Longitude'] < -124.5) | (listings_clean['Longitude'] > -114.0)
) & ~listings_clean['missing_coords_flag']

print("\nGeographic data quality summary:")
print(f"  Missing coordinates:        {listings_clean['missing_coords_flag'].sum():,}")
print(f"  Zero coordinates:           {listings_clean['zero_coords_flag'].sum():,}")
print(f"  Positive longitude (error): {listings_clean['positive_longitude_flag'].sum():,}")
print(f"  Out of state/implausible:   {listings_clean['out_of_state_flag'].sum():,}")

# 6. Full data quality summary
print("\nFULL DATA QUALITY SUMMARY:")
print(f"  Total records: {len(listings_clean):,}")
print(f"\n  -- Invalid Numeric Values --")
print(f"  ListPrice <= 0:             {listings_clean['invalid_list_price'].sum():,}")
print(f"  LivingArea <= 0:            {listings_clean['invalid_living_area'].sum():,}")
print(f"  DaysOnMarket < 0:           {listings_clean['invalid_days_on_market'].sum():,}")
print(f"\n  -- Date Consistency --")
print(f"  listing_after_close_flag:   {listings_clean['listing_after_close_flag'].sum():,}")
print(f"  purchase_after_close_flag:  {listings_clean['purchase_after_close_flag'].sum():,}")
print(f"  negative_timeline_flag:     {listings_clean['negative_timeline_flag'].sum():,}")
print(f"\n  -- Geographic --")
print(f"  Missing coordinates:        {listings_clean['missing_coords_flag'].sum():,}")
print(f"  Zero coordinates:           {listings_clean['zero_coords_flag'].sum():,}")
print(f"  Positive longitude:         {listings_clean['positive_longitude_flag'].sum():,}")
print(f"  Out of state:               {listings_clean['out_of_state_flag'].sum():,}")

# After row count
print(f"\nRow count after cleaning: {len(listings_clean):,}")
print(f"Columns before: {listings.shape[1]} | Columns after: {listings_clean.shape[1]}")

# =============================================================================
# WEEK 6 — FEATURE ENGINEERING (coming soon)
# =============================================================================


# =============================================================================
# WEEK 7 — OUTLIER DETECTION (coming soon)
# =============================================================================


# =============================================================================
# FINAL OUTPUT — Save clean CSV for Tableau
# =============================================================================

listings_clean.to_csv('CRMLSListing_Cleaned.csv', index=False)
print(f"\nSaved CRMLSListing_Cleaned.csv — {len(listings_clean):,} rows, {listings_clean.shape[1]} columns")