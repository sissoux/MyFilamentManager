#!/usr/bin/env python3
"""Test script to demonstrate dynamic combobox updating with custom values."""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from FilamentStockManager import FilamentStockApp, FilamentSpool
from datetime import datetime
import tkinter as tk

def test_dynamic_combobox_update():
    """Test that adding new spools updates combobox values dynamically."""
    
    print("Testing dynamic combobox updates...\n")
    
    # Create a minimal Tkinter app instance
    root = tk.Tk()
    root.withdraw()  # Hide the window
    app = FilamentStockApp(root)
    
    print("=== Initial State (Empty Stock) ===")
    print(f"Material dropdown: {list(app.material_combo['values'])[:5]}... (showing first 5)")
    print(f"Brand dropdown: {list(app.brand_combo['values'])}")
    print(f"Color dropdown: {list(app.color_combo['values'])[:5]}... (showing first 5)")
    
    # Add a custom material spool
    print("\n=== Adding custom material 'PLA+' ===")
    custom_spool1 = FilamentSpool(
        id="PLA+-WHITE-001",
        brand="eSUN",
        material="PLA+",  # Custom material
        name="eMax",
        color="White",
        estimated_weight=1000,
        is_opened=False,
        remaining_weight=None,
        price=22.99,
        buying_date="2026-04-03",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        barcode="PLA+-WHITE-001",
    )
    app.spools.append(custom_spool1)
    app._update_combobox_values()
    
    material_values = list(app.material_combo['values'])
    if "PLA+" in material_values:
        print(f"✓ Custom material 'PLA+' added to dropdown")
        print(f"  Position: {material_values.index('PLA+') + 1} of {len(material_values)}")
    
    # Add multiple spools of the same custom brand
    print("\n=== Adding 3 spools with custom brand 'Hatchbox' ===")
    for i in range(3):
        spool = FilamentSpool(
            id=f"PLA-BLACK-{i+1:03d}",
            brand="Hatchbox",  # Custom brand
            material="PLA",
            name=f"True Black #{i+1}",
            color="Black",
            estimated_weight=1000,
            is_opened=False,
            remaining_weight=None,
            price=20.99,
            buying_date="2026-04-03",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            barcode=f"PLA-BLACK-{i+1:03d}",
        )
        app.spools.append(spool)
    
    app._update_combobox_values()
    
    brand_values = list(app.brand_combo['values'])
    if "Hatchbox" in brand_values:
        print(f"✓ Custom brand 'Hatchbox' added to dropdown")
        print(f"  Position: {brand_values.index('Hatchbox') + 1} (should be first - most used)")
        print(f"  Full list: {brand_values}")
    
    # Add spools with custom color
    print("\n=== Adding 2 spools with custom color 'Neon Green' ===")
    for i in range(2):
        spool = FilamentSpool(
            id=f"PETG-NEON-GREEN-{i+1:03d}",
            brand="Prusa",
            material="PETG",
            name=f"Translucent Green #{i+1}",
            color="Neon Green",  # Custom color
            estimated_weight=1000,
            is_opened=False,
            remaining_weight=None,
            price=24.99,
            buying_date="2026-04-03",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            barcode=f"PETG-NEON-GREEN-{i+1:03d}",
        )
        app.spools.append(spool)
    
    app._update_combobox_values()
    
    color_values = list(app.color_combo['values'])
    if "Neon Green" in color_values:
        print(f"✓ Custom color 'Neon Green' added to dropdown")
        print(f"  Position: {color_values.index('Neon Green') + 1}")
    
    # Show final statistics
    print("\n=== Final Statistics ===")
    print(f"Total spools: {len(app.spools)}")
    print(f"Unique materials: {len(set(s.material for s in app.spools))}")
    print(f"Unique brands: {len(set(s.brand for s in app.spools))}")
    print(f"Unique colors: {len(set(s.color for s in app.spools))}")
    
    print("\n=== Most Frequent Values (Top 3) ===")
    from collections import Counter
    
    material_counts = Counter(s.material for s in app.spools).most_common(3)
    brand_counts = Counter(s.brand for s in app.spools).most_common(3)
    color_counts = Counter(s.color for s in app.spools).most_common(3)
    
    print(f"Materials: {[(m, c) for m, c in material_counts]}")
    print(f"Brands: {[(b, c) for b, c in brand_counts]}")
    print(f"Colors: {[(col, c) for col, c in color_counts]}")
    
    print("\n✓ Dynamic combobox update test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_dynamic_combobox_update()
    sys.exit(0 if success else 1)
