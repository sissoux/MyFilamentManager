# Filament Stock Manager

Desktop application for managing 3D printer filament inventory with barcode generation and automatic weight tracking.

## Key Features

- **Smart Inventory**: Track spools with human-readable IDs (e.g., `PLA-BLACK-001`)
- **Auto-calculations**: Automatic weight and price memory
- **Barcode Labels**: Generate and print labels for Brother QL-800 printer
- **Dynamic Dropdowns**: Custom materials, colors, and brands persist automatically
- **Import/Export**: JSON and YAML support

## Installation

```bash
pip install python-barcode pillow pyyaml
python FilamentStockManager.py
```

**Optional** (for Brother QL-800 printing):
```bash
pip install brother-ql pyusb
```

## How to Use

### Adding a New Spool

1. **Fill the form** with spool details (Brand, Material, Color, Weight)
2. **Weigh the entire spool** and enter as "Actual Weight"
3. **Click "Add Spool"** – barcode generates automatically

💡 The buying date auto-fills with today, and price remembers previous purchases for the same material/color combination.

### Updating Weight

1. **Select a spool** from the table
2. **Weigh and update** the "Actual Weight" field
3. **Click "Update Spool"** – remaining weight calculates automatically

### Duplicating a Spool

1. **Select a spool** to use as template
2. **Click "Duplicate"**
3. **Choose new color** and weigh the spool
4. **Confirm** – creates a new spool with unique ID

### Printing Labels

1. **Connect Brother QL-800** with 62mm continuous labels (DK-22205)
2. **Select a spool** from the table
3. **Click "Print Label"** – prints immediately with auto-cut

### Managing Files

- **Ctrl+N**: New stock file
- **Ctrl+O**: Open stock file
- **Ctrl+S**: Save stock file
- **Auto-save checkbox**: Automatically saves after each change

### Custom Dropdowns

All dropdowns accept custom values:
- Type directly in the field
- Custom values save to `defaults.json` automatically
- Most-used values appear at the top

## Understanding Weight Fields

- **Original Weight**: Filament weight only (e.g., 1000g)
- **Actual Weight**: Total weight including spool holder (weigh the whole spool)
- **Spool Holder Weight**: Calculated automatically (Actual - Original)
- **Remaining Weight**: Auto-calculated when updating (Actual - Holder)

## Files

- `stock.json` – Your inventory (auto-loaded at startup)
- `defaults.json` – Custom materials/colors/brands
- `barcodes/` – Generated barcode images
- `printable_labels/` – Printable label images

---

**Need more details?** See [NEW_FEATURES_GUIDE.md](NEW_FEATURES_GUIDE.md) for comprehensive documentation.

**Made for 3D printing enthusiasts who want to track their filament inventory efficiently! 🎨🖨️**
