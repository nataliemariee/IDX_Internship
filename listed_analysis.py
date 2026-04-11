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
# WEEKS 2-3 — EDA & VALIDATION (coming soon)
# =============================================================================


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