#!/usr/bin/env python3
"""Test script to verify human-readable ID generation."""

import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import FilamentStockManager
sys.path.insert(0, str(Path(__file__).parent))

# Import necessary modules
from FilamentStockManager import FilamentSpool, FilamentStockApp
import tkinter as tk

def test_human_readable_ids():
    """Test that IDs are generated in human-readable format."""
    
    print("Testing human-readable ID generation...\n")
    
    # Create a minimal Tkinter app instance to test ID generation
    root = tk.Tk()
    root.withdraw()  # Hide the window
    app = FilamentStockApp(root)
    
    # Test data for spools
    test_spools = [
        {"material": "PLA", "color": "Black"},
        {"material": "PLA", "color": "Black"},  # Duplicate to test incrementing
        {"material": "PETG", "color": "Blue"},
        {"material": "PLA", "color": "White"},
        {"material": "PETG", "color": "Blue"},  # Another duplicate
    ]
    
    generated_ids = []
    
    for spool_data in test_spools:
        material = spool_data["material"]
        color = spool_data["color"]
        
        # Generate ID using the app's method
        new_id = app._generate_human_readable_id(material, color)
        generated_ids.append(new_id)
        
        print(f"Material: {material:6} | Color: {color:6} | Generated ID: {new_id}")
        
        # Add a dummy spool to the app's list so the next ID increments
        dummy_spool = FilamentSpool(
            id=new_id,
            brand="Test",
            material=material,
            name="Test Spool",
            color=color,
            estimated_weight=1000,
            is_opened=False,
            remaining_weight=None,
            price=20.0,
            buying_date="2026-04-03",
            created_at="2026-04-03T10:00:00",
            updated_at="2026-04-03T10:00:00",
            barcode=new_id,
        )
        app.spools.append(dummy_spool)
    
    print("\n✓ All IDs generated successfully!")
    print(f"\nGenerated IDs: {generated_ids}")
    
    # Verify expected patterns
    expected = ["PLA-BLACK-001", "PLA-BLACK-002", "PETG-BLUE-001", "PLA-WHITE-001", "PETG-BLUE-002"]
    if generated_ids == expected:
        print("\n✓ IDs match expected pattern!")
        return True
    else:
        print(f"\n✗ IDs do not match expected pattern!")
        print(f"Expected: {expected}")
        print(f"Got:      {generated_ids}")
        return False

if __name__ == "__main__":
    success = test_human_readable_ids()
    sys.exit(0 if success else 1)
