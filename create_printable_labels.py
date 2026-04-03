#!/usr/bin/env python3
"""Script to show a preview of what the barcode labels would look like when printed."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_printable_label(barcode_path: Path, output_dir: Path) -> None:
    """Create a printable label with barcode and ID text."""
    # Load the barcode image
    barcode_img = Image.open(barcode_path)
    
    # Get ID from filename (without .png)
    spool_id = barcode_path.stem
    
    # Create a new image with space for text below
    label_width = barcode_img.width
    text_height = 40
    label_height = barcode_img.height + text_height
    
    label = Image.new('RGB', (label_width, label_height), color='white')
    
    # Paste barcode on top
    label.paste(barcode_img, (0, 0))
    
    # Add text below
    draw = ImageDraw.Draw(label)
    
    # Try to use a nice font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Center the text
    bbox = draw.textbbox((0, 0), spool_id, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (label_width - text_width) // 2
    text_y = barcode_img.height + 5
    
    draw.text((text_x, text_y), spool_id, fill='black', font=font)
    
    # Save the printable label
    output_path = output_dir / f"{spool_id}_label.png"
    label.save(output_path)
    print(f"✓ Created printable label: {output_path.name}")

def main():
    """Generate printable labels for all barcodes."""
    print("Generating printable barcode labels...\n")
    
    barcodes_dir = Path(__file__).parent / "barcodes"
    labels_dir = Path(__file__).parent / "printable_labels"
    labels_dir.mkdir(exist_ok=True)
    
    # Find all barcode PNG files
    barcode_files = list(barcodes_dir.glob("*.png"))
    
    if not barcode_files:
        print("✗ No barcode files found in barcodes/ directory")
        print("  Run the app or test_barcode_generation.py first")
        return False
    
    for barcode_file in sorted(barcode_files):
        create_printable_label(barcode_file, labels_dir)
    
    print(f"\n✓ Generated {len(barcode_files)} printable labels")
    print(f"✓ Check '{labels_dir}' folder for printable PNG files")
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
