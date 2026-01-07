"""
Data Quality Validator for CDR data
Validates CDR data before processing to ensure data integrity
"""
from datetime import datetime
import pandas as pd
import sys
import os
import re

class CDRDataQualityValidator:
    """Quality checks for telecom CDR data"""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.validation_results = []
        
    def validate_cdr_file(self, file_path):
        """
        Run comprehensive quality checks on CDR data
        Returns: (is_valid, validation_results)
        """
        print(f"\n[QUALITY CHECK] Validating: {file_path}")
        print("=" * 60)
        
        # Read data
        df = pd.read_csv(file_path)
        
        self.validation_results = []
        total_records = len(df)
        
        # ===== QUALITY CHECKS =====
        
        # 1. Schema Validation
        print("\n[1/7] Checking schema completeness...")
        expected_columns = ['call_id', 'caller_num', 'receiver_num', 'call_type', 
                          'duration_sec', 'timestamp', 'tower_id', 'signal_strength']
        missing_cols = set(expected_columns) - set(df.columns)
        if missing_cols:
            self.validation_results.append(('FAIL', 'Schema', f'Missing columns: {missing_cols}'))
        else:
            self.validation_results.append(('PASS', 'Schema', 'All required columns present'))
        
        # 2. No NULL values in critical columns
        print("[2/7] Checking for NULL values...")
        null_counts = df[expected_columns].isnull().sum()
        null_cols = null_counts[null_counts > 0]
        if len(null_cols) > 0:
            self.validation_results.append(('FAIL', 'NULL Check', f'NULL values found: {dict(null_cols)}'))
        else:
            self.validation_results.append(('PASS', 'NULL Check', 'No NULL values found'))
        
        # 3. Unique call_id (no duplicates)
        print("[3/7] Checking call_id uniqueness...")
        duplicates = df['call_id'].duplicated().sum()
        if duplicates > 0:
            self.validation_results.append(('FAIL', 'Uniqueness', f'{duplicates} duplicate call_ids found'))
        else:
            self.validation_results.append(('PASS', 'Uniqueness', 'All call_ids are unique'))
        
        # 4. Valid phone number format
        print("[4/7] Validating phone number formats...")
        phone_pattern = r'^\+947\d{8}$'
        invalid_caller = ~df['caller_num'].astype(str).str.match(phone_pattern)
        invalid_receiver = ~df['receiver_num'].astype(str).str.match(phone_pattern)
        if invalid_caller.sum() > 0 or invalid_receiver.sum() > 0:
            self.validation_results.append(('FAIL', 'Phone Format', 
                f'Invalid caller: {invalid_caller.sum()}, Invalid receiver: {invalid_receiver.sum()}'))
        else:
            self.validation_results.append(('PASS', 'Phone Format', 'All phone numbers valid'))
        
        # 5. Valid call_type enumeration
        print("[5/7] Validating call types...")
        valid_types = ['VOICE', 'SMS', 'DATA']
        invalid_types = ~df['call_type'].isin(valid_types)
        if invalid_types.sum() > 0:
            self.validation_results.append(('FAIL', 'Call Type', f'{invalid_types.sum()} invalid call types'))
        else:
            self.validation_results.append(('PASS', 'Call Type', 'All call types valid'))
        
        # 6. Duration constraints
        print("[6/7] Checking duration constraints...")
        invalid_duration = (df['duration_sec'] < 0) | (df['duration_sec'] > 7200)
        if invalid_duration.sum() > 0:
            self.validation_results.append(('FAIL', 'Duration', f'{invalid_duration.sum()} out-of-range durations'))
        else:
            self.validation_results.append(('PASS', 'Duration', 'All durations within valid range'))
        
        # 7. Signal strength range
        print("[7/7] Validating signal strength range...")
        invalid_signal = (df['signal_strength'] < 1) | (df['signal_strength'] > 5)
        if invalid_signal.sum() > 0:
            self.validation_results.append(('FAIL', 'Signal Strength', f'{invalid_signal.sum()} out-of-range signals'))
        else:
            self.validation_results.append(('PASS', 'Signal Strength', 'All signal strengths valid'))
        
        # Count results
        total_checks = len(self.validation_results)
        failed_checks = [r for r in self.validation_results if r[0] == 'FAIL']
        successful_checks = total_checks - len(failed_checks)
        success = len(failed_checks) == 0
        success_rate = (successful_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Print summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print(f"File: {file_path}")
        print(f"Total Records: {total_records}")
        print(f"Overall Status: {'✓ PASSED' if success else '✗ FAILED'}")
        print(f"Total Checks: {total_checks}")
        print(f"Successful: {successful_checks}")
        print(f"Failed: {len(failed_checks)}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Show all results
        print("\n" + "=" * 60)
        print("DETAILED RESULTS:")
        print("=" * 60)
        for status, check_name, message in self.validation_results:
            symbol = '✓' if status == 'PASS' else '✗'
            print(f"{symbol} {check_name}: {message}")
        
        print("=" * 60 + "\n")
        
        return success, self.validation_
        return success, results
    
    def generate_quality_report(self, file_path):
        """Generate text quality report"""
        success, results = self.validate_cdr_file(file_path)
        
        # Save validation results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"./data/quality_reports/validation_report_{timestamp}.txt"
        
        os.makedirs("./data/quality_reports", exist_ok=True)
        
        # Save text report
        with open(report_path, 'w') as f:
            f.write(f"Data Quality Report - {timestamp}\n")
            f.write("=" * 60 + "\n")
            f.write(f"File: {file_path}\n")
            f.write(f"Status: {'PASSED' if success else 'FAILED'}\n")
            f.write(f"Total Checks: {len(results)}\n\n")
            f.write("Detailed Results:\n")
            f.write("-" * 60 + "\n")
            for status, check_name, message in results:
                f.write(f"{status}: {check_name} - {message}\n")
        
        print(f"[INFO] Quality report saved to: {report_path}")
        
        return success


def main():
    """Run validation on latest CDR file"""
    import glob
    
    # Find latest CDR file
    cdr_files = glob.glob("./data/raw/cdr_*.csv")
    if not cdr_files:
        print("[ERROR] No CDR files found!")
        sys.exit(1)
    
    latest_file = max(cdr_files, key=os.path.getctime)
    
    # Validate
    validator = CDRDataQualityValidator("./data/raw")
    is_valid = validator.generate_quality_report(latest_file)
    
    if not is_valid:
        print("[QUALITY GATE] ✗ Data quality checks FAILED!")
        print("[ACTION] Fix data issues before processing.")
        sys.exit(1)
    else:
        print("[QUALITY GATE] ✓ Data quality checks PASSED!")
        print("[ACTION] Safe to proceed with ETL processing.")
        sys.exit(0)


if __name__ == "__main__":
    main()
