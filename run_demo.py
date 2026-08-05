import os
from processor import process_file

# Hardcoded test data (CSV format, realistic for CAM reconciliation)
test_csv = b"""tenant_name,property,charge_amount,due_date
Acme Corp,Riverside Plaza,4500.00,2025-06-01
Beta Inc,Sunset Towers,12000.00,2025-05-15
Gamma LLC,Highland Park,2500.00,2025-07-01"""

def main():
    print("Running demo with test CSV data...")
    results = process_file(test_csv)
    print(f"Extracted {len(results)} records:")
    for rec in results:
        print(f"  Title: {rec['title']}, Status: {rec['status']}, Due: {rec['due_date']}, Details: {rec['details']}")
    assert isinstance(results, list)
    print("Demo completed successfully.")

if __name__ == "__main__":
    main()
