#!/usr/bin/env python3
"""
Export Attendance Records to CSV
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from src.utils import export_attendance_csv, get_today_summary

def print_menu():
    """Print export menu"""
    print("\n" + "=" * 60)
    print("  EXPORT ATTENDANCE RECORDS")
    print("=" * 60)
    print("\n1. Export Today's Records")
    print("2. Export This Week's Records")
    print("3. Export This Month's Records")
    print("4. Export All Records")
    print("5. Export Custom Date Range")
    print("6. View Today's Summary")
    print("0. Exit")
    print()

def get_date_input(prompt):
    """Get date input from user"""
    while True:
        date_str = input(prompt)
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            print("Invalid format. Use YYYY-MM-DD (e.g., 2024-06-13)")

def main():
    """Main export function"""
    
    if not os.path.exists(config.DATABASE_PATH):
        print(f"\nERROR: Database not found at {config.DATABASE_PATH}")
        print("No attendance records to export.")
        return
    
    while True:
        print_menu()
        
        try:
            choice = input("Select option: ").strip()
            
            if choice == "0":
                print("\nExiting...")
                break
            
            elif choice == "1":
                # Today
                today = datetime.now().strftime("%Y-%m-%d")
                output_file = f"attendance_today_{today}.csv"
                output_path = os.path.join(os.path.dirname(config.DATABASE_PATH), output_file)
                
                success, message = export_attendance_csv(
                    config.DATABASE_PATH, 
                    output_path, 
                    today, 
                    today
                )
                
                if success:
                    print(f"\n✓ {message}")
                else:
                    print(f"\n✗ {message}")
            
            elif choice == "2":
                # This week
                today = datetime.now()
                week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
                week_end = today.strftime("%Y-%m-%d")
                
                output_file = f"attendance_week_{week_start}_to_{week_end}.csv"
                output_path = os.path.join(os.path.dirname(config.DATABASE_PATH), output_file)
                
                success, message = export_attendance_csv(
                    config.DATABASE_PATH, 
                    output_path, 
                    week_start, 
                    week_end
                )
                
                if success:
                    print(f"\n✓ {message}")
                else:
                    print(f"\n✗ {message}")
            
            elif choice == "3":
                # This month
                today = datetime.now()
                month_start = today.replace(day=1).strftime("%Y-%m-%d")
                month_end = today.strftime("%Y-%m-%d")
                
                output_file = f"attendance_month_{today.strftime('%Y-%m')}.csv"
                output_path = os.path.join(os.path.dirname(config.DATABASE_PATH), output_file)
                
                success, message = export_attendance_csv(
                    config.DATABASE_PATH, 
                    output_path, 
                    month_start, 
                    month_end
                )
                
                if success:
                    print(f"\n✓ {message}")
                else:
                    print(f"\n✗ {message}")
            
            elif choice == "4":
                # All records
                output_file = f"attendance_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                output_path = os.path.join(os.path.dirname(config.DATABASE_PATH), output_file)
                
                success, message = export_attendance_csv(
                    config.DATABASE_PATH, 
                    output_path
                )
                
                if success:
                    print(f"\n✓ {message}")
                else:
                    print(f"\n✗ {message}")
            
            elif choice == "5":
                # Custom range
                print("\nEnter date range (YYYY-MM-DD format):")
                start_date = get_date_input("Start date: ")
                end_date = get_date_input("End date: ")
                
                output_file = f"attendance_{start_date}_to_{end_date}.csv"
                output_path = os.path.join(os.path.dirname(config.DATABASE_PATH), output_file)
                
                success, message = export_attendance_csv(
                    config.DATABASE_PATH, 
                    output_path, 
                    start_date, 
                    end_date
                )
                
                if success:
                    print(f"\n✓ {message}")
                else:
                    print(f"\n✗ {message}")
            
            elif choice == "6":
                # Today's summary
                summary = get_today_summary(config.DATABASE_PATH)
                
                if summary:
                    print("\n" + "=" * 60)
                    print(f"  TODAY'S ATTENDANCE SUMMARY - {summary['date']}")
                    print("=" * 60)
                    print(f"\n  Check-Ins: {summary['check_ins']}")
                    print(f"  Check-Outs: {summary['check_outs']}")
                    print(f"  Unique Employees: {summary['unique_employees']}")
                    print(f"  Total Records: {summary['total_records']}")
                    print("\n" + "=" * 60)
                else:
                    print("\n✗ Unable to retrieve summary")
            
            else:
                print("\nInvalid option. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")

if __name__ == "__main__":
    main()
