import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime
from pathlib import Path
import warnings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

warnings.filterwarnings('ignore')


class DataCleaner:
    def __init__(self, dataset_path, step1_output_folder, log_folder, output_folder):
        """
        Initialize the DataCleaner for Step 2

        Args:
            dataset_path: Path to the original dataset
            step1_output_folder: Path to Step 1 analysis results
            log_folder: Folder for log files
            output_folder: Folder for cleaned dataset output
        """
        self.dataset_path = dataset_path
        self.step1_output_folder = Path(step1_output_folder)
        self.log_folder = Path(log_folder)
        self.output_folder = Path(output_folder)

        # Create timestamp for this cleaning session
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_folder = f"step2_data_cleaning_{self.timestamp}"

        # Create session-specific folders
        self.session_log_folder = self.log_folder / self.session_folder
        self.session_output_folder = self.output_folder / self.session_folder

        # Create directories
        for folder in [self.session_log_folder, self.session_output_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Load dataset
        self.df = None
        self.original_shape = None
        self.cleaning_log = []
        self.load_dataset()

    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.session_log_folder / f"cleaning_log_{self.timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Data cleaning started at {datetime.now()}")

    def load_dataset(self):
        """Load the original dataset"""
        try:
            if self.dataset_path.endswith('.xlsx') or self.dataset_path.endswith('.xls'):
                self.df = pd.read_excel(self.dataset_path)
            elif self.dataset_path.endswith('.csv'):
                self.df = pd.read_csv(self.dataset_path)
            else:
                raise ValueError("Unsupported file format. Please use .xlsx, .xls, or .csv")

            self.original_shape = self.df.shape
            self.logger.info(f"Original dataset loaded successfully. Shape: {self.original_shape}")
            print(f"✅ Original dataset loaded: {self.original_shape[0]} rows, {self.original_shape[1]} columns")

        except Exception as e:
            self.logger.error(f"Error loading dataset: {str(e)}")
            raise

    def load_step1_results(self):
        """Load results from Step 1 analysis"""
        print("\n" + "=" * 50)
        print("LOADING STEP 1 ANALYSIS RESULTS")
        print("=" * 50)

        try:
            # Find the most recent step1 folder
            step1_folders = [f for f in self.step1_output_folder.parent.iterdir()
                             if f.is_dir() and f.name.startswith('step1_dataset_analysis_')]

            if not step1_folders:
                raise FileNotFoundError("No Step 1 analysis results found")

            # Get the most recent step1 folder
            latest_step1_folder = max(step1_folders, key=lambda x: x.stat().st_mtime)
            print(f"📁 Using Step 1 results from: {latest_step1_folder.name}")

            # Load complete identical rows
            identical_rows_file = None
            for file in latest_step1_folder.iterdir():
                if file.name.startswith('complete_identical_rows_'):
                    identical_rows_file = file
                    break

            if identical_rows_file and identical_rows_file.exists():
                self.identical_rows = pd.read_csv(identical_rows_file)
                print(f"✅ Loaded complete identical rows: {len(self.identical_rows)} rows")
            else:
                self.identical_rows = pd.DataFrame()
                print("✅ No complete identical rows file found")

            self.logger.info(f"Step 1 results loaded from {latest_step1_folder}")
            return latest_step1_folder

        except Exception as e:
            self.logger.error(f"Error loading Step 1 results: {str(e)}")
            raise

    def remove_complete_duplicates(self):
        """Remove complete identical rows, keeping only one copy"""
        print("\n" + "=" * 50)
        print("REMOVING COMPLETE DUPLICATE ROWS")
        print("=" * 50)

        if len(self.identical_rows) == 0:
            print("✅ No complete duplicate rows to remove")
            self.logger.info("No complete duplicate rows found to remove")
            return

        # Find all duplicated rows (including originals)
        all_duplicates_mask = self.df.duplicated(keep=False)
        duplicate_groups = self.df[all_duplicates_mask]

        if len(duplicate_groups) == 0:
            print("✅ No duplicate groups found in current dataset")
            return

        print(f"Found {len(duplicate_groups)} rows involved in duplications")

        # Keep only the first occurrence of each duplicate group
        before_count = len(self.df)

        # Get indices of rows to remove (all duplicates except the first occurrence)
        duplicates_to_remove = self.df.duplicated(keep='first')
        removed_indices = self.df[duplicates_to_remove].index.tolist()

        # Remove duplicates
        self.df = self.df.drop_duplicates(keep='first').reset_index(drop=True)

        after_count = len(self.df)
        removed_count = before_count - after_count

        print(f"📊 Duplicate removal summary:")
        print(f"  Rows before: {before_count}")
        print(f"  Rows after: {after_count}")
        print(f"  Rows removed: {removed_count}")

        # Log which specific rows were removed
        if removed_indices:
            self.cleaning_log.append({
                'action': 'remove_duplicates',
                'rows_removed': removed_indices,
                'count': removed_count,
                'description': f"Removed {removed_count} complete duplicate rows"
            })

            print(f"📝 Removed row indices: {removed_indices[:10]}{'...' if len(removed_indices) > 10 else ''}")
            self.logger.info(f"Removed complete duplicate rows. Row indices: {removed_indices}")

        self.logger.info(f"Duplicate removal completed. Removed {removed_count} rows")

    def fix_null_schadennummer(self):
        """Fix null Schadennummer values for patients with same birthdate and schadendatum"""
        print("\n" + "=" * 50)
        print("FIXING NULL SCHADENNUMMER VALUES")
        print("=" * 50)

        if 'Schadennummer' not in self.df.columns:
            print("❌ Schadennummer column not found")
            return

        # Find rows with null Schadennummer
        null_schadennummer = self.df['Schadennummer'].isnull()
        null_count = null_schadennummer.sum()

        print(f"Found {null_count} rows with null Schadennummer")

        if null_count == 0:
            print("✅ No null Schadennummer values to fix")
            return

        # Check if we have the expected pattern (6 rows with same birthdate and schadendatum)
        null_rows = self.df[null_schadennummer]

        # Check if birthdate and schadendatum columns exist
        date_columns = []
        for col in ['birthdate', 'schadendatum', 'Schadendatum']:
            if col in self.df.columns:
                date_columns.append(col)

        if len(date_columns) >= 2:
            # Group null rows by date columns to see if they belong to same patient
            grouping_cols = date_columns[:2]  # Use first two date columns found
            grouped = null_rows.groupby(grouping_cols).size()

            print(f"Grouping null Schadennummer rows by {grouping_cols}:")
            for group_key, count in grouped.items():
                print(f"  {group_key}: {count} rows")

        # Get indices of null Schadennummer rows
        null_indices = self.df[null_schadennummer].index.tolist()

        # Assign "without_schadennummer" to Schadennummer
        self.df.loc[null_schadennummer, 'Schadennummer'] = 'without_schadennummer'

        # Assign 0 to Unique ID for these rows
        if 'Unique ID' in self.df.columns:
            self.df.loc[null_schadennummer, 'Unique ID'] = 0

        print(f"📊 Null Schadennummer fix summary:")
        print(f"  Rows modified: {null_count}")
        print(f"  Schadennummer set to: 'without_schadennummer'")
        print(f"  Unique ID set to: 0")

        # Log the changes
        self.cleaning_log.append({
            'action': 'fix_null_schadennummer',
            'rows_modified': null_indices,
            'count': null_count,
            'description': f"Fixed {null_count} null Schadennummer values, set to 'without_schadennummer' and Unique ID to 0"
        })

        print(f"📝 Modified row indices: {null_indices}")
        self.logger.info(f"Fixed null Schadennummer values. Row indices: {null_indices}")

    def remove_hash_column_duplicates(self):
        """Remove duplicate rows based on # column, keeping only the first occurrence"""
        print("\n" + "=" * 50)
        print("REMOVING # COLUMN DUPLICATES")
        print("=" * 50)

        if '#' not in self.df.columns:
            print("❌ '#' column not found")
            return

        # Find duplicates in # column
        hash_duplicates = self.df['#'].duplicated(keep='first')  # Keep first, mark others as duplicates
        duplicate_count = hash_duplicates.sum()

        print(f"Found {duplicate_count} duplicate rows based on # column")

        if duplicate_count == 0:
            print("✅ No # column duplicates to remove")
            return

        # Show some examples before removal
        all_hash_duplicates = self.df['#'].duplicated(keep=False)  # Mark all duplicates including first
        duplicate_examples = self.df[all_hash_duplicates][['#', 'Schadennummer', 'Unique ID']].groupby('#').size()

        print(f"Examples of duplicate # values (showing frequency):")
        for hash_val, count in duplicate_examples.head(10).items():
            print(f"  # = {hash_val}: {count} occurrences")

        # Get indices of rows to remove
        removed_indices = self.df[hash_duplicates].index.tolist()

        # Remove duplicates (keep first occurrence)
        before_count = len(self.df)
        self.df = self.df[~hash_duplicates].reset_index(drop=True)
        after_count = len(self.df)

        print(f"📊 # column duplicate removal summary:")
        print(f"  Rows before: {before_count}")
        print(f"  Rows after: {after_count}")
        print(f"  Rows removed: {duplicate_count}")

        # Log the changes
        self.cleaning_log.append({
            'action': 'remove_hash_duplicates',
            'rows_removed': removed_indices,
            'count': duplicate_count,
            'description': f"Removed {duplicate_count} duplicate rows based on # column, kept first occurrence"
        })

        print(f"📝 Removed row indices: {removed_indices[:10]}{'...' if len(removed_indices) > 10 else ''}")
        self.logger.info(f"Removed # column duplicates. Row indices: {removed_indices}")

        self.logger.info(f"# column duplicate removal completed. Removed {duplicate_count} rows")

    def remove_hash_column_duplicates(self):
        """Remove duplicate rows based on # column, keeping only the first occurrence"""
        print("\n" + "=" * 50)
        print("REMOVING # COLUMN DUPLICATES")
        print("=" * 50)

        if '#' not in self.df.columns:
            print("❌ '#' column not found")
            return

        # Find duplicates in # column
        hash_duplicates = self.df['#'].duplicated(keep='first')  # Keep first, mark others as duplicates
        duplicate_count = hash_duplicates.sum()

        print(f"Found {duplicate_count} duplicate rows based on # column")

        if duplicate_count == 0:
            print("✅ No # column duplicates to remove")
            return

        # Show some examples before removal
        all_hash_duplicates = self.df['#'].duplicated(keep=False)  # Mark all duplicates including first
        duplicate_examples = self.df[all_hash_duplicates][['#', 'Schadennummer', 'Unique ID']].groupby('#').size()

        print(f"Examples of duplicate # values (showing frequency):")
        for hash_val, count in duplicate_examples.head(10).items():
            print(f"  # = {hash_val}: {count} occurrences")

        # Get indices of rows to remove
        removed_indices = self.df[hash_duplicates].index.tolist()

        # Remove duplicates (keep first occurrence)
        before_count = len(self.df)
        self.df = self.df[~hash_duplicates].reset_index(drop=True)
        after_count = len(self.df)

        print(f"📊 # column duplicate removal summary:")
        print(f"  Rows before: {before_count}")
        print(f"  Rows after: {after_count}")
        print(f"  Rows removed: {duplicate_count}")

        # Log the changes
        self.cleaning_log.append({
            'action': 'remove_hash_duplicates',
            'rows_removed': removed_indices,
            'count': duplicate_count,
            'description': f"Removed {duplicate_count} duplicate rows based on # column, kept first occurrence"
        })

        print(f"📝 Removed row indices: {removed_indices[:10]}{'...' if len(removed_indices) > 10 else ''}")
        self.logger.info(f"Removed # column duplicates. Row indices: {removed_indices}")

        self.logger.info(f"# column duplicate removal completed. Removed {duplicate_count} rows")

    def remove_schadennummer_column(self):
        """Remove Schadennummer column for data privacy"""
        print("\n" + "=" * 50)
        print("REMOVING SCHADENNUMMER COLUMN (DATA PRIVACY)")
        print("=" * 50)

        if 'Schadennummer' not in self.df.columns:
            print("❌ Schadennummer column not found")
            return

        # Save the unique values before removal for logging
        unique_schadennummer = self.df['Schadennummer'].unique()

        # Remove the column
        self.df = self.df.drop('Schadennummer', axis=1)

        print(f"✅ Schadennummer column removed")
        print(f"📊 Column contained {len(unique_schadennummer)} unique values")

        self.cleaning_log.append({
            'action': 'remove_schadennummer',
            'description': f"Removed Schadennummer column for data privacy. Column had {len(unique_schadennummer)} unique values"
        })

        self.logger.info("Removed Schadennummer column for data privacy")

    def verify_cleaned_dataset(self):
        """Verify the cleaned dataset for remaining issues"""
        print("\n" + "=" * 50)
        print("VERIFYING CLEANED DATASET")
        print("=" * 50)

        verification_results = {}

        # 1. Check for remaining identical rows
        print("1. CHECKING FOR REMAINING IDENTICAL ROWS:")
        print("-" * 40)

        remaining_duplicates = self.df.duplicated()
        duplicate_count = remaining_duplicates.sum()

        print(f"Remaining complete duplicate rows: {duplicate_count}")
        verification_results['remaining_duplicates'] = duplicate_count

        if duplicate_count > 0:
            print("❌ WARNING: Still have duplicate rows!")
            duplicate_indices = self.df[remaining_duplicates].index.tolist()
            print(f"Duplicate row indices: {duplicate_indices}")
        else:
            print("✅ No remaining duplicate rows")

        # 2. Check for missing values in Unique ID
        print(f"\n2. CHECKING UNIQUE ID COLUMN:")
        print("-" * 30)

        if 'Unique ID' in self.df.columns:
            missing_unique_id = self.df['Unique ID'].isnull().sum()
            unique_id_count = self.df['Unique ID'].nunique()

            print(f"Missing values in Unique ID: {missing_unique_id}")
            print(f"Unique patients (Unique ID): {unique_id_count}")

            verification_results['missing_unique_id'] = missing_unique_id
            verification_results['unique_patients'] = unique_id_count

            if missing_unique_id > 0:
                print("❌ WARNING: Missing values in Unique ID column!")
                missing_indices = self.df[self.df['Unique ID'].isnull()].index.tolist()
                print(f"Missing Unique ID row indices: {missing_indices}")
            else:
                print("✅ No missing values in Unique ID")
        else:
            print("❌ Unique ID column not found!")
            verification_results['unique_id_column_exists'] = False

        # 3. Overall dataset summary
        print(f"\n3. OVERALL DATASET SUMMARY:")
        print("-" * 30)

        current_shape = self.df.shape
        rows_removed = self.original_shape[0] - current_shape[0]

        summary = {
            'Original rows': self.original_shape[0],
            'Current rows': current_shape[0],
            'Rows removed': rows_removed,
            'Original columns': self.original_shape[1],
            'Current columns': current_shape[1],
            'Columns removed': self.original_shape[1] - current_shape[1]
        }

        for key, value in summary.items():
            print(f"  {key}: {value}")

        verification_results.update(summary)

        # Save verification results
        verification_df = pd.DataFrame(list(verification_results.items()), columns=['Metric', 'Value'])
        verification_df.to_csv(self.session_output_folder / f"verification_results_{self.timestamp}.csv", index=False)

        self.logger.info(f"Dataset verification completed. Results: {verification_results}")
        return verification_results

    def check_unique_id_different_gender(self):
        """Check if any Unique ID has different gender values across records"""
        print("\n" + "=" * 50)
        print("CHECKING UNIQUE ID WITH DIFFERENT GENDER")
        print("=" * 50)

        if 'Unique ID' not in self.df.columns:
            print("❌ 'Unique ID' column not found!")
            return None

        if 'Geschlecht' not in self.df.columns:
            print("❌ 'Geschlecht' column not found!")
            return None

        # Group by Unique ID and check for different gender values
        gender_per_patient = self.df.groupby('Unique ID')['Geschlecht'].nunique()

        # Find patients with more than one gender value
        patients_multiple_genders = gender_per_patient[gender_per_patient > 1]

        print(f"Found {len(patients_multiple_genders)} patients with multiple gender values")

        if len(patients_multiple_genders) == 0:
            print("✅ No patients found with different gender values")
            print("✅ All patients have consistent gender across their records")

            # Create empty CSV file to show the check was performed
            empty_df = pd.DataFrame(
                columns=['Unique_ID', 'Total_Records', 'Different_Genders', 'Gender_Values', 'Records_Indices'])
            empty_df.to_csv(
                self.session_output_folder / f"patients_multiple_genders_{self.timestamp}.csv",
                index=False
            )
            print(f"✅ Created: patients_multiple_genders_{self.timestamp}.csv (empty - no issues found)")

            self.logger.info("Gender consistency check: All patients have consistent gender values")
            return []

        # Get detailed information for these patients
        problematic_patients = []

        print(f"\nDetailed analysis of patients with multiple genders:")
        print("-" * 55)

        for patient_id in patients_multiple_genders.index:
            patient_records = self.df[self.df['Unique ID'] == patient_id]
            unique_genders = patient_records['Geschlecht'].unique()

            # Remove null values for cleaner display
            unique_genders_clean = [str(g) for g in unique_genders if pd.notna(g)]

            print(f"Patient {patient_id}:")
            print(f"  Total records: {len(patient_records)}")
            print(f"  Different genders: {unique_genders_clean}")
            print(f"  Gender distribution:")

            gender_counts = patient_records['Geschlecht'].value_counts()
            for gender, count in gender_counts.items():
                print(f"    {gender}: {count} records")

            problematic_patients.append({
                'Unique_ID': patient_id,
                'Total_Records': len(patient_records),
                'Different_Genders': len(unique_genders_clean),
                'Gender_Values': ', '.join(unique_genders_clean),
                'Records_Indices': patient_records.index.tolist()
            })
            print()

        # Save detailed results
        if problematic_patients:
            problem_df = pd.DataFrame(problematic_patients)
            problem_df.to_csv(
                self.session_output_folder / f"patients_multiple_genders_{self.timestamp}.csv",
                index=False
            )

            print(f"✅ Saved: patients_multiple_genders_{self.timestamp}.csv")

            # Also save all records for these patients for detailed review
            all_problem_records = []
            for patient_id in patients_multiple_genders.index:
                patient_records = self.df[self.df['Unique ID'] == patient_id]
                all_problem_records.append(patient_records)

            if all_problem_records:
                all_records_df = pd.concat(all_problem_records, ignore_index=True)
                all_records_df.to_csv(
                    self.session_output_folder / f"all_records_multiple_genders_{self.timestamp}.csv",
                    index=False
                )
                print(f"✅ Saved: all_records_multiple_genders_{self.timestamp}.csv")

        # Summary
        total_patients = self.df['Unique ID'].nunique()
        print(f"📊 GENDER CONSISTENCY SUMMARY:")
        print(f"  Total unique patients: {total_patients}")
        print(f"  Patients with multiple genders: {len(patients_multiple_genders)}")
        if total_patients > 0:
            print(f"  Percentage affected: {len(patients_multiple_genders) / total_patients * 100:.2f}%")

        if len(patients_multiple_genders) == 0:
            print(f"  ✅ RESULT: All patients have consistent gender values!")
        else:
            print(f"  ⚠️ RESULT: Found gender inconsistencies that need review!")

        self.logger.info(
            f"Gender consistency check completed. Found {len(patients_multiple_genders)} patients with multiple gender values")

        return problematic_patients

    def save_cleaned_dataset(self):
        """Save the cleaned dataset"""
        print("\n" + "=" * 50)
        print("SAVING CLEANED DATASET")
        print("=" * 50)

        # Save cleaned dataset
        cleaned_file_path = self.session_output_folder / f"dataset_cleaned_{self.timestamp}.csv"
        self.df.to_csv(cleaned_file_path, index=False)

        print(f"✅ Cleaned dataset saved: {cleaned_file_path}")
        print(f"📊 Final dataset shape: {self.df.shape}")

        # Save cleaning log
        if self.cleaning_log:
            cleaning_log_df = pd.DataFrame(self.cleaning_log)
            cleaning_log_df.to_csv(self.session_output_folder / f"cleaning_log_{self.timestamp}.csv", index=False)
            print(f"✅ Cleaning log saved: cleaning_log_{self.timestamp}.csv")

        self.logger.info(f"Cleaned dataset saved to {cleaned_file_path}")

        return cleaned_file_path

    def run_complete_cleaning(self):
        """Run the complete data cleaning process"""
        print("🚀 Starting Complete Data Cleaning Process...")

        try:
            # Load Step 1 results
            self.load_step1_results()

            # Execute cleaning steps
            self.remove_complete_duplicates()
            self.fix_null_schadennummer()
            self.remove_hash_column_duplicates()
            self.remove_schadennummer_column()

            # Verify and save
            verification_results = self.verify_cleaned_dataset()
            gender_check_results = self.check_unique_id_different_gender()
            cleaned_file_path = self.save_cleaned_dataset()

            # Final summary
            print("\n" + "=" * 50)
            print("DATA CLEANING COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            print(f"📁 Cleaned dataset: {cleaned_file_path}")
            print(f"📁 Logs: {self.session_log_folder}")
            print(f"📁 Results: {self.session_output_folder}")

            # Check if dataset is ready for next step
            if (verification_results.get('remaining_duplicates', 0) == 0 and
                    verification_results.get('missing_unique_id', 0) == 0):
                print("\n✅ Dataset is ready for Step 3 (Logistic Regression)!")
            else:
                print("\n⚠️ Dataset may need additional cleaning before Step 3")

            self.logger.info("Complete data cleaning process finished successfully")
            return cleaned_file_path

        except Exception as e:
            print(f"❌ Error during cleaning process: {str(e)}")
            self.logger.error(f"Error during cleaning process: {str(e)}")
            raise


# Usage example:
if __name__ == "__main__":
    # Load environment variables
    dataset_path = os.getenv('DATASET', 'path/to/your/dataset.xlsx')
    log_folder = os.getenv('LOG_FOLDER', 'logs')
    output_folder = os.getenv('OUTPUT_FOLDER', 'output')

    # Use the most recent step1 output folder
    step1_output_folder = f"{output_folder}/step1_dataset_analysis_latest"

    # Initialize and run cleaning
    cleaner = DataCleaner(dataset_path, step1_output_folder, log_folder, output_folder)
    cleaned_file_path = cleaner.run_complete_cleaning()