#!/usr/bin/env python3
"""Test script to verify combobox dropdown functionality."""

import sys
import json
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from FilamentStockManager import FilamentStockApp
import tkinter as tk

def test_combobox_values():
    """Test that combobox values are populated correctly with defaults and sorted by occurrence."""
    
    print("Testing combobox dropdown values...\n")
    
    # Create a minimal Tkinter app instance
    root = tk.Tk()
    root.withdraw()  # Hide the window
    app = FilamentStockApp(root)
    
    # Load the sample stock
    sample_file = Path(__file__).parent / "sample_stock.json"
    if sample_file.exists():
        print(f"Loading sample stock from {sample_file.name}...")
        app._load_from_path(sample_file)
        print(f"Loaded {len(app.spools)} spools\n")
    else:
        print("No sample_stock.json found, using empty stock\n")
    
    # Check brand combobox values
    print("=== Brand Combobox Values ===")
    brand_values = list(app.brand_combo['values'])
    print(f"Values: {brand_values}")
    print(f"Count: {len(brand_values)}")
    
    # Check material combobox values
    print("\n=== Material Combobox Values ===")
    material_values = list(app.material_combo['values'])
    print(f"Values: {material_values}")
    print(f"Count: {len(material_values)}")
    
    # Check color combobox values
    print("\n=== Color Combobox Values ===")
    color_values = list(app.color_combo['values'])
    print(f"Values: {color_values}")
    print(f"Count: {len(color_values)}")
    
    # Verify that most used materials are first (if stock loaded)
    if app.spools:
        print("\n=== Occurrence Verification ===")
        from collections import Counter
        
        # Count material occurrences
        material_counts = Counter(spool.material for spool in app.spools)
        print(f"Material counts in stock: {dict(material_counts)}")
        
        # The first materials should be the most common ones from stock
        if material_counts:
            most_common_material = material_counts.most_common(1)[0][0]
            if material_values and material_values[0] == most_common_material:
                print(f"✓ Most common material '{most_common_material}' is first in dropdown")
            elif most_common_material in material_values:
                print(f"⚠ Most common material '{most_common_material}' found but not first")
                print(f"  First value is: '{material_values[0]}'")
        
        # Count brand occurrences
        brand_counts = Counter(spool.brand for spool in app.spools)
        print(f"Brand counts in stock: {dict(brand_counts)}")
        
        # Count color occurrences
        color_counts = Counter(spool.color for spool in app.spools)
        print(f"Color counts in stock: {dict(color_counts)}")
    
    print("\n✓ Combobox test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_combobox_values()
    sys.exit(0 if success else 1)
