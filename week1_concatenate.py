import pandas as pd
import os

# ── SOLD DATASET ──────────────────────────────────────────────────────────────

# Load all monthly sold files and concatenate them
# Following the handbook's example workflow pattern:
# sold1 = pd.read_csv('CRMLSSold202401.csv')
# sold2 = pd.read_csv('CRMLSSold202402.csv')
# sold = pd.concat([sold1, sold2])
# We automate this across all 27 months using a loop

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

# Load each file into a list of dataframes
sold_dfs = []
for file in sold_files:
    df = pd.read_csv(file, low_memory=False)
    sold_dfs.append(df)
    print(f"Loaded {file}: {len(df)} rows")

# Concatenate all monthly files into one combined dataset
sold = pd.concat(sold_dfs, ignore_index=True)

# Row count BEFORE Residential filter
print(f"\nSOLD - Total rows after concatenation (all property types): {len(sold)}")

# Filter to Residential only
sold = sold[sold['PropertyType'] == 'Residential']

# Row count AFTER Residential filter
print(f"SOLD - Total rows after Residential filter: {len(sold)}")

# Save combined sold dataset
sold.to_csv('CRMLSSold_Combined.csv', index=False)
print(f"Saved CRMLSSold_Combined.csv\n")


# ── LISTINGS DATASET ──────────────────────────────────────────────────────────

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

# Load each file into a list of dataframes
listings_dfs = []
for file in listings_files:
    df = pd.read_csv(file, low_memory=False)
    listings_dfs.append(df)
    print(f"Loaded {file}: {len(df)} rows")

# Concatenate all monthly files into one combined dataset
listings = pd.concat(listings_dfs, ignore_index=True)

# Row count BEFORE Residential filter
print(f"\nLISTINGS - Total rows after concatenation (all property types): {len(listings)}")

# Filter to Residential only
listings = listings[listings['PropertyType'] == 'Residential']

# Row count AFTER Residential filter
print(f"LISTINGS - Total rows after Residential filter: {len(listings)}")

# Save combined listings dataset
listings.to_csv('CRMLSListing_Combined.csv', index=False)
print(f"Saved CRMLSListing_Combined.csv")
