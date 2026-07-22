#!/usr/bin/env python
import sys
import os
sys.path.insert(0, r'c:\Users\wb661551\OneDrive - WBG\Desktop\Internship\poorest_decile\replication_excercise')

# Test basic imports
try:
    import pandas as pd
    print("✓ pandas imported")
    
    import matplotlib.pyplot as plt
    print("✓ matplotlib imported")
    
    # Test reading the output CSV
    csv_path = r'c:\Users\wb661551\OneDrive - WBG\Desktop\Internship\poorest_decile\replication_excercise\bottom10percent_output.csv'
    df = pd.read_csv(csv_path)
    print(f"✓ CSV loaded: {len(df)} rows, {len(df.columns)} columns")
    print(f"  Deciles in data: {sorted(df['decile'].unique())}")
    
    # Test that colors are defined for all deciles
    deciles = sorted(df['decile'].unique())
    from bottom10percent_from_daniel import DECILE_COLORS, TARGET_DECILES
    print(f"✓ TARGET_DECILES: {TARGET_DECILES}")
    for d in deciles:
        if d in DECILE_COLORS:
            print(f"  Decile {d}: color {DECILE_COLORS[d]}")
        else:
            print(f"  ✗ Decile {d}: NO COLOR DEFINED")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
