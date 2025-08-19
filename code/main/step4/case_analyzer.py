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
plt.rcParams['font.size'] = 12


class CaseAnalyzer:
    def __init__(self, cleaned_dataset_path, log_folder, output_folder, plot_folder):
        """
        Initialize the CaseAnalyzer for Step 4: Analysis per Case

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
        self.session_folder = f"step4_case_analysis_{self.timestamp}"

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
        self.analysis_results = {}
        self.inconsistency_log = []

        # Load dataset
        self.load_dataset()

    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.session_log_folder / f"case_analysis_log_{self.timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Case analysis started at {datetime.now()}")

    def load_dataset(self):
        """Load the cleaned dataset from Step 2"""
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

    def analyze_calls_per_case(self):
        """
        Q1: How many phone calls per case were made on average?
        Count records per Unique ID (including ID = 0)
        """
        print("\n" + "=" * 60)
        print("ANALYSE Q1: ANRUFE PRO FALL")
        print("=" * 60)

        if 'Unique ID' not in self.df.columns:
            raise ValueError("'Unique ID' column not found in dataset")

        # Count calls per patient (including Unique ID = 0)
        calls_per_patient = self.df.groupby('Unique ID').size()

        # Calculate statistics
        total_cases = len(calls_per_patient)
        total_calls = calls_per_patient.sum()
        average_calls = calls_per_patient.mean()
        median_calls = calls_per_patient.median()
        min_calls = calls_per_patient.min()
        max_calls = calls_per_patient.max()
        std_calls = calls_per_patient.std()

        print(f"📊 Anrufe pro Fall Analyse:")
        print(f"  Gesamtzahl der Fälle: {total_cases}")
        print(f"  Gesamtzahl der Anrufe: {total_calls}")
        print(f"  Durchschnittliche Anrufe pro Fall: {average_calls:.2f}")
        print(f"  Median Anrufe pro Fall: {median_calls:.1f}")
        print(f"  Minimum Anrufe pro Fall: {min_calls}")
        print(f"  Maximum Anrufe pro Fall: {max_calls}")
        print(f"  Standardabweichung: {std_calls:.2f}")

        # Distribution analysis
        calls_distribution = calls_per_patient.value_counts().sort_index()
        print(f"\n📈 Verteilung der Anrufe:")
        for calls, count in calls_distribution.items():
            percentage = (count / total_cases) * 100
            print(f"  {calls} Anrufe: {count} Fälle ({percentage:.1f}%)")

        # Create histogram
        plt.figure(figsize=(12, 8))
        plt.hist(calls_per_patient, bins=range(1, max_calls + 2), edgecolor='black', alpha=0.7, color='skyblue')
        plt.title('Frequency of contact', fontsize=16, fontweight='bold')
        plt.xlabel('number of contacts per case')
        plt.ylabel('number of cases')
        plt.grid(True, alpha=0.3)

        # Add average line
        plt.axvline(average_calls, color='red', linestyle='--', linewidth=2,
                    label=f'mean: {average_calls:.2f}')
        plt.legend()

        plt.tight_layout()
        plt.savefig(
            self.session_plot_folder / f"anrufe_pro_fall_verteilung_{self.timestamp}.png",
            dpi=300, bbox_inches='tight'
        )
        plt.show()

        # Save results
        results = {
            'Total_Cases': total_cases,
            'Total_Calls': total_calls,
            'Average_Calls_Per_Case': average_calls,
            'Median_Calls_Per_Case': median_calls,
            'Min_Calls_Per_Case': min_calls,
            'Max_Calls_Per_Case': max_calls,
            'Std_Calls_Per_Case': std_calls,
            'Analysis_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.analysis_results['calls_per_case'] = results

        # Save detailed results
        calls_per_patient_df = calls_per_patient.reset_index()
        calls_per_patient_df.columns = ['Unique_ID', 'Anzahl_Anrufe']
        calls_per_patient_df.to_csv(
            self.session_output_folder / f"anrufe_pro_fall_details_{self.timestamp}.csv",
            index=False
        )

        # Save summary results
        results_df = pd.DataFrame([results])
        results_df.to_csv(
            self.session_output_folder / f"anrufe_pro_fall_summary_{self.timestamp}.csv",
            index=False
        )

        self.logger.info(f"Calls per case analysis completed. Average: {average_calls:.2f} calls per case")
        return results

    def analyze_call_duration_per_case(self):
        """
        Q2: How long did the phone calls last (Duration = last date - first date) on average per case?
        Single call patients get 0 duration
        Create box plot with German labels
        """
        print("\n" + "=" * 60)
        print("ANALYSE Q2: ANRUFDAUER PRO FALL")
        print("=" * 60)

        if 'Kontaktdatum' not in self.df.columns:
            raise ValueError("'Kontaktdatum' column not found in dataset")

        if 'Unique ID' not in self.df.columns:
            raise ValueError("'Unique ID' column not found in dataset")

        # Convert Kontaktdatum to datetime
        self.df['Kontaktdatum_dt'] = pd.to_datetime(self.df['Kontaktdatum'], errors='coerce')

        # Check for invalid dates
        invalid_dates = self.df['Kontaktdatum_dt'].isnull()
        if invalid_dates.sum() > 0:
            print(f"⚠️ Warnung: {invalid_dates.sum()} ungültige Datumsangaben gefunden")

        # Calculate duration per patient
        duration_data = []

        for patient_id in self.df['Unique ID'].unique():
            if pd.isna(patient_id):
                continue

            patient_data = self.df[self.df['Unique ID'] == patient_id]
            valid_dates = patient_data['Kontaktdatum_dt'].dropna()

            if len(valid_dates) == 0:
                # No valid dates - skip this patient
                continue
            elif len(valid_dates) == 1:
                # Single call - duration = 0
                first_call = valid_dates.min()
                last_call = valid_dates.min()
                duration_days = 0
            else:
                # Multiple calls - calculate duration
                first_call = valid_dates.min()
                last_call = valid_dates.max()
                duration_days = (last_call - first_call).days

            duration_data.append({
                'Unique_ID': patient_id,
                'Anzahl_Anrufe': len(patient_data),
                'Anzahl_gueltige_Daten': len(valid_dates),
                'Erster_Anruf': first_call,
                'Letzter_Anruf': last_call,
                'Dauer_Tage': duration_days
            })

        duration_df = pd.DataFrame(duration_data)

        if len(duration_df) == 0:
            print("❌ Keine gültigen Daten für Daueranalyse gefunden!")
            return None

        # Calculate statistics
        durations = duration_df['Dauer_Tage']
        total_cases = len(duration_df)
        average_duration = durations.mean()
        median_duration = durations.median()
        min_duration = durations.min()
        max_duration = durations.max()
        std_duration = durations.std()

        # Count single vs multiple call cases
        single_call_cases = (duration_df['Anzahl_gueltige_Daten'] == 1).sum()
        multiple_call_cases = (duration_df['Anzahl_gueltige_Daten'] > 1).sum()
        zero_duration_cases = (durations == 0).sum()

        print(f"📊 Anrufdauer Analyse:")
        print(f"  Gesamtzahl der Fälle mit gültigen Daten: {total_cases}")
        print(f"  Fälle mit einem Anruf (Dauer = 0): {single_call_cases}")
        print(f"  Fälle mit mehreren Anrufen: {multiple_call_cases}")
        print(f"  Durchschnittliche Dauer: {average_duration:.2f} Tage")
        print(f"  Median Dauer: {median_duration:.1f} Tage")
        print(f"  Minimum Dauer: {min_duration} Tage")
        print(f"  Maximum Dauer: {max_duration} Tage")
        print(f"  Standardabweichung: {std_duration:.2f} Tage")

        # Create box plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Box plot for all cases
        box_data = durations
        bp1 = ax1.boxplot(box_data, vert=True, patch_artist=True,
                          boxprops=dict(facecolor='lightblue', alpha=0.7),
                          medianprops=dict(color='red', linewidth=2))

        ax1.set_title('Duration of support vs. healing process group', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Duration of support (days)')
        ax1.grid(True, alpha=0.3)

        # Add statistics text
        stats_text = f'Mittelwert: {average_duration:.1f} Tage\nMedian: {median_duration:.1f} Tage\nStd: {std_duration:.1f} Tage'
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # Box plot for cases with multiple calls only
        multiple_call_durations = duration_df[duration_df['Anzahl_gueltige_Daten'] > 1]['Dauer_Tage']

        if len(multiple_call_durations) > 0:
            bp2 = ax2.boxplot(multiple_call_durations, vert=True, patch_artist=True,
                              boxprops=dict(facecolor='lightgreen', alpha=0.7),
                              medianprops=dict(color='red', linewidth=2))

            avg_multiple = multiple_call_durations.mean()
            med_multiple = multiple_call_durations.median()
            std_multiple = multiple_call_durations.std()

            ax2.set_title('Duration of support vs. healing process group', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Duration of support (days)')
            ax2.grid(True, alpha=0.3)

            stats_text2 = f'Mittelwert: {avg_multiple:.1f} Tage\nMedian: {med_multiple:.1f} Tage\nStd: {std_multiple:.1f} Tage'
            ax2.text(0.02, 0.98, stats_text2, transform=ax2.transAxes, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        else:
            ax2.text(0.5, 0.5, 'Keine Mehrfachanrufe\nverfügbar',
                     transform=ax2.transAxes, ha='center', va='center', fontsize=12)
            ax2.set_title('Box-Plot: Anrufdauer pro Fall (nur Mehrfachanrufe)', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(
            self.session_plot_folder / f"anrufdauer_boxplot_{self.timestamp}.png",
            dpi=300, bbox_inches='tight'
        )
        plt.show()

        # Save results
        results = {
            'Total_Cases_With_Valid_Dates': total_cases,
            'Single_Call_Cases': single_call_cases,
            'Multiple_Call_Cases': multiple_call_cases,
            'Average_Duration_Days': average_duration,
            'Median_Duration_Days': median_duration,
            'Min_Duration_Days': min_duration,
            'Max_Duration_Days': max_duration,
            'Std_Duration_Days': std_duration,
            'Average_Duration_Multiple_Calls_Only': multiple_call_durations.mean() if len(
                multiple_call_durations) > 0 else None,
            'Analysis_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.analysis_results['call_duration'] = results

        # Save detailed results
        duration_df.to_csv(
            self.session_output_folder / f"anrufdauer_details_{self.timestamp}.csv",
            index=False
        )

        # Save summary results
        results_df = pd.DataFrame([results])
        results_df.to_csv(
            self.session_output_folder / f"anrufdauer_summary_{self.timestamp}.csv",
            index=False
        )

        self.logger.info(f"Call duration analysis completed. Average duration: {average_duration:.2f} days")
        return results

    def analyze_risk_factors(self):
        """
        Q3: Risk factor analysis
        Part A: Find patients with inconsistent risk factor values
        Part B: Count patients with/without risk factors
        Risk Factor: 0 (no risk), 1 (has risk), null (no info)
        """
        print("\n" + "=" * 60)
        print("ANALYSE Q3: RISIKOFAKTOREN")
        print("=" * 60)

        if 'Risk Factor' not in self.df.columns:
            raise ValueError("'Risk Factor' column not found in dataset")

        if 'Unique ID' not in self.df.columns:
            raise ValueError("'Unique ID' column not found in dataset")

        # Part A: Find inconsistent patients
        print("📋 TEIL A: INKONSISTENZ-PRÜFUNG")
        print("-" * 40)

        inconsistent_patients = []
        patient_risk_summary = []

        for patient_id in self.df['Unique ID'].unique():
            if pd.isna(patient_id):
                continue

            patient_data = self.df[self.df['Unique ID'] == patient_id]
            risk_values = patient_data['Risk Factor'].dropna()  # Remove null values for consistency check

            if len(risk_values) == 0:
                # All values are null
                patient_risk_summary.append({
                    'Unique_ID': patient_id,
                    'Total_Records': len(patient_data),
                    'Has_Risk_Factor': 'Keine Information',
                    'Risk_Values': 'Alle null',
                    'Inconsistent': False
                })
            else:
                unique_risk_values = risk_values.unique()

                # Check for inconsistency (both 0 and 1 present)
                has_inconsistency = len(unique_risk_values) > 1 and (
                            0 in unique_risk_values and 1 in unique_risk_values)

                if has_inconsistency:
                    inconsistent_patients.append({
                        'Unique_ID': patient_id,
                        'Total_Records': len(patient_data),
                        'Risk_Values': list(unique_risk_values),
                        'Value_Counts': patient_data['Risk Factor'].value_counts().to_dict()
                    })

                # Determine patient's overall risk status
                if 1 in unique_risk_values:
                    risk_status = 'Ja'  # Has risk factor (any visit with 1 = yes)
                elif 0 in unique_risk_values:
                    risk_status = 'Nein'  # No risk factor (only 0s)
                else:
                    risk_status = 'Keine Information'  # Should not happen as we filtered nulls

                patient_risk_summary.append({
                    'Unique_ID': patient_id,
                    'Total_Records': len(patient_data),
                    'Has_Risk_Factor': risk_status,
                    'Risk_Values': str(list(unique_risk_values)),
                    'Inconsistent': has_inconsistency
                })

        print(f"Inkonsistente Patienten gefunden: {len(inconsistent_patients)}")

        if inconsistent_patients:
            print("Beispiele inkonsistenter Patienten:")
            for i, patient in enumerate(inconsistent_patients[:5]):
                print(f"  Patient {patient['Unique_ID']}: Werte {patient['Risk_Values']}")
        else:
            print("✅ Keine inkonsistenten Patienten gefunden!")

        # Part B: Overall frequency analysis
        print(f"\n📊 TEIL B: HÄUFIGKEITSVERTEILUNG")
        print("-" * 40)

        patient_summary_df = pd.DataFrame(patient_risk_summary)

        # Count patients by risk status
        risk_counts = patient_summary_df['Has_Risk_Factor'].value_counts()
        total_patients = len(patient_summary_df)

        print(f"Gesamtzahl der Patienten: {total_patients}")
        for status, count in risk_counts.items():
            percentage = (count / total_patients) * 100
            print(f"  {status}: {count} Patienten ({percentage:.1f}%)")

        # Create bar chart
        plt.figure(figsize=(12, 8))

        # Prepare data for plotting
        categories = risk_counts.index.tolist()
        values = risk_counts.values.tolist()
        colors = ['lightcoral' if 'Ja' in cat else 'lightblue' if 'Nein' in cat else 'lightgray' for cat in categories]

        bars = plt.bar(categories, values, color=colors, edgecolor='black', alpha=0.7)

        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height + total_patients * 0.01,
                     f'{value}\n({value / total_patients * 100:.1f}%)',
                     ha='center', va='bottom', fontweight='bold')

        plt.title('Verteilung der Risikofaktoren bei Patienten', fontsize=16, fontweight='bold')
        plt.xlabel('Risikofaktor-Status')
        plt.ylabel('Anzahl der Patienten')
        plt.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(
            self.session_plot_folder / f"risikofaktoren_verteilung_{self.timestamp}.png",
            dpi=300, bbox_inches='tight'
        )
        plt.show()

        # Save results
        results = {
            'Total_Patients': total_patients,
            'Patients_With_Risk_Factor': risk_counts.get('Ja', 0),
            'Patients_Without_Risk_Factor': risk_counts.get('Nein', 0),
            'Patients_No_Information': risk_counts.get('Keine Information', 0),
            'Inconsistent_Patients': len(inconsistent_patients),
            'Percentage_With_Risk': (risk_counts.get('Ja', 0) / total_patients * 100) if total_patients > 0 else 0,
            'Percentage_Without_Risk': (risk_counts.get('Nein', 0) / total_patients * 100) if total_patients > 0 else 0,
            'Percentage_No_Info': (
                        risk_counts.get('Keine Information', 0) / total_patients * 100) if total_patients > 0 else 0,
            'Analysis_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.analysis_results['risk_factors'] = results

        # Save detailed patient summary
        patient_summary_df.to_csv(
            self.session_output_folder / f"risikofaktoren_patienten_summary_{self.timestamp}.csv",
            index=False
        )

        # Save inconsistent patients log
        if inconsistent_patients:
            inconsistent_df = pd.DataFrame(inconsistent_patients)
            inconsistent_df.to_csv(
                self.session_output_folder / f"risikofaktoren_inkonsistente_patienten_{self.timestamp}.csv",
                index=False
            )

        # Save summary results
        results_df = pd.DataFrame([results])
        results_df.to_csv(
            self.session_output_folder / f"risikofaktoren_summary_{self.timestamp}.csv",
            index=False
        )

        self.logger.info(f"Risk factor analysis completed. {len(inconsistent_patients)} inconsistent patients found")
        return results

    def generate_final_report(self):
        """Generate comprehensive final report for Step 4"""
        print("\n" + "=" * 60)
        print("GENERIERE ABSCHLUSSBERICHT")
        print("=" * 60)

        # Combine all results
        summary_data = []

        # Q1: Calls per case
        if 'calls_per_case' in self.analysis_results:
            calls_results = self.analysis_results['calls_per_case']
            summary_data.append({
                'Frage': 'Q1: Anrufe pro Fall',
                'Ergebnis': f"Durchschnitt: {calls_results['Average_Calls_Per_Case']:.2f} Anrufe pro Fall",
                'Details': f"Total: {calls_results['Total_Cases']} Fälle, {calls_results['Total_Calls']} Anrufe"
            })

        # Q2: Call duration
        if 'call_duration' in self.analysis_results:
            duration_results = self.analysis_results['call_duration']
            summary_data.append({
                'Frage': 'Q2: Anrufdauer pro Fall',
                'Ergebnis': f"Durchschnitt: {duration_results['Average_Duration_Days']:.2f} Tage",
                'Details': f"Einzelanrufe: {duration_results['Single_Call_Cases']}, Mehrfachanrufe: {duration_results['Multiple_Call_Cases']}"
            })

        # Q3: Risk factors
        if 'risk_factors' in self.analysis_results:
            risk_results = self.analysis_results['risk_factors']
            summary_data.append({
                'Frage': 'Q3: Risikofaktoren',
                'Ergebnis': f"Mit Risiko: {risk_results['Percentage_With_Risk']:.1f}%, Ohne Risiko: {risk_results['Percentage_Without_Risk']:.1f}%",
                'Details': f"Inkonsistente Patienten: {risk_results['Inconsistent_Patients']}, Keine Info: {risk_results['Percentage_No_Info']:.1f}%"
            })

        # Save comprehensive summary
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(
            self.session_output_folder / f"case_analysis_final_report_{self.timestamp}.csv",
            index=False
        )

        print("📊 FALLANALYSE ZUSAMMENFASSUNG:")
        print("-" * 50)
        for _, row in summary_df.iterrows():
            print(f"{row['Frage']}: {row['Ergebnis']}")
            print(f"  Details: {row['Details']}")
            print()

        print(f"✅ Analyse abgeschlossen! Ergebnisse gespeichert in:")
        print(f"   📁 Logs: {self.session_log_folder}")
        print(f"   📁 Outputs: {self.session_output_folder}")
        print(f"   📁 Plots: {self.session_plot_folder}")

        self.logger.info("Case analysis completed successfully")

    def run_complete_analysis(self):
        """Run the complete case analysis (Step 4)"""
        print("🚀 Starting Complete Case Analysis (Step 4)...")

        try:
            # Run all three analyses
            self.analyze_calls_per_case()
            self.analyze_call_duration_per_case()
            self.analyze_risk_factors()

            # Generate final report
            self.generate_final_report()

            print("\n✅ Complete case analysis finished successfully!")
            self.logger.info("Complete case analysis finished successfully")

        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            self.logger.error(f"Error during analysis: {str(e)}")
            raise


# Usage example:
if __name__ == "__main__":
    # Load environment variables
    cleaned_dataset_path = os.getenv('DATASET_CLEANED', 'path/to/cleaned_dataset.csv')
    log_folder = os.getenv('LOG_FOLDER', 'logs')
    output_folder = os.getenv('OUTPUT_FOLDER', 'output')
    plot_folder = os.getenv('PLOT_FOLDER', 'plots')

    # Initialize and run analysis
    analyzer = CaseAnalyzer(cleaned_dataset_path, log_folder, output_folder, plot_folder)
    analyzer.run_complete_analysis()