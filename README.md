# Filament Stock Manager

A comprehensive desktop application for managing 3D printer filament inventory with barcode generation, smart defaults, and automatic weight calculations.

## Features

### 📦 Inventory Management
- Track filament spools with detailed information (brand, material, color, weight, price)
- Human-readable spool IDs (e.g., `PLA-BLACK-001`)
- Support for both new and opened spools
- Automatic barcode generation for each spool
- Import/Export stock data (JSON/YAML formats)

### 🎯 Smart Auto-Fill Features
- **Auto-Fill Buying Date**: Today's date automatically fills when creating new spools
- **Auto-Calculate Remaining Weight**: Automatically calculates remaining filament weight based on actual weight minus spool holder weight
- **Auto-Set Opened Status**: When selecting a spool to update, status automatically changes to "Opened"
- **Smart Price Recall**: Remembers the last price paid for specific Brand + Material + Color + Weight combinations
- **Auto-Save**: Optional checkbox to automatically save the file after any change (add/update/delete/duplicate)

### 📊 Dynamic Dropdowns
- **Materials**: PLA, PLA Silk, PETG, TPU, ABS, ASA, Nylon, PETG Carbon, PC
- **Colors**: Black, White, Red, Blue, Green, Yellow, Orange, Purple, Gray, Natural
- **Brands**: Prusa, Sunlu, Bambu Lab, Polymaker
- **Weights**: 1000g (1kg), 250g (mini spools)
- All dropdowns support custom values
- **Custom values are automatically saved** to `defaults.json` and persist across sessions
- Most-used values appear at the top

### 🏷️ Barcode & Label Generation
- Automatic barcode generation (Code128 format)
- **Direct printing to Brother QL-800 label printer** (62mm DK-22205 labels)
- Printable labels combining barcode + spool ID  
- Easy scanning for quick inventory updates
- Barcodes stored in `barcodes/` directory
- Printable labels stored in `printable_labels/` directory

### 📈 Weight Tracking
- **Original Weight**: Manufacturer's specified filament weight (e.g., 1000g)
- **Actual Weight**: Total weight including spool holder
- **Spool Holder Weight**: Automatically calculated (Actual - Original)
- **Remaining Weight**: Auto-calculated when updating (Actual - Spool Holder)

## Requirements

### Python Version
- Python 3.8 or higher

### Dependencies
```bash
pip install python-barcode pillow pyyaml brother-ql pyusb
```

**Required:**
- `tkinter` (usually included with Python)
- `python-barcode` - Barcode generation
- `Pillow` - Image processing for labels

**Optional:**
- `pyyaml` - YAML file support
- `brother-ql` - Direct printing to Brother QL label printers
- `pyusb` - USB communication for Brother QL printers

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install python-barcode pillow pyyaml
   ```
3. Run the application:
   ```bash
   python FilamentStockManager.py
   ```

## Usage

### Starting the Application
```bash
python FilamentStockManager.py
```

### Creating a New Spool
1. Fill in the form fields:
   - **Brand**: Select from dropdown or type custom value
   - **Material**: Select from dropdown or type custom value
   - **Color**: Select from dropdown or type custom value
   - **Name**: Optional product name
   - **Original Weight**: Select 1000g or 250g (or type custom)
   - **Actual Weight**: Total weight including spool holder
   - **Status**: "New" (unopened) or "Opened"
   - **Price**: Cost of the spool
   - **Buying Date**: Automatically filled with today's date
2. Click "Add Spool"
3. Barcode and printable label are automatically generated

### Updating a Spool
1. Select a spool from the table
2. Update the **Actual Weight** field (weigh the entire spool)
3. Remaining weight is automatically calculated
4. Click "Update Spool"

### Printing Labels (Brother QL-800)
1. Make sure your Brother QL-800 printer is:
   - Connected via USB
   - Powered on
   - Loaded with 62mm continuous labels (DK-22205)
2. Select a spool from the table
3. Click "Print Label"
4. The barcode label will print automatically with auto-cut

**Note:** The print function requires `brother-ql` and `pyusb` packages. If not installed, you'll see an error message with installation instructions.

### Generating Printable Labels
Run the label generator script:
```bash
python create_printable_labels.py
```

This creates printable labels (barcode + ID text) in the `printable_labels/` directory.

## File Formats

### JSON Stock File
```json
{
  "spools": [
    {
      "id": "PLA-BLACK-001",
      "brand": "Prusa",
      "material": "PLA",
      "name": "Prusament PLA",
      "color": "Black",
      "original_weight": 1000.0,
      "actual_weight": 1250.0,
      "spool_holder_weight": 250.0,
      "is_opened": false,
      "remaining_weight": 1000.0,
      "price": 24.99,
      "buying_date": "2026-04-03",
      "created_at": "2026-04-03T10:30:00",
      "updated_at": "2026-04-03T10:30:00",
      "barcode": "PLA-BLACK-001"
    }
  ]
}
```

## Project Structure

```
MyFilamentManager/
├── FilamentStockManager.py      # Main application
├── create_printable_labels.py   # Label generation script
├── README.md                     # This file
├── NEW_FEATURES_GUIDE.md        # Detailed features guide
├── COMBOBOX_FEATURES.md         # Dropdown features documentation
├── stock.json                   # Main stock data (auto-loaded at startup)
├── defaults.json                # Custom materials/colors/brands (auto-saved)
├── sample_stock.json            # Sample stock data
├── test_stock.json              # Test data
├── requirements.txt             # Python dependencies
├── barcodes/                    # Generated barcodes (PNG)
├── printable_labels/            # Printable labels (PNG)
├── test_*.py                    # Unit tests
└── __pycache__/                 # Python cache
```

## Testing

Run the test suite:
```bash
python test_new_features.py
python test_auto_update.py
python test_barcode_generation.py
python test_combobox_values.py
python test_default_values.py
python test_dynamic_combobox.py
python test_human_readable_ids.py
python test_original_weight.py
```

## Tips & Tricks

### Fast Workflow for New Spools
1. Select Brand, Material, Color, Weight from dropdowns
2. Enter Actual Weight (weigh the full spool)
3. Price auto-fills if you've bought this combination before
4. Buying date auto-fills with today
5. For "New" status, remaining weight auto-fills with original weight
6. Click "Add Spool" → Done!

### Fast Workflow for Updating Spools
1. Select spool from table (status auto-changes to "Opened")
2. Weigh the spool and enter new Actual Weight
3. Remaining weight auto-calculates
4. Click "Update Spool" → Done!

### Fast Workflow for Printing Labels
1. Select spool from table
2. Click "Print Label"
3. Label prints automatically on Brother QL-800 → Done!

### Custom Values
All dropdown fields accept custom values:
- Type directly in the combobox field
- Custom values are saved and appear in future dropdowns
- Values are sorted by frequency of use

### Auto-Save
Enable the "Auto-save after changes" checkbox at the bottom of the form to automatically save your stock file after every add, update, delete, or duplicate operation. Your preference is saved and remembered for next time.

## Keyboard Shortcuts

- **Ctrl+N**: New stock file
- **Ctrl+O**: Open stock file
- **Ctrl+S**: Save stock file

## Data Persistence

Stock data is saved in JSON format and includes:
- All spool information
- Timestamps (created_at, updated_at)
- Barcode references
- Weight calculations

## License

Free to use and modify for personal or commercial projects.

## Support

For questions or issues, refer to:
- [NEW_FEATURES_GUIDE.md](NEW_FEATURES_GUIDE.md) - Detailed feature explanations
- [COMBOBOX_FEATURES.md](COMBOBOX_FEATURES.md) - Dropdown behavior details

## Version History

### Latest Version
- Human-readable spool IDs
- Smart auto-fill features
- Auto-calculate remaining weight
- Price recall memory
- Barcode generation
- Printable labels
- Dynamic dropdowns with custom values
- Spool holder weight tracking

---

**Made for 3D printing enthusiasts who want to track their filament inventory efficiently! 🎨🖨️**
