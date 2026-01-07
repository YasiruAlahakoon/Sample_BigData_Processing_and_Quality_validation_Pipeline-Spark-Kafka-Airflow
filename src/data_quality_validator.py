"""
Data Quality Validator using Great Expectations
Validates CDR data before processing to ensure data integrity
"""
import great_expectations as gx
from great_expectations.core.batch import BatchRequest
from datetime import datetime
import pandas as pd
import sys
import os

class CDRDataQualityValidator:
    """Quality checks for telecom CDR data"""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.context = gx.get_context()
        self.validation_results = {}
        
    def validate_cdr_file(self, file_path):
        """
        Run comprehensive quality checks on CDR data
        Returns: (is_valid, validation_results)
        """
        print(f"\n[QUALITY CHECK] Validating: {file_path}")
        print("=" * 60)
        
        # Read data
        df = pd.read_csv(file_path)
        
        # Create validator
        validator = self.context.sources.pandas_default.read_dataframe(df)
        
        # ===== QUALITY CHECKS =====
        
        # 1. Schema Validation
        print("\n[1/7] Checking schema completeness...")
        expected_columns = ['call_id', 'caller_num', 'receiver_num', 'call_type', 
                          'duration_sec', 'timestamp', 'tower_id', 'signal_strength']
        validator.expect_table_columns_to_match_set(
            column_set=expected_columns,
            exact_match=True
        )
        
        # 2. No NULL values in critical columns
        print("[2/7] Checking for NULL values...")
        for col in expected_columns:
            validator.expect_column_values_to_not_be_null(column=col)
        
        # 3. Unique call_id (no duplicates)
        print("[3/7] Checking call_id uniqueness...")
        validator.expect_column_values_to_be_unique(column='call_id')
        
        # 4. Valid phone number format
        print("[4/7] Validating phone number formats...")
        validator.expect_column_values_to_match_regex(
            column='caller_num',
            regex=r'^\+947\d{8}$'
        )
        validator.expect_column_values_to_match_regex(
            column='receiver_num',
            regex=r'^\+947\d{8}$'
        )
        
        # 5. Valid call_type enumeration
        print("[5/7] Validating call types...")
        validator.expect_column_values_to_be_in_set(
            column='call_type',
            value_set=['VOICE', 'SMS', 'DATA']
        )
        
        # 6. Duration constraints
        print("[6/7] Checking duration constraints...")
        validator.expect_column_values_to_be_between(
            column='duration_sec',
            min_value=0,
            max_value=7200  # Max 2 hours
        )
        
        # 7. Signal strength range
        print("[7/7] Validating signal strength range...")
        validator.expect_column_values_to_be_between(
            column='signal_strength',
            min_value=1,
            max_value=5
        )
        
        # Get validation results
        checkpoint_result = validator.validate()
        
        # Print summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        success = checkpoint_result.success
        stats = checkpoint_result.statistics
        
        print(f"Overall Status: {'✓ PASSED' if success else '✗ FAILED'}")
        print(f"Total Checks: {stats['evaluated_validations']}")
        print(f"Successful: {stats['successful_validations']}")
        print(f"Failed: {stats['unsuccessful_validations']}")
        print(f"Success Rate: {stats['success_percent']:.1f}%")
        
        # Show failures in detail
        if not success:
            print("\n" + "=" * 60)
            print("FAILED VALIDATIONS:")
            print("=" * 60)
            for result in checkpoint_result.results:
                if not result.success:
                    expectation = result.expectation_config.expectation_type
                    print(f"✗ {expectation}")
                    if 'column' in result.expectation_config.kwargs:
                        print(f"  Column: {result.expectation_config.kwargs['column']}")
                    print(f"  Details: {result.result}")
        
        print("=" * 60 + "\n")
        
        return success, checkpoint_result
    
    def generate_quality_report(self, file_path):
        """Generate HTML quality report"""
        success, results = self.validate_cdr_file(file_path)
        
        # Save validation results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"./data/quality_reports/validation_report_{timestamp}.html"
        
        os.makedirs("./data/quality_reports", exist_ok=True)
        
        # Build data docs (HTML reports)
        self.context.build_data_docs()
        
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
