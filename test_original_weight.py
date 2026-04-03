"""Test script to verify original_weight changes"""
import json
from pathlib import Path

# Test 1: Check JSON file uses "original_weight"
print("Test 1: Checking sample_stock.json...")
with open("sample_stock.json", "r") as f:
    data = json.load(f)

for spool in data:
    spool_id = spool.get("id", "unknown")
    if "estimated_weight" in spool:
        print(f"  ❌ FAIL: {spool_id} still uses 'estimated_weight'")
    elif "original_weight" in spool:
        print(f"  ✓ PASS: {spool_id} uses 'original_weight' = {spool['original_weight']}g")
    else:
        print(f"  ⚠ WARNING: {spool_id} has no weight field")

# Test 2: Test backward compatibility by loading old format
print("\nTest 2: Testing backward compatibility with old 'estimated_weight' field...")
from FilamentStockManager import FilamentSpool

old_format = {
    "id": "TEST-001",
    "brand": "TestBrand",
    "material": "PLA",
    "name": "Test Spool",
    "color": "Green",
    "estimated_weight": 1000,  # Old field name
    "is_opened": False,
    "remaining_weight": None,
    "price": 20.0,
    "buying_date": "2026-04-03",
    "created_at": "2026-04-03T10:00:00",
    "updated_at": "2026-04-03T10:00:00",
    "barcode": "TEST-001",
    "actual_weight": 1230,
    "spool_holder_weight": 230
}

spool = FilamentSpool.from_dict(old_format)
if spool.original_weight == 1000:
    print("  ✓ PASS: Old 'estimated_weight' correctly loaded as 'original_weight'")
else:
    print(f"  ❌ FAIL: Expected 1000, got {spool.original_weight}")

# Test 3: Test new format
print("\nTest 3: Testing new 'original_weight' field...")
new_format = {
    "id": "TEST-002",
    "brand": "TestBrand",
    "material": "PETG",
    "name": "New Test Spool",
    "color": "Blue",
    "original_weight": 250,  # New field name
    "is_opened": True,
    "remaining_weight": 100,
    "price": 15.0,
    "buying_date": "2026-04-03",
    "created_at": "2026-04-03T11:00:00",
    "updated_at": "2026-04-03T11:00:00",
    "barcode": "TEST-002",
    "actual_weight": 450,
    "spool_holder_weight": 200
}

spool2 = FilamentSpool.from_dict(new_format)
if spool2.original_weight == 250:
    print("  ✓ PASS: New 'original_weight' field correctly loaded")
else:
    print(f"  ❌ FAIL: Expected 250, got {spool2.original_weight}")

# Test 4: Check to_dict() uses new field name
print("\nTest 4: Testing to_dict() serialization...")
spool_dict = spool2.to_dict()
if "original_weight" in spool_dict:
    print(f"  ✓ PASS: to_dict() uses 'original_weight' = {spool_dict['original_weight']}g")
elif "estimated_weight" in spool_dict:
    print("  ❌ FAIL: to_dict() still uses 'estimated_weight'")
else:
    print("  ❌ FAIL: to_dict() has no weight field")

print("\n" + "="*60)
print("All tests completed!")
print("="*60)
