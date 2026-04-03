#!/usr/bin/env python3
"""Test script to verify barcode generation works correctly."""

import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import FilamentStockManager
sys.path.insert(0, str(Path(__file__).parent))

# Import necessary modules
from FilamentStockManager import FilamentSpool, barcode_lib, ImageWriter

def test_barcode_generation():
    """Test that barcode generation creates PNG files in barcodes folder."""
    
    # Check if barcode library is available
    if barcode_lib is None or ImageWriter is None:
        print("ERROR: python-barcode library not installed!")
        print("Install it with: pip install python-barcode[images]")
        return False
    
    print("✓ Barcode library is available")
    
    # Load test data
    test_file = Path(__file__).parent / "sample_stock.json"
    with test_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"✓ Loaded {len(data)} test spools")
    
    # Create barcodes directory
    barcode_dir = Path(__file__).parent / "barcodes"
    barcode_dir.mkdir(exist_ok=True)
    print(f"✓ Created/verified barcodes directory: {barcode_dir}")
    
    # Generate barcodes for each spool
    for item in data:
        spool = FilamentSpool.from_dict(item)
        
        try:
            # Get barcode directory
            barcode_dir = Path(__file__).parent / "barcodes"
            
            # The ID is now human-readable (e.g., PLA-BLACK-001)
            # Use it directly as the filename
            code128 = barcode_lib.get_barcode_class("code128")
            barcode_instance = code128(spool.id, writer=ImageWriter())
            output_path = barcode_dir / spool.id
            barcode_instance.save(str(output_path))
            
            # Check if PNG was created (library adds .png extension)
            png_file = Path(str(output_path) + ".png")
            if png_file.exists():
                size = png_file.stat().st_size
                print(f"✓ Generated barcode ID={spool.id}: {png_file.name} ({size} bytes)")
            else:
                print(f"✗ Failed to create PNG for {spool.id}")
                return False
                
        except Exception as e:
            print(f"✗ Error generating barcode for {spool.id}: {e}")
            return False
    
    print("\n✓ All barcodes generated successfully!")
    print(f"✓ Check the '{barcode_dir}' folder for PNG files")
    return True

if __name__ == "__main__":
    success = test_barcode_generation()
    sys.exit(0 if success else 1)
