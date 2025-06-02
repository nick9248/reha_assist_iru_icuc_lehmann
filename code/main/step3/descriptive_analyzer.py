import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import os
import logging
from datetime import datetime
from pathlib import Path
import warnings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

warnings.filterwarnings('ignore')


class DescriptiveAnalyzer:
    def __init__(self, cleaned_dataset_path, log_folder, output_folder, plot_folder):
        """
        Initialize the DescriptiveAnalyzer for Step 3

        Args:
            cleaned_dataset_path: Path to the cleaned dataset from Step 2
            log_folder: Folder for log files
            output_folder: Folder for analysis output
            plot_folder: Folder for plots
        """
        self.dataset_path = cleaned_dataset_path
        self.log_folder = Path(log_folder)
        self.output_folder = Path(output_folder)
        self.plot_folder = Path(plot_folder)

        # Create timestamp for this analysis session
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_folder = f"step3_descriptive_analysis_{self.timestamp}"

        # Create session-specific folders
        self.session_log_folder = self.log_folder / self.session_folder
        self.session_output_folder = self.output_folder / self.session_folder
        self.session_plot_folder = self.plot_folder / self.session_folder

        # Create directories
        for folder in [self.session_log_folder, self.session_output_folder, self.session_plot_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Initialize data containers
        self.df = None
        self.unique_patients_df = None
        self.exclusion_log = []
        self.analysis_results = {}

        # Load dataset
        self.load_dataset()

    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.session_log_folder / f"descriptive_analysis_log_{self.timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Descriptive analysis started at {datetime.now()}")

    def load_dataset(self):
        """Load the cleaned dataset from Step 2"""
        try:
            if self.dataset_path.endswith('.xlsx') or self.dataset_path.endswith('.xls'):
                self.df = pd.read_excel(self.dataset_path)
            elif self.dataset_path.endswith('.csv'):
                self.df = pd.read_csv(self.dataset_path)
            else:
                raise ValueError("Unsupported file format. Please use .xlsx, .xls, or .csv")

            self.logger.info(f"Cleaned dataset loaded successfully. Shape: {self.df.shape}")
            print(f"✅ Cleaned dataset loaded: {self.df.shape[0]} rows, {self.df.shape[1]} columns")

        except Exception as e:
            self.logger.error(f"Error loading cleaned dataset: {str(e)}")
            raise

    def log_exclusion(self, patient_id, issue, value, reason):
        """Log exclusions and anomalies"""
        self.exclusion_log.append({
            'Patient_ID': patient_id,
            'Issue': issue,
            'Value': value,
            'Reason': reason,
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def get_unique_patients_data(self):
        """
        Extract first visit per patient for demographic analysis
        Log any patients with missing demographic data
        """
        print("\n" + "=" * 50)
        print("EXTRACTING UNIQUE PATIENTS DATA")
        print("=" * 50)

        if 'Unique ID' not in self.df.columns:
            raise ValueError("'Unique ID' column not found in dataset")

        # Get first visit per patient
        self.unique_patients_df = self.df.groupby('Unique ID').first().reset_index()

        total_visits = len(self.df)
        unique_patients = len(self.unique_patients_df)

        print(f"📊 Data extraction summary:")
        print(f"  Total visits in dataset: {total_visits}")
        print(f"  Unique patients: {unique_patients}")
        print(f"  Average visits per patient: {total_visits / unique_patients:.2f}")

        # Check for patients with invalid Unique ID (only null values, 0 is valid)
        invalid_unique_id = self.df['Unique ID'].isnull()
        if invalid_unique_id.sum() > 0:
            invalid_indices = self.df[invalid_unique_id].index.tolist()
            for idx in invalid_indices:
                self.log_exclusion(
                    patient_id=f"Row_{idx}",
                    issue="Invalid_Unique_ID",
                    value=self.df.loc[idx, 'Unique ID'],
                    reason="Null Unique ID"
                )
            print(f"⚠️ Found {invalid_unique_id.sum()} rows with invalid Unique ID")

        self.logger.info(f"Unique patients data extracted. {unique_patients} patients from {total_visits} visits")
        return self.unique_patients_df

    def analyze_total_cases(self):
        """
        Count total unique patients advised
        Log: patients with invalid Unique ID
        """
        print("\n" + "=" * 50)
        print("ANALYZING TOTAL CASES ADVISED")
        print("=" * 50)

        # Count valid unique patients (including ID = 0)
        valid_patients = self.unique_patients_df[
            self.unique_patients_df['Unique ID'].notna()
        ]

        total_cases = len(valid_patients)
        excluded_cases = len(self.unique_patients_df) - total_cases

        print(f"📊 Total Cases Analysis:")
        print(f"  Total unique patients advised: {total_cases}")
        print(f"  (Includes patient with Unique ID = 0)")
        if excluded_cases > 0:
            print(f"  Excluded patients (null ID): {excluded_cases}")

        # Save results
        results = {
            'Total_Cases_Advised': total_cases,
            'Excluded_Null_ID': excluded_cases,
            'Analysis_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.analysis_results['total_cases'] = results

        # Save to CSV
        results_df = pd.DataFrame([results])
        results_df.to_csv(
            self.session_output_folder / f"total_cases_results_{self.timestamp}.csv",
            index=False
        )

        self.logger.info(f"Total cases analysis completed. {total_cases} unique patients advised")
        return results

    def analyze_gender_distribution(self):
        """
        Gender analysis with Chi-Square Goodness of Fit test
        Log: patients with missing/invalid gender
        Create pie chart with German labels
        """
        print("\n" + "=" * 50)
        print("ANALYZING GENDER DISTRIBUTION")
        print("=" * 50)

        if 'Geschlecht' not in self.unique_patients_df.columns:
            raise ValueError("'Geschlecht' column not found in dataset")

        # Clean gender data
        valid_genders = ['m', 'w']
        gender_data = self.unique_patients_df['Geschlecht'].copy()

        # Log invalid/missing gender values
        invalid_gender_mask = ~gender_data.isin(valid_genders) | gender_data.isnull()
        invalid_count = invalid_gender_mask.sum()

        if invalid_count > 0:
            invalid_patients = self.unique_patients_df[invalid_gender_mask]['Unique ID'].tolist()
            for patient_id in invalid_patients:
                invalid_value = self.unique_patients_df[
                    self.unique_patients_df['Unique ID'] == patient_id
                    ]['Geschlecht'].iloc[0]
                self.log_exclusion(
                    patient_id=patient_id,
                    issue="Invalid_Gender",
                    value=invalid_value,
                    reason=f"Gender value not in {valid_genders}"
                )

        # Filter to valid gender data
        valid_gender_data = gender_data[~invalid_gender_mask]

        # Count gender distribution
        gender_counts = valid_gender_data.value_counts()
        total_valid = len(valid_gender_data)

        print(f"📊 Gender Distribution Analysis:")
        print(f"  Total patients with valid gender: {total_valid}")
        print(f"  Männlich (m): {gender_counts.get('m', 0)} ({gender_counts.get('m', 0) / total_valid * 100:.1f}%)")
        print(f"  Weiblich (w): {gender_counts.get('w', 0)} ({gender_counts.get('w', 0) / total_valid * 100:.1f}%)")
        if invalid_count > 0:
            print(f"  Excluded (invalid gender): {invalid_count}")

        # Chi-Square Goodness of Fit Test (50:50 expected)
        if total_valid >= 5:  # Minimum sample size for Chi-Square
            observed = [gender_counts.get('m', 0), gender_counts.get('w', 0)]
            expected = [total_valid / 2, total_valid / 2]  # 50:50 distribution

            chi2_stat, p_value = stats.chisquare(observed, expected)

            print(f"\n📊 Chi-Square Goodness of Fit Test (H0: 50:50 distribution):")
            print(f"  Chi-Square statistic: {chi2_stat:.4f}")
            print(f"  P-value: {p_value:.4f}")
            print(
                f"  Result: {'Signifikant unterschiedlich' if p_value < 0.05 else 'Nicht signifikant unterschiedlich'} von Gleichverteilung (α=0.05)")
        else:
            chi2_stat, p_value = None, None
            print(f"⚠️ Sample size too small for Chi-Square test (n={total_valid})")

        # Create pie chart
        if total_valid > 0:
            plt.figure(figsize=(10, 8))

            labels = ['Männlich', 'Weiblich']
            sizes = [gender_counts.get('m', 0), gender_counts.get('w', 0)]
            colors = ['lightblue', 'lightpink']

            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('Geschlechterverteilung der Patienten', fontsize=16, fontweight='bold')
            plt.axis('equal')

            # Save plot
            plt.savefig(
                self.session_plot_folder / f"geschlechterverteilung_{self.timestamp}.png",
                dpi=300, bbox_inches='tight'
            )
            plt.show()

        # Save results
        results = {
            'Total_Valid_Patients': total_valid,
            'Male_Count': gender_counts.get('m', 0),
            'Female_Count': gender_counts.get('w', 0),
            'Male_Percentage': gender_counts.get('m', 0) / total_valid * 100 if total_valid > 0 else 0,
            'Female_Percentage': gender_counts.get('w', 0) / total_valid * 100 if total_valid > 0 else 0,
            'Excluded_Invalid_Gender': invalid_count,
            'Chi_Square_Statistic': chi2_stat,
            'Chi_Square_P_Value': p_value,
            'Significant_Difference_from_50_50': p_value < 0.05 if p_value is not None else None,
            'Analysis_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.analysis_results['gender_distribution'] = results

        # Save to CSV
        results_df = pd.DataFrame([results])
        results_df.to_csv(
            self.session_output_folder / f"gender_analysis_results_{self.timestamp}.csv",
            index=False
        )

        self.logger.info(f"Gender analysis completed. {total_valid} valid patients, Chi-Square p-value: {p_value}")
        return results

    def analyze_average_age(self):
        """
        Age analysis with anomaly detection and normality test
        Create histogram with normal overlay and box plot
        """
        print("\n" + "=" * 50)
        print("ANALYZING AVERAGE AGE")
        print("=" * 50)

        if 'Alter-Unfall' not in self.unique_patients_df.columns:
            raise ValueError("'Alter-Unfall' column not found in dataset")

        # Clean age data
        age_data = self.unique_patients_df['Alter-Unfall'].copy()

        # Log missing age values
        missing_age_mask = age_data.isnull()
        missing_count = missing_age_mask.sum()

        if missing_count > 0:
            missing_patients = self.unique_patients_df[missing_age_mask]['Unique ID'].tolist()
            for patient_id in missing_patients:
                self.log_exclusion(
                    patient_id=patient_id,
                    issue="Missing_Age",
                    value=np.nan,
                    reason="Age value is null/missing"
                )

        # Log age anomalies (< 0 or > 120)
        age_outlier_mask = (age_data < 0) | (age_data > 120)
        outlier_count = age_outlier_mask.sum()

        if outlier_count > 0:
            outlier_patients = self.unique_patients_df[age_outlier_mask]['Unique ID'].tolist()
            outlier_ages = age_data[age_outlier_mask].tolist()
            for patient_id, age in zip(outlier_patients, outlier_ages):
                self.log_exclusion(
                    patient_id=patient_id,
                    issue="Age_Outlier",
                    value=age,
                    reason=f"Age outside reasonable range (0-120): {age}"
                )

        # Filter to valid age data
        valid_age_mask = ~missing_age_mask & ~age_outlier_mask
        valid_age_data = age_data[valid_age_mask]
        total_valid = len(valid_age_data)

        if total_valid == 0:
            print("❌ No valid age data found!")
            return None

        # Calculate statistics
        age_mean = valid_age_data.mean()
        age_median = valid_age_data.median()
        age_std = valid_age_data.std()
        age_min = valid_age_data.min()
        age_max = valid_age_data.max()

        print(f"📊 Age Analysis:")
        print(f"  Total patients with valid age: {total_valid}")
        print(f"  Average age: {age_mean:.2f} years")
        print(f"  Median age: {age_median:.2f} years")
        print(f"  Standard deviation: {age_std:.2f} years")
        print(f"  Age range: {age_min:.0f} - {age_max:.0f} years")
        if missing_count > 0:
            print(f"  Excluded (missing age): {missing_count}")
        if outlier_count > 0:
            print(f"  Excluded (age outliers): {outlier_count}")

        # Shapiro-Wilk normality test
        if total_valid >= 3:  # Minimum sample size for Shapiro-Wilk
            shapiro_stat, shapiro_p = stats.shapiro(valid_age_data)

            print(f"\n📊 Shapiro-Wilk Normality Test:")
            print(f"  Shapiro-Wilk statistic: {shapiro_stat:.4f}")
            print(f"  P-value: {shapiro_p:.4f}")
            print(
                f"  Result: Age data {'ist nicht normalverteilt' if shapiro_p < 0.05 else 'könnte normalverteilt sein'} (α=0.05)")
        else:
            shapiro_stat, shapiro_p = None, None
            print(f"⚠️ Sample size too small for normality test (n={total_valid})")

        # Create visualizations
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # 1. Histogram with normal distribution overlay
        ax1.hist(valid_age_data, bins=20, density=True, alpha=0.7, color='skyblue',
                 edgecolor='black', label='Beobachtete Verteilung')

        # Overlay normal distribution
        x = np.linspace(valid_age_data.min(), valid_age_data.max(), 100)
        normal_y = stats.norm.pdf(x, age_mean, age_std)
        ax1.plot(x, normal_y, 'r-', alpha=0.6, linewidth=2, label='Normalverteilung')

        ax1.set_title('Altersverteilung der Patienten', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Alter in Jahren')
        ax1.set_ylabel('Häufigkeitsdichte')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Box plot
        ax2.boxplot(valid_age_data, vert=True, patch_artist=True,
                    boxprops=dict(facecolor='lightgreen', alpha=0.7),
                    medianprops=dict(color='red', linewidth=2))
        ax2.set_title('Box-Plot der Altersverteilung', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Alter in Jahren')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(
            self.session_plot_folder / f"altersverteilung_{self.timestamp}.png",
            dpi=300, bbox_inches='tight'
        )
        plt.show()

        # Save results
        results = {
            'Total_Valid_Patients': total_valid,
            'Average_Age': age_mean,
            'Median_Age': age_median,
            'Standard_Deviation': age_std,
            'Min_Age': age_min,
            'Max_Age': age_max,
            'Excluded_Missing_Age': missing_count,
            'Excluded_Age_Outliers': outlier_count,
            'Shapiro_Wilk_Statistic': shapiro_stat,
            'Shapiro_Wilk_P_Value': shapiro_p,
            'Age_Data_Normal_Distribution': shapiro_p >= 0.05 if shapiro_p is not None else None,
            'Analysis_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.analysis_results['age_analysis'] = results

        # Save to CSV
        results_df = pd.DataFrame([results])
        results_df.to_csv(
            self.session_output_folder / f"age_analysis_results_{self.timestamp}.csv",
            index=False
        )

        self.logger.info(f"Age analysis completed. {total_valid} valid patients, mean age: {age_mean:.2f}")
        return results

    def save_exclusion_log(self):
        """Save all exclusions and anomalies to CSV"""
        if self.exclusion_log:
            exclusion_df = pd.DataFrame(self.exclusion_log)
            exclusion_df.to_csv(
                self.session_output_folder / f"exclusion_log_{self.timestamp}.csv",
                index=False
            )
            print(f"✅ Exclusion log saved: {len(self.exclusion_log)} entries")
            self.logger.info(f"Exclusion log saved with {len(self.exclusion_log)} entries")
        else:
            # Create empty file to show no exclusions
            pd.DataFrame(columns=['Patient_ID', 'Issue', 'Value', 'Reason', 'Timestamp']).to_csv(
                self.session_output_folder / f"exclusion_log_{self.timestamp}.csv",
                index=False
            )
            print("✅ No exclusions found - empty log created")

    def generate_summary_report(self):
        """Generate final summary report"""
        print("\n" + "=" * 50)
        print("GENERATING SUMMARY REPORT")
        print("=" * 50)

        # Combine all results
        summary_data = []

        # Total cases
        if 'total_cases' in self.analysis_results:
            total_cases = self.analysis_results['total_cases']['Total_Cases_Advised']
            summary_data.append({
                'Analysis': 'Total Cases Advised',
                'Result': f"{total_cases} unique patients",
                'Details': f"Excluded {self.analysis_results['total_cases']['Excluded_Null_ID']} patients with null ID"
            })

        # Gender distribution
        if 'gender_distribution' in self.analysis_results:
            gender_results = self.analysis_results['gender_distribution']
            male_pct = gender_results['Male_Percentage']
            female_pct = gender_results['Female_Percentage']
            chi_square_sig = gender_results['Significant_Difference_from_50_50']

            summary_data.append({
                'Analysis': 'Gender Distribution',
                'Result': f"Männlich: {male_pct:.1f}%, Weiblich: {female_pct:.1f}%",
                'Details': f"Chi-Square test: {'Signifikant unterschiedlich' if chi_square_sig else 'Nicht signifikant unterschiedlich'} von 50:50 (p={gender_results['Chi_Square_P_Value']:.4f})"
            })

        # Age analysis
        if 'age_analysis' in self.analysis_results:
            age_results = self.analysis_results['age_analysis']
            avg_age = age_results['Average_Age']
            normal_dist = age_results['Age_Data_Normal_Distribution']

            summary_data.append({
                'Analysis': 'Average Age',
                'Result': f"{avg_age:.2f} years (SD: {age_results['Standard_Deviation']:.2f})",
                'Details': f"Normalverteilung: {'Ja' if normal_dist else 'Nein'} (Shapiro-Wilk p={age_results['Shapiro_Wilk_P_Value']:.4f})"
            })

        # Save summary
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(
            self.session_output_folder / f"descriptive_summary_report_{self.timestamp}.csv",
            index=False
        )

        print("📊 DESCRIPTIVE ANALYSIS SUMMARY:")
        print("-" * 40)
        for _, row in summary_df.iterrows():
            print(f"{row['Analysis']}: {row['Result']}")
            print(f"  {row['Details']}")
            print()

        print(f"✅ Analysis completed! Results saved in:")
        print(f"   📁 Logs: {self.session_log_folder}")
        print(f"   📁 Output: {self.session_output_folder}")
        print(f"   📁 Plots: {self.session_plot_folder}")

        self.logger.info("Descriptive analysis completed successfully")

    def run_complete_analysis(self):
        """Run the complete descriptive analysis"""
        print("🚀 Starting Complete Descriptive Analysis...")

        try:
            # Step 1: Extract unique patients data
            self.get_unique_patients_data()

            # Step 2: Analyze total cases advised
            self.analyze_total_cases()

            # Step 3: Analyze gender distribution
            self.analyze_gender_distribution()

            # Step 4: Analyze average age
            self.analyze_average_age()

            # Step 5: Save exclusion log
            self.save_exclusion_log()

            # Step 6: Generate summary report
            self.generate_summary_report()

            print("\n✅ Complete descriptive analysis finished successfully!")
            self.logger.info("Complete descriptive analysis finished successfully")

        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            self.logger.error(f"Error during analysis: {str(e)}")
            raise


# Usage example:
if __name__ == "__main__":
    # Load environment variables
    cleaned_dataset_path = os.getenv('CLEANED_DATASET', 'path/to/cleaned_dataset.csv')
    log_folder = os.getenv('LOG_FOLDER', 'logs')
    output_folder = os.getenv('OUTPUT_FOLDER', 'output')
    plot_folder = os.getenv('PLOT_FOLDER', 'plots')

    # Initialize and run analysis
    analyzer = DescriptiveAnalyzer(cleaned_dataset_path, log_folder, output_folder, plot_folder)
    analyzer.run_complete_analysis()