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

sold.to_csv('CRMLSSold_Combined.csv', index=False)
print(f"\nSaved CRMLSSold_Combined.csv — {len(sold)} rows")