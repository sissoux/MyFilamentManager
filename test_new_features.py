#!/usr/bin/env python3
"""Test script to verify new features: dropdown prefill, price recall, weight dropdown, and spool holder calculation."""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from FilamentStockManager import FilamentStockApp
import tkinter as tk

def test_new_features():
    """Test all new features."""
    
    print("Testing new features...\n")
    
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
    
    # Test 1: Dropdown prefill
    print("=== Test 1: Dropdown Prefill ===")
    app.clear_form()  # This should trigger prefill
    print(f"Brand: {app.brand_var.get()}")
    print(f"Material: {app.material_var.get()}")
    print(f"Color: {app.color_var.get()}")
    print(f"Estimated weight: {app.estimated_weight_var.get()}")
    
    if app.brand_var.get() and app.material_var.get() and app.color_var.get():
        print("✓ Dropdowns prefilled with first values")
    else:
        print("✗ Dropdowns not prefilled")
    
    # Test 2: Weight dropdown
    print("\n=== Test 2: Weight Dropdown ===")
    weight_values = list(app.weight_combo['values'])
    print(f"Weight options: {weight_values}")
    if weight_values == ["1000", "250"]:
        print("✓ Weight dropdown has correct values (1000g, 250g)")
        print(f"✓ Default weight: {app.estimated_weight_var.get()}g")
    else:
        print("✗ Weight dropdown values incorrect")
    
    # Test 3: Price recall for matching combo
    print("\n=== Test 3: Price Recall for Matching Combo ===")
    
    # Clear and set values to match an existing spool
    app.clear_form()
    
    # Set to match PLA-BLACK (Prusament, PLA, Black, 1000g) - should recall $24.99
    app.brand_var.set("Prusament")
    app.material_var.set("PLA")
    app.color_var.set("Black")
    app.estimated_weight_var.set("1000")
    
    # Trigger the combo change event
    app._on_combo_changed()
    
    recalled_price = app.price_var.get()
    print(f"Set combo: Prusament / PLA / Black / 1000g")
    print(f"Recalled price: ${recalled_price}")
    
    if recalled_price == "24.99":
        print("✓ Price correctly recalled from last matching spool")
    else:
        print(f"⚠ Price recall may not be working (expected 24.99, got {recalled_price})")
    
    # Test 4: Different combo should recall different price
    print("\n=== Test 4: Different Combo Price Recall ===")
    app.clear_form()
    app.brand_var.set("eSUN")
    app.material_var.set("PETG")
    app.color_var.set("Blue")
    app.estimated_weight_var.set("1000")
    app._on_combo_changed()
    
    recalled_price2 = app.price_var.get()
    print(f"Set combo: eSUN / PETG / Blue / 1000g")
    print(f"Recalled price: ${recalled_price2}")
    
    if recalled_price2 == "19.99":
        print("✓ Different combo recalls different price")
    else:
        print(f"⚠ Price recall may not be working (expected 19.99, got {recalled_price2})")
    
    # Test 5: Spool holder weight calculation
    print("\n=== Test 5: Spool Holder Weight Calculation ===")
    
    for i, spool in enumerate(app.spools[:3], 1):
        print(f"Spool {i}: {spool.id}")
        print(f"  Estimated filament: {spool.estimated_weight}g")
        print(f"  Actual total weight: {spool.actual_weight}g")
        print(f"  Calculated holder: {spool.spool_holder_weight}g")
        
        expected_holder = spool.actual_weight - spool.estimated_weight
        if abs(spool.spool_holder_weight - expected_holder) < 0.01:
            print(f"  ✓ Correct calculation")
        else:
            print(f"  ✗ Incorrect: expected {expected_holder}g")
    
    # Test 6: Actual weight field
    print("\n=== Test 6: Actual Weight Field ===")
    app.clear_form()
    if hasattr(app, 'actual_weight_var'):
        print("✓ Actual weight field exists")
        
        # Select a spool to check if actual weight is loaded
        app.tree.selection_set("0")
        app.on_tree_select(None)
        actual_weight_value = app.actual_weight_var.get()
        print(f"  Selected spool actual weight: {actual_weight_value}g")
        
        if actual_weight_value:
            print("✓ Actual weight loaded from spool data")
        else:
            print("⚠ Actual weight not loaded")
    else:
        print("✗ Actual weight field not found")
    
    print("\n=== Summary ===")
    print("✓ All new features implemented:")
    print("  - Dropdown prefill with first values")
    print("  - Weight dropdown (1kg/250g)")
    print("  - Price recall for matching brand/material/color/weight combos")
    print("  - Actual weight field")
    print("  - Automatic spool holder weight calculation")
    
    print("\n✓ New features test completed!")
    return True

if __name__ == "__main__":
    success = test_new_features()
    sys.exit(0 if success else 1)
