"""Test script to verify default values for new spools"""
import tkinter as tk
from datetime import datetime
from FilamentStockManager import FilamentStockApp

def test_default_values():
    print("Testing Default Values for New Spools\n" + "=" * 60)
    
    # Create a test window (but don't show it)
    root = tk.Tk()
    root.withdraw()  # Hide the window
    app = FilamentStockApp(root)
    
    print("\nTest 1: Buying date should default to today's date")
    print("-" * 60)
    
    # Clear form should set buying date to today
    app.clear_form()
    
    buying_date = app.buying_date_var.get()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if buying_date == today:
        print(f"  ✓ PASS: Buying date defaults to today: {buying_date}")
    else:
        print(f"  ❌ FAIL: Expected {today}, got {buying_date}")
    
    print("\n\nTest 2: Remaining weight should equal original weight for new spools")
    print("-" * 60)
    
    # Set up a new spool
    app.brand_var.set("Prusament")
    app.material_var.set("PLA")
    app.name_var.set("Test Spool")
    app.color_var.set("Black")
    app.original_weight_var.set("1000")
    app.actual_weight_var.set("1250")
    app.price_var.set("24.99")
    app.status_var.set("new")  # Important: this is a new spool
    
    # Call _read_form to create the spool object
    spool = app._read_form()
    
    if spool:
        print(f"  Spool ID: {spool.id}")
        print(f"  Original weight: {spool.original_weight}g")
        print(f"  Remaining weight: {spool.remaining_weight}g")
        print(f"  Is opened: {spool.is_opened}")
        
        if spool.remaining_weight == spool.original_weight:
            print(f"  ✓ PASS: Remaining weight ({spool.remaining_weight}g) equals original weight ({spool.original_weight}g)")
        else:
            print(f"  ❌ FAIL: Remaining weight ({spool.remaining_weight}g) should equal original weight ({spool.original_weight}g)")
    else:
        print("  ❌ FAIL: Could not create spool")
    
    print("\n\nTest 3: Test with different original weights")
    print("-" * 60)
    
    for weight in [250, 500, 750, 1000]:
        app.clear_form()
        app.brand_var.set("TestBrand")
        app.material_var.set("PETG")
        app.name_var.set("Test")
        app.color_var.set("Blue")
        app.original_weight_var.set(str(weight))
        app.actual_weight_var.set(str(weight + 200))
        app.price_var.set("20.00")
        app.status_var.set("new")
        
        spool = app._read_form()
        if spool and spool.remaining_weight == weight:
            print(f"  ✓ PASS: {weight}g original → {spool.remaining_weight}g remaining")
        else:
            print(f"  ❌ FAIL: {weight}g original → {spool.remaining_weight if spool else 'ERROR'}g remaining")
    
    print("\n\nTest 4: Opened spools should use entered remaining weight (not original)")
    print("-" * 60)
    
    app.clear_form()
    app.brand_var.set("Prusament")
    app.material_var.set("PLA")
    app.name_var.set("Opened Test")
    app.color_var.set("Red")
    app.original_weight_var.set("1000")
    app.actual_weight_var.set("850")
    app.price_var.set("24.99")
    app.status_var.set("opened")  # This is an opened spool
    app.remaining_weight_var.set("600")  # User enters 600g remaining
    
    spool = app._read_form()
    
    if spool:
        print(f"  Original weight: {spool.original_weight}g")
        print(f"  Remaining weight: {spool.remaining_weight}g")
        print(f"  Is opened: {spool.is_opened}")
        
        if spool.remaining_weight == 600 and spool.remaining_weight != spool.original_weight:
            print(f"  ✓ PASS: Opened spool uses entered remaining weight (600g), not original (1000g)")
        else:
            print(f"  ❌ FAIL: Expected 600g remaining, got {spool.remaining_weight}g")
    else:
        print("  ❌ FAIL: Could not create spool")
    
    print("\n\nTest 5: Verify buying date persists on form clear")
    print("-" * 60)
    
    # Clear form multiple times and check date remains today
    for i in range(3):
        app.clear_form()
        buying_date = app.buying_date_var.get()
        if buying_date == today:
            print(f"  ✓ Clear #{i+1}: Buying date still {buying_date}")
        else:
            print(f"  ❌ Clear #{i+1}: Expected {today}, got {buying_date}")
    
    root.destroy()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_default_values()
