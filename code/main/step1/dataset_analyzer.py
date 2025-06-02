import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
from datetime import datetime
from pathlib import Path
import warnings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

warnings.filterwarnings('ignore')


class DatasetAnalyzer:
    def __init__(self, dataset_path, log_folder, output_folder, plot_folder, headers_file=None):
        """
        Initialize the DatasetAnalyzer with environment paths

        Args:
            dataset_path: Path to the main dataset
            log_folder: Folder for log files
            output_folder: Folder for output files
            plot_folder: Folder for plot files
            headers_file: Optional path to file with column headers/descriptions
        """
        self.dataset_path = dataset_path
        self.log_folder = Path(log_folder)
        self.output_folder = Path(output_folder)
        self.plot_folder = Path(plot_folder)
        self.headers_file = headers_file

        # Create timestamp for this analysis session
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_folder = f"step1_dataset_analysis_{self.timestamp}"

        # Create session-specific folders
        self.session_log_folder = self.log_folder / self.session_folder
        self.session_output_folder = self.output_folder / self.session_folder
        self.session_plot_folder = self.plot_folder / self.session_folder

        # Create directories
        for folder in [self.session_log_folder, self.session_output_folder, self.session_plot_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Load dataset and headers
        self.df = None
        self.headers_info = None
        self.load_dataset()
        self.load_headers_info()

    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.session_log_folder / f"analysis_log_{self.timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Dataset analysis started at {datetime.now()}")

    def load_headers_info(self):
        """Load column headers information if available"""
        if self.headers_file and Path(self.headers_file).exists():
            try:
                if self.headers_file.endswith('.csv'):
                    self.headers_info = pd.read_csv(self.headers_file)
                elif self.headers_file.endswith(('.xlsx', '.xls')):
                    self.headers_info = pd.read_excel(self.headers_file)

                self.logger.info(f"Headers file loaded: {self.headers_info.shape}")
                print(f"✅ Headers file loaded: {self.headers_info.shape[0]} rows, {self.headers_info.shape[1]} columns")

                # Display headers info
                print("\nColumn Headers Information:")
                print("-" * 30)
                print(self.headers_info.head())

            except Exception as e:
                self.logger.warning(f"Could not load headers file: {str(e)}")
                print(f"⚠️ Could not load headers file: {str(e)}")
        else:
            if self.headers_file:
                self.logger.warning(f"Headers file not found: {self.headers_file}")
                print(f"⚠️ Headers file not found: {self.headers_file}")

    def load_dataset(self):
        """Load the dataset from the specified path"""
        try:
            if self.dataset_path.endswith('.xlsx') or self.dataset_path.endswith('.xls'):
                self.df = pd.read_excel(self.dataset_path)
            elif self.dataset_path.endswith('.csv'):
                self.df = pd.read_csv(self.dataset_path)
            else:
                raise ValueError("Unsupported file format. Please use .xlsx, .xls, or .csv")

            self.logger.info(f"Dataset loaded successfully. Shape: {self.df.shape}")
            print(f"✅ Dataset loaded: {self.df.shape[0]} rows, {self.df.shape[1]} columns")

        except Exception as e:
            self.logger.error(f"Error loading dataset: {str(e)}")
            raise

    def basic_info(self):
        """Get basic information about the dataset"""
        print("=" * 50)
        print("BASIC DATASET INFORMATION")
        print("=" * 50)

        info_dict = {
            'Dataset Shape': self.df.shape,
            'Memory Usage': f"{self.df.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB",
            'Column Count': len(self.df.columns),
            'Row Count': len(self.df)
        }

        for key, value in info_dict.items():
            print(f"{key}: {value}")

        print("\nColumn Names and Types:")
        print("-" * 30)
        for col in self.df.columns:
            print(f"{col}: {self.df[col].dtype}")

        # Save basic info
        info_df = pd.DataFrame(list(info_dict.items()), columns=['Metric', 'Value'])
        info_df.to_csv(self.session_output_folder / f"basic_info_{self.timestamp}.csv", index=False)

        self.logger.info("Basic information analysis completed")
        return info_dict

    def missing_values_analysis(self):
        """Analyze missing values in the dataset"""
        print("\n" + "=" * 50)
        print("MISSING VALUES ANALYSIS")
        print("=" * 50)

        missing_data = self.df.isnull().sum()
        missing_percent = (missing_data / len(self.df)) * 100

        missing_df = pd.DataFrame({
            'Column': missing_data.index,
            'Missing_Count': missing_data.values,
            'Missing_Percentage': missing_percent.values
        }).sort_values('Missing_Percentage', ascending=False)

        print(missing_df)

        # Save missing values analysis
        missing_df.to_csv(self.session_output_folder / f"missing_values_{self.timestamp}.csv", index=False)

        # Plot missing values
        if missing_data.sum() > 0:
            plt.figure(figsize=(12, 6))
            sns.heatmap(self.df.isnull(), yticklabels=False, cbar=True, cmap='viridis')
            plt.title('Missing Values Heatmap')
            plt.tight_layout()
            plt.savefig(self.session_plot_folder / f"missing_values_heatmap_{self.timestamp}.png", dpi=300,
                        bbox_inches='tight')
            plt.show()

        self.logger.info("Missing values analysis completed")
        return missing_df

    def validate_expected_columns(self):
        """Validate that expected columns exist in the dataset"""
        print("\n" + "=" * 50)
        print("COLUMN VALIDATION")
        print("=" * 50)

        expected_columns = {
            'Unique ID': 'Patient identifier',
            'Schadennummer': 'Original patient number (can be dropped for privacy)',
            'StatusFL': 'Function limitation status (verbessert=2, unverändert=1, verschlechtert=0)',
            'StatusP': 'Pain status (verbessert=2, unverändert=1, verschlechtert=0)',
            'FLScore': 'Function limitation score (0-4)',
            'P': 'Pain score (0-4)',
            'Alter-Unfall': 'Age at accident date'
        }

        found_columns = []
        missing_columns = []

        print("Expected Columns Check:")
        print("-" * 30)

        for col, description in expected_columns.items():
            if col in self.df.columns:
                found_columns.append(col)
                print(f"✅ {col}: {description}")
            else:
                missing_columns.append(col)
                print(f"❌ {col}: {description} - MISSING")

        print(f"\nSummary: {len(found_columns)}/{len(expected_columns)} expected columns found")

        # Check for similar column names
        if missing_columns:
            print(f"\nChecking for similar column names:")
            for missing_col in missing_columns:
                similar_cols = [col for col in self.df.columns if
                                missing_col.lower() in col.lower() or col.lower() in missing_col.lower()]
                if similar_cols:
                    print(f"  '{missing_col}' might be: {similar_cols}")

        validation_results = {
            'found_columns': found_columns,
            'missing_columns': missing_columns,
            'all_columns': list(self.df.columns)
        }

        # Save validation results
        validation_df = pd.DataFrame([
                                         {'Column': col, 'Status': 'Found', 'Description': expected_columns[col]} for
                                         col in found_columns
                                     ] + [
                                         {'Column': col, 'Status': 'Missing', 'Description': expected_columns[col]} for
                                         col in missing_columns
                                     ])

        validation_df.to_csv(self.session_output_folder / f"column_validation_{self.timestamp}.csv", index=False)

        self.logger.info(f"Column validation completed. Found: {len(found_columns)}, Missing: {len(missing_columns)}")
        return validation_results

    def data_types_analysis(self):
        """Analyze data types and unique values"""
        print("\n" + "=" * 50)
        print("DATA TYPES AND UNIQUE VALUES ANALYSIS")
        print("=" * 50)

        dtype_analysis = []

        for col in self.df.columns:
            unique_count = self.df[col].nunique()
            sample_values = self.df[col].dropna().unique()[:5] if len(self.df[col].dropna().unique()) > 0 else []

            dtype_analysis.append({
                'Column': col,
                'Data_Type': str(self.df[col].dtype),
                'Unique_Count': unique_count,
                'Sample_Values': str(list(sample_values))
            })

            print(f"\n{col}:")
            print(f"  Type: {self.df[col].dtype}")
            print(f"  Unique values: {unique_count}")
            print(f"  Sample values: {list(sample_values)}")

        dtype_df = pd.DataFrame(dtype_analysis)
        dtype_df.to_csv(self.session_output_folder / f"data_types_analysis_{self.timestamp}.csv", index=False)

        self.logger.info("Data types analysis completed")
        return dtype_df

    def analyze_duplications(self):
        """Analyze duplications: complete identical records and patients with multiple visits on same day"""
        print("\n" + "=" * 50)
        print("DUPLICATION ANALYSIS")
        print("=" * 50)

        # 1. Complete identical records
        print("1. COMPLETE IDENTICAL RECORDS:")
        print("-" * 30)

        # Find completely identical rows
        complete_duplicates = self.df.duplicated()
        complete_duplicate_count = complete_duplicates.sum()

        print(f"Total complete duplicate rows: {complete_duplicate_count}")

        if complete_duplicate_count > 0:
            # Get the duplicate rows
            duplicate_rows = self.df[complete_duplicates]
            print(f"Saving {len(duplicate_rows)} duplicate rows to CSV...")

            # Save only the duplicate rows (not the originals)
            duplicate_rows.to_csv(self.session_output_folder / f"complete_identical_rows_{self.timestamp}.csv",
                                  index=False)
            print(f"✅ Saved: complete_identical_rows_{self.timestamp}.csv")
        else:
            print("✅ No complete duplicate records found")
            # Create empty file
            pd.DataFrame().to_csv(self.session_output_folder / f"complete_identical_rows_{self.timestamp}.csv",
                                  index=False)

        # 2. Patients with multiple visits on same day
        print(f"\n2. PATIENTS WITH MULTIPLE VISITS ON SAME DAY:")
        print("-" * 45)

        # Look for date columns
        possible_date_columns = []
        for col in self.df.columns:
            col_lower = col.lower()
            if any(date_word in col_lower for date_word in ['date', 'datum', 'zeit', 'time', 'kontakt', 'contact']):
                possible_date_columns.append(col)

        print(f"Date columns found: {possible_date_columns}")

        all_multiple_visit_patients = set()

        if possible_date_columns and 'Unique ID' in self.df.columns:
            for date_col in possible_date_columns:
                print(f"\n📅 Checking {date_col}...")

                try:
                    # Convert to datetime and extract just the date part
                    date_series = pd.to_datetime(self.df[date_col], errors='coerce')
                    date_only = date_series.dt.date

                    # Group by patient and date to find multiple visits on same day
                    patient_date_groups = self.df.groupby(['Unique ID', date_only]).size()
                    multiple_visits_same_day = patient_date_groups[patient_date_groups > 1]

                    print(f"  Found {len(multiple_visits_same_day)} patient-day combinations with multiple visits")

                    if len(multiple_visits_same_day) > 0:
                        # Get unique patient IDs with multiple visits
                        patients_with_multiple_visits = set(
                            multiple_visits_same_day.index.get_level_values('Unique ID'))
                        all_multiple_visit_patients.update(patients_with_multiple_visits)
                        print(f"  Unique patients with multiple visits: {len(patients_with_multiple_visits)}")

                except Exception as e:
                    print(f"  ❌ Could not analyze {date_col}: {str(e)}")

        # Save unique patient IDs with multiple visits on same day
        if all_multiple_visit_patients:
            multiple_visit_df = pd.DataFrame({
                'Unique_ID': sorted(list(all_multiple_visit_patients))
            })
            multiple_visit_df.to_csv(
                self.session_output_folder / f"patients_multiple_visits_same_day_{self.timestamp}.csv", index=False)
            print(f"\n✅ Saved: patients_multiple_visits_same_day_{self.timestamp}.csv")
            print(f"   Total unique patients with multiple visits on same day: {len(all_multiple_visit_patients)}")
        else:
            print("\n✅ No patients with multiple visits on same day found")
            # Create empty file
            pd.DataFrame({'Unique_ID': []}).to_csv(
                self.session_output_folder / f"patients_multiple_visits_same_day_{self.timestamp}.csv", index=False)

        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"  Complete duplicate rows: {complete_duplicate_count}")
        print(f"  Patients with multiple visits same day: {len(all_multiple_visit_patients)}")

        self.logger.info(
            f"Duplication analysis completed. Files created: complete_identical_rows and patients_multiple_visits_same_day")

        return {
            'complete_duplicates': complete_duplicate_count,
            'multiple_visit_patients': len(all_multiple_visit_patients)
        }

    def analyze_important_columns_missing(self):
        """Check if any patient has 100% missing values in important columns"""
        print("\n" + "=" * 50)
        print("IMPORTANT COLUMNS - 100% MISSING VALUES ANALYSIS")
        print("=" * 50)

        # Define important columns
        important_cols = [
            'Alter-Unfall', 'Kontaktdatum', 'FLScore', 'StatusFL',
            'P', 'StatusP', 'Verlauf_entspricht_NBE', 'Geschlecht', 'birthdate'
        ]

        print(f"Checking important columns: {important_cols}")

        if 'Unique ID' not in self.df.columns:
            print("❌ 'Unique ID' column not found!")
            return None

        # Check which important columns exist in the dataset
        existing_important_cols = []
        missing_important_cols = []

        for col in important_cols:
            if col in self.df.columns:
                existing_important_cols.append(col)
            else:
                missing_important_cols.append(col)

        print(f"\n📋 Column availability:")
        print(f"  ✅ Found: {existing_important_cols}")
        if missing_important_cols:
            print(f"  ❌ Missing from dataset: {missing_important_cols}")

        if not existing_important_cols:
            print("❌ None of the important columns found in dataset!")
            return None

        # Analyze each existing important column
        patients_100_missing = {}

        print(f"\n🔍 Analyzing patients with 100% missing values:")
        print("-" * 50)

        for col in existing_important_cols:
            print(f"\n📊 {col}:")

            # Group by patient and check if all values are missing
            patient_groups = self.df.groupby('Unique ID')[col]

            patients_all_missing = []
            for patient_id, patient_data in patient_groups:
                # Check if all values for this patient are null/missing
                if patient_data.isna().all():
                    patients_all_missing.append({
                        'Unique_ID': patient_id,
                        'Total_Records': len(patient_data),
                        'Missing_Count': patient_data.isna().sum()
                    })

            print(f"  Patients with 100% missing {col}: {len(patients_all_missing)}")

            if patients_all_missing:
                patients_100_missing[col] = patients_all_missing
                print(f"  Examples (first 5):")
                for i, patient_info in enumerate(patients_all_missing[:5]):
                    print(
                        f"    Patient {patient_info['Unique_ID']}: {patient_info['Total_Records']} records, all missing")
            else:
                print(f"  ✅ No patients with 100% missing {col}")

        # Create summary CSV with all patients who have 100% missing in any important column
        all_problematic_patients = []

        for col, patients_list in patients_100_missing.items():
            for patient_info in patients_list:
                all_problematic_patients.append({
                    'Unique_ID': patient_info['Unique_ID'],
                    'Missing_Column': col,
                    'Total_Records': patient_info['Total_Records'],
                    'Missing_Count': patient_info['Missing_Count']
                })

        if all_problematic_patients:
            # Save to CSV
            problematic_df = pd.DataFrame(all_problematic_patients)
            problematic_df.to_csv(
                self.session_output_folder / f"patients_100_missing_important_cols_{self.timestamp}.csv",
                index=False
            )

            print(f"\n📁 Saved: patients_100_missing_important_cols_{self.timestamp}.csv")
            print(f"   Total problematic patient-column combinations: {len(all_problematic_patients)}")

            # Show summary by column
            print(f"\n📊 Summary by column:")
            summary_by_col = problematic_df.groupby('Missing_Column')['Unique_ID'].nunique().sort_values(
                ascending=False)
            for col, count in summary_by_col.items():
                print(f"  {col}: {count} patients")

            # Show patients with multiple important columns missing
            patients_multi_missing = problematic_df.groupby('Unique_ID')['Missing_Column'].count()
            patients_multi_missing = patients_multi_missing[patients_multi_missing > 1].sort_values(ascending=False)

            if len(patients_multi_missing) > 0:
                print(f"\n⚠️ Patients with multiple important columns 100% missing:")
                for patient_id, missing_count in patients_multi_missing.head(10).items():
                    missing_cols = problematic_df[problematic_df['Unique_ID'] == patient_id]['Missing_Column'].tolist()
                    print(f"  Patient {patient_id}: {missing_count} columns ({', '.join(missing_cols)})")
        else:
            print(f"\n✅ No patients found with 100% missing values in any important column!")
            # Create empty CSV
            pd.DataFrame(columns=['Unique_ID', 'Missing_Column', 'Total_Records', 'Missing_Count']).to_csv(
                self.session_output_folder / f"patients_100_missing_important_cols_{self.timestamp}.csv",
                index=False
            )

        # Overall summary
        print(f"\n📋 OVERALL SUMMARY:")
        print(f"  Important columns analyzed: {len(existing_important_cols)}")
        print(f"  Columns with patients having 100% missing: {len(patients_100_missing)}")
        print(f"  Total patient-column problems: {len(all_problematic_patients)}")

        unique_problematic_patients = len(
            set(item['Unique_ID'] for item in all_problematic_patients)) if all_problematic_patients else 0
        total_patients = self.df['Unique ID'].nunique()
        print(
            f"  Unique patients with problems: {unique_problematic_patients}/{total_patients} ({unique_problematic_patients / total_patients * 100:.1f}%)")

        self.logger.info(
            f"Important columns missing analysis completed. Found {len(all_problematic_patients)} patient-column problems")

    def create_id_translation(self):
        """Create translation file between Unique ID and Schadennummer"""
        print("\n" + "=" * 50)
        print("ID TRANSLATION FILE")
        print("=" * 50)

        if 'Unique ID' not in self.df.columns:
            print("❌ 'Unique ID' column not found!")
            return None

        if 'Schadennummer' not in self.df.columns:
            print("❌ 'Schadennummer' column not found!")
            return None

        # Create unique mapping between Unique ID and Schadennummer
        id_translation = self.df[['Unique ID', 'Schadennummer']].drop_duplicates().sort_values('Unique ID')

        print(f"Created translation for {len(id_translation)} unique patients")
        print("Sample translations:")
        print(id_translation.head(10))

        # Save translation file
        id_translation.to_csv(
            self.session_output_folder / f"id_translation_{self.timestamp}.csv",
            index=False
        )

        print(f"\n✅ Saved: id_translation_{self.timestamp}.csv")

        # Verify no duplicates in mapping
        unique_id_counts = id_translation['Unique ID'].value_counts()
        schadennummer_counts = id_translation['Schadennummer'].value_counts()

        if (unique_id_counts > 1).any():
            print("⚠️ Warning: Some Unique IDs map to multiple Schadennummers!")
            duplicates = unique_id_counts[unique_id_counts > 1]
            print(f"   Problematic Unique IDs: {duplicates.index.tolist()}")

        if (schadennummer_counts > 1).any():
            print("⚠️ Warning: Some Schadennummers map to multiple Unique IDs!")
            duplicates = schadennummer_counts[schadennummer_counts > 1]
            print(f"   Problematic Schadennummers: {duplicates.index.tolist()}")

        if (unique_id_counts == 1).all() and (schadennummer_counts == 1).all():
            print("✅ Perfect 1:1 mapping between Unique ID and Schadennummer")

        self.logger.info(f"ID translation file created with {len(id_translation)} mappings")
        return id_translation

    def check_column_hash_duplicates(self):
        """Check for duplicates in the # column and return Schadennummer values in SQL format"""
        print("\n" + "=" * 50)
        print("CHECKING DUPLICATES IN # COLUMN")
        print("=" * 50)

        if '#' not in self.df.columns:
            print("❌ '#' column not found!")
            return None

        if 'Schadennummer' not in self.df.columns:
            print("❌ 'Schadennummer' column not found!")
            return None

        # Check for duplicates in # column
        hash_duplicates = self.df['#'].duplicated(keep=False)
        duplicate_count = hash_duplicates.sum()

        print(f"Found {duplicate_count} rows with duplicate # values")

        if duplicate_count == 0:
            print("✅ No duplicates found in # column")
            return "-- No duplicates found in # column"

        # Get rows with duplicate # values
        duplicate_rows = self.df[hash_duplicates]

        # Show some examples
        print(f"\nSample duplicate # values:")
        duplicate_hash_values = duplicate_rows['#'].value_counts().head(10)
        for hash_val, count in duplicate_hash_values.items():
            print(f"  # = {hash_val}: appears {count} times")

        # Get unique Schadennummer values for rows with duplicate #
        schadennummer_with_duplicate_hash = duplicate_rows['Schadennummer'].unique()

        # Remove any null values from the list
        schadennummer_with_duplicate_hash = [str(x) for x in schadennummer_with_duplicate_hash if pd.notna(x)]

        print(f"\nFound {len(schadennummer_with_duplicate_hash)} unique Schadennummer values with duplicate # values")
        print(f"Sample Schadennummer values: {schadennummer_with_duplicate_hash[:5]}")

        if len(schadennummer_with_duplicate_hash) == 0:
            print("✅ No valid Schadennummer values with duplicate #")
            return "-- No valid Schadennummer values with duplicate #"

        # Format as SQL IN clause
        sql_format = "IN ('" + "','".join(schadennummer_with_duplicate_hash) + "')"

        print(f"\nSQL format:")
        print(f"{sql_format}")

        # Save detailed analysis
        duplicate_analysis = duplicate_rows[['#', 'Schadennummer', 'Unique ID']].sort_values('#')
        duplicate_analysis.to_csv(self.session_output_folder / f"hash_duplicates_details_{self.timestamp}.csv",
                                  index=False)

        # Save SQL format to file
        with open(self.session_output_folder / f"schadennummer_duplicate_hash_{self.timestamp}.txt", 'w') as f:
            f.write(sql_format)

        print(f"\n✅ Saved: hash_duplicates_details_{self.timestamp}.csv")
        print(f"✅ Saved: schadennummer_duplicate_hash_{self.timestamp}.txt")

        self.logger.info(
            f"Found {duplicate_count} rows with duplicate # values, {len(schadennummer_with_duplicate_hash)} unique Schadennummer affected")

        return sql_format

        return {
            'existing_important_cols': existing_important_cols,
            'missing_important_cols': missing_important_cols,
            'patients_100_missing': patients_100_missing,
            'total_problems': len(all_problematic_patients),
            'unique_problematic_patients': unique_problematic_patients
        }
        """Analyze data types and unique values"""
        print("\n" + "=" * 50)
        print("DATA TYPES AND UNIQUE VALUES ANALYSIS")
        print("=" * 50)

        dtype_analysis = []

        for col in self.df.columns:
            unique_count = self.df[col].nunique()
            sample_values = self.df[col].dropna().unique()[:5] if len(self.df[col].dropna().unique()) > 0 else []

            dtype_analysis.append({
                'Column': col,
                'Data_Type': str(self.df[col].dtype),
                'Unique_Count': unique_count,
                'Sample_Values': str(list(sample_values))
            })

            print(f"\n{col}:")
            print(f"  Type: {self.df[col].dtype}")
            print(f"  Unique values: {unique_count}")
            print(f"  Sample values: {list(sample_values)}")

        dtype_df = pd.DataFrame(dtype_analysis)
        dtype_df.to_csv(self.session_output_folder / f"data_types_analysis_{self.timestamp}.csv", index=False)

        self.logger.info("Data types analysis completed")
        return dtype_df

    def identify_patient_patterns(self):
        """Analyze patient patterns based on Unique ID"""
        print("\n" + "=" * 50)
        print("PATIENT PATTERNS ANALYSIS")
        print("=" * 50)

        if 'Unique ID' in self.df.columns:
            # Count calls per patient
            calls_per_patient = self.df['Unique ID'].value_counts().sort_values(ascending=False)

            pattern_stats = {
                'Total Unique Patients': self.df['Unique ID'].nunique(),
                'Total Calls': len(self.df),
                'Average Calls per Patient': calls_per_patient.mean(),
                'Max Calls per Patient': calls_per_patient.max(),
                'Min Calls per Patient': calls_per_patient.min(),
                'Patients with Single Call': (calls_per_patient == 1).sum(),
                'Patients with Multiple Calls': (calls_per_patient > 1).sum()
            }

            print("Patient Call Patterns:")
            for key, value in pattern_stats.items():
                print(f"  {key}: {value}")

            # Plot distribution of calls per patient
            plt.figure(figsize=(12, 6))
            calls_per_patient.hist(bins=20, edgecolor='black', alpha=0.7)
            plt.title('Distribution of Calls per Patient')
            plt.xlabel('Number of Calls')
            plt.ylabel('Number of Patients')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(self.session_plot_folder / f"calls_per_patient_{self.timestamp}.png", dpi=300,
                        bbox_inches='tight')
            plt.show()

            # Save patient patterns
            pattern_df = pd.DataFrame(list(pattern_stats.items()), columns=['Metric', 'Value'])
            pattern_df.to_csv(self.session_output_folder / f"patient_patterns_{self.timestamp}.csv", index=False)

            self.logger.info("Patient patterns analysis completed")
            return pattern_stats
        else:
            print("❌ 'Unique ID' column not found!")
            self.logger.warning("Unique ID column not found in dataset")
            return None

    def analyze_status_columns(self):
        """Analyze StatusFL and StatusP columns"""
        print("\n" + "=" * 50)
        print("STATUS COLUMNS ANALYSIS")
        print("=" * 50)

        status_columns = ['StatusFL', 'StatusP']
        status_analysis = {}

        for col in status_columns:
            if col in self.df.columns:
                print(f"\n{col} Analysis:")
                value_counts = self.df[col].value_counts()
                print(value_counts)

                status_analysis[col] = value_counts.to_dict()

                # Plot status distribution
                plt.figure(figsize=(10, 6))
                value_counts.plot(kind='bar', color=['green', 'orange', 'red'])
                plt.title(f'{col} Distribution')
                plt.xlabel('Status')
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(self.session_plot_folder / f"{col.lower()}_distribution_{self.timestamp}.png", dpi=300,
                            bbox_inches='tight')
                plt.show()
            else:
                print(f"❌ {col} column not found!")
                self.logger.warning(f"{col} column not found in dataset")

        # Save status analysis
        if status_analysis:
            status_df = pd.DataFrame([(col, status, count) for col, statuses in status_analysis.items()
                                      for status, count in statuses.items()],
                                     columns=['Column', 'Status', 'Count'])
            status_df.to_csv(self.session_output_folder / f"status_analysis_{self.timestamp}.csv", index=False)

        self.logger.info("Status columns analysis completed")
        return status_analysis

    def analyze_score_columns(self):
        """Analyze FLScore and P columns (P is the pain score column)"""
        print("\n" + "=" * 50)
        print("SCORE COLUMNS ANALYSIS")
        print("=" * 50)

        score_columns = ['FLScore', 'P']
        score_analysis = {}

        for col in score_columns:
            if col in self.df.columns:
                print(f"\n{col} Analysis:")
                print(f"  Range: {self.df[col].min()} - {self.df[col].max()}")
                print(f"  Mean: {self.df[col].mean():.2f}")
                print(f"  Median: {self.df[col].median():.2f}")
                print(f"  Std: {self.df[col].std():.2f}")

                value_counts = self.df[col].value_counts().sort_index()
                print(f"  Value distribution:\n{value_counts}")

                score_analysis[col] = {
                    'min': self.df[col].min(),
                    'max': self.df[col].max(),
                    'mean': self.df[col].mean(),
                    'median': self.df[col].median(),
                    'std': self.df[col].std(),
                    'distribution': value_counts.to_dict()
                }

                # Plot score distribution
                plt.figure(figsize=(10, 6))
                value_counts.plot(kind='bar', color='skyblue', edgecolor='black')
                plt.title(f'{col} Distribution')
                plt.xlabel('Score')
                plt.ylabel('Count')
                plt.tight_layout()
                plt.savefig(self.session_plot_folder / f"{col.lower()}_distribution_{self.timestamp}.png", dpi=300,
                            bbox_inches='tight')
                plt.show()
            else:
                print(f"❌ {col} column not found!")
                self.logger.warning(f"{col} column not found in dataset")

        self.logger.info("Score columns analysis completed")
        return score_analysis

    def generate_summary_report(self):
        """Generate a minimal summary report without correlation matrix"""
        print("\n" + "=" * 50)
        print("GENERATING FINAL REPORT")
        print("=" * 50)

        print(f"✅ Analysis completed! Results saved in:")
        print(f"   📁 Logs: {self.session_log_folder}")
        print(f"   📁 Output: {self.session_output_folder}")
        print(f"   📁 Plots: {self.session_plot_folder}")

        self.logger.info("Analysis completed successfully")

    def run_complete_analysis(self):
        """Run the complete dataset analysis"""
        print("🚀 Starting Complete Dataset Analysis...")

        try:
            # Run only the required analysis steps
            self.basic_info()  # ✅ Keep - basic dataset info
            self.validate_expected_columns()  # ✅ Keep - column validation
            self.missing_values_analysis()  # ✅ Keep - missing values analysis
            self.data_types_analysis()  # ✅ Keep - data types analysis
            self.analyze_important_columns_missing()  # ✅ Keep - patients 100% missing important cols
            self.analyze_duplications()  # ✅ Keep - complete identical rows + multiple visits same day
            self.create_id_translation()  # ✅ Keep - unique ID to Schadennummer mapping
            self.check_column_hash_duplicates()  # ✅ New - check duplicates in # column
            self.generate_summary_report()  # ✅ Keep - final summary (simplified)

            print("\n✅ Complete analysis finished successfully!")
            self.logger.info("Complete dataset analysis finished successfully")

        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            self.logger.error(f"Error during analysis: {str(e)}")
            raise


# Usage example:
if __name__ == "__main__":
    # Load environment variables
    dataset_path = os.getenv('DATASET', 'path/to/your/dataset.xlsx')
    log_folder = os.getenv('LOG_FOLDER', 'logs')
    output_folder = os.getenv('OUTPUT_FOLDER', 'output')
    plot_folder = os.getenv('PLOT_FOLDER', 'plots')

    # Initialize and run analysis
    analyzer = DatasetAnalyzer(dataset_path, log_folder, output_folder, plot_folder)
    analyzer.run_complete_analysis()