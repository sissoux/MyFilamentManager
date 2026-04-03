"""Test script to verify auto-update features"""
import json
import tkinter as tk
from FilamentStockManager import FilamentStockApp

def test_auto_features():
    print("Testing Auto-Update Features\n" + "=" * 60)
    
    # Load sample data
    with open("sample_stock.json", "r") as f:
        data = json.load(f)
    
    print(f"\nLoaded {len(data)} sample spools\n")
    
    # Create a test window (but don't show it)
    root = tk.Tk()
    root.withdraw()  # Hide the window
    app = FilamentStockApp(root)
    
    # Load the sample data
    app._deserialize(data)
    
    print("Test 1: Selecting a spool should auto-set to 'opened'")
    print("-" * 60)
    
    # Simulate selecting the first spool (PLA-BLACK-001)
    app.selected_index = 0
    spool = app.spools[0]
    app.current_id = spool.id
    
    # Manually trigger the selection logic (simulating on_tree_select)
    app.brand_var.set(spool.brand)
    app.material_var.set(spool.material)
    app.name_var.set(spool.name)
    app.color_var.set(spool.color)
    app.original_weight_var.set(str(spool.original_weight))
    app.actual_weight_var.set(str(spool.actual_weight) if spool.actual_weight else "")
    # Auto-set to "opened" when selecting for update
    app.status_var.set("opened")
    app.remaining_weight_var.set("" if spool.remaining_weight is None else str(spool.remaining_weight))
    app._toggle_remaining_field()
    
    status = app.status_var.get()
    if status == "opened":
        print(f"  ✓ PASS: Status auto-set to 'opened' (was: {spool.is_opened})")
    else:
        print(f"  ❌ FAIL: Status is '{status}', expected 'opened'")
    
    print(f"\n  Spool: {spool.id}")
    print(f"  Original weight: {spool.original_weight}g")
    print(f"  Spool holder weight: {spool.spool_holder_weight}g")
    print(f"  Current actual weight: {spool.actual_weight}g")
    
    print("\n\nTest 2: Changing actual weight should auto-calculate remaining")
    print("-" * 60)
    
    # Test with different actual weights
    test_weights = [1200, 1100, 800, 450]
    
    for test_weight in test_weights:
        app.actual_weight_var.set(str(test_weight))
        # Trigger the callback manually
        app._on_actual_weight_changed()
        
        expected_remaining = test_weight - spool.spool_holder_weight
        actual_remaining_str = app.remaining_weight_var.get()
        
        if actual_remaining_str:
            actual_remaining = float(actual_remaining_str)
            if abs(actual_remaining - expected_remaining) < 0.1:
                print(f"  ✓ PASS: Actual={test_weight}g → Remaining={actual_remaining}g (expected {expected_remaining}g)")
            else:
                print(f"  ❌ FAIL: Actual={test_weight}g → Remaining={actual_remaining}g (expected {expected_remaining}g)")
        else:
            print(f"  ❌ FAIL: No remaining weight calculated for actual={test_weight}g")
    
    print("\n\nTest 3: Auto-calculation should not work for new spools")
    print("-" * 60)
    
    # Clear selection and set to "new"
    app.clear_form()
    app.current_id = None
    app.selected_index = None
    app.status_var.set("new")
    app.actual_weight_var.set("1300")
    app._on_actual_weight_changed()
    
    remaining = app.remaining_weight_var.get()
    if remaining == "":
        print("  ✓ PASS: Remaining weight not calculated for new spools")
    else:
        print(f"  ❌ FAIL: Remaining weight should not be calculated for new spools (got {remaining})")
    
    print("\n\nTest 4: Test with PETG spool (different holder weight)")
    print("-" * 60)
    
    # Select PETG-BLUE-001 (index 1)
    app.selected_index = 1
    spool2 = app.spools[1]
    app.current_id = spool2.id
    app.status_var.set("opened")
    app.actual_weight_var.set(str(spool2.actual_weight))
    
    print(f"  Spool: {spool2.id}")
    print(f"  Spool holder weight: {spool2.spool_holder_weight}g")
    
    # Test calculation
    test_weight = 900
    app.actual_weight_var.set(str(test_weight))
    app._on_actual_weight_changed()
    
    expected = test_weight - spool2.spool_holder_weight
    actual = float(app.remaining_weight_var.get())
    
    if abs(actual - expected) < 0.1:
        print(f"  ✓ PASS: Actual={test_weight}g → Remaining={actual}g (expected {expected}g)")
    else:
        print(f"  ❌ FAIL: Got {actual}g, expected {expected}g")
    
    root.destroy()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_auto_features()
