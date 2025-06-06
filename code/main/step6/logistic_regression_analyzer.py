import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import os
import logging
from datetime import datetime
from pathlib import Path
import warnings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
warnings.filterwarnings('ignore')
plt.rcParams['font.size'] = 12


class LogisticRegressionAnalyzer:
    def __init__(self, cleaned_dataset_path, log_folder, output_folder, plot_folder):
        """
        Initialize the LogisticRegressionAnalyzer for Step 6: Logistic Regression Analysis
        """
        self.dataset_path = cleaned_dataset_path
        self.log_folder = Path(log_folder)
        self.output_folder = Path(output_folder)
        self.plot_folder = Path(plot_folder)

        # Create timestamp for this analysis session
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_folder = f"step6_logistic_regression_{self.timestamp}"

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
        self.patient_data = None
        self.analysis_results = {}
        self.exclusion_log = []

        # Load dataset
        self.load_dataset()

    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.session_log_folder / f"logistic_regression_log_{self.timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logistic regression analysis started at {datetime.now()}")

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

    def create_healing_groups(self):
        """Create healing process groups based on StatusP and StatusFL across all visits"""
        print("\n" + "=" * 60)
        print("HEALING GROUPS CREATION & CORRELATION ANALYSIS")
        print("=" * 60)

        # Status value mapping
        status_mapping = {
            'verbessert': 2,
            'unverändert': 1,
            'verschlechtert': 0
        }

        print("📋 Healing Group Definitions:")
        print("  Gruppe 1 - Ohne Stagnation: Nur 'verbessert' (2) in allen Besuchen")
        print("  Gruppe 2 - Mit Stagnation: Mind. ein 'unverändert' (1), kein 'verschlechtert' (0)")
        print("  Gruppe 3 - Mit Verschlechterung: Mind. ein 'verschlechtert' (0)")

        # Collect patient data
        patient_data = {}

        for _, row in self.df.iterrows():
            patient_id = row['Unique ID']
            if pd.isna(patient_id):
                continue

            if patient_id not in patient_data:
                patient_data[patient_id] = {
                    'status_values': [],
                    'contact_dates': [],
                    'contact_count': 0,
                    'age': row['Alter-Unfall'],
                    'gender': row['Geschlecht'],
                    'nbe': row['Verlauf_entspricht_NBE'],
                    'p_score': row['P'],
                    'fl_score': row['FLScore'],
                    'status_p': row['StatusP'],
                    'status_fl': row['StatusFL'],
                    'risk_factor': row['Risk Factor']
                }

            patient_data[patient_id]['contact_count'] += 1

            # Collect contact dates
            if not pd.isna(row['Kontaktdatum']):
                try:
                    contact_date = pd.to_datetime(row['Kontaktdatum'])
                    patient_data[patient_id]['contact_dates'].append(contact_date)
                except:
                    pass

            # Collect status values (both StatusFL and StatusP)
            for status_col in ['StatusFL', 'StatusP']:
                if not pd.isna(row[status_col]):
                    if row[status_col] in status_mapping:
                        patient_data[patient_id]['status_values'].append(status_mapping[row[status_col]])
                    elif row[status_col] in [0, 1, 2]:
                        patient_data[patient_id]['status_values'].append(row[status_col])

        # Assign groups and calculate duration
        group_assignments = []
        excluded_patients = 0

        for patient_id, data in patient_data.items():
            status_values = data['status_values']
            contact_dates = data['contact_dates']

            # Calculate call duration
            if len(contact_dates) >= 2:
                contact_dates.sort()
                duration_days = (contact_dates[-1] - contact_dates[0]).days
            else:
                duration_days = 0

            # Exclude patients with no status data
            if len(status_values) == 0:
                excluded_patients += 1
                self.exclusion_log.append({
                    'Patient_ID': patient_id,
                    'Issue': 'No_Status_Data',
                    'Reason': 'Both StatusFL and StatusP missing for all visits'
                })
                continue

            # Group assignment logic
            has_verschlechtert = 0 in status_values
            has_unveraendert = 1 in status_values

            if has_verschlechtert:
                group = 3  # Mit Verschlechterung
            elif has_unveraendert:
                group = 2  # Mit Stagnation
            else:
                group = 1  # Ohne Stagnation (only 'verbessert' = 2)

            group_assignments.append({
                'Patient_ID': patient_id,
                'Healing_Group': group,
                'Contact_Count': data['contact_count'],
                'Duration_Days': duration_days,
                'Age': data['age'],
                'Gender': data['gender'],
                'NBE': data['nbe'],
                'P_Score': data['p_score'],
                'FL_Score': data['fl_score'],
                'Status_P': data['status_p'],
                'Status_FL': data['status_fl'],
                'Risk_Factor': data['risk_factor']
            })

        # Create DataFrame
        self.patient_data = pd.DataFrame(group_assignments)

        # Group statistics
        group_counts = self.patient_data['Healing_Group'].value_counts().sort_index()
        total_patients = len(self.patient_data)

        print(f"\n📊 Healing Group Summary:")
        print(f"  Total patients: {total_patients}")
        print(f"  Excluded (no status data): {excluded_patients}")

        group_names = {1: "Ohne Stagnation", 2: "Mit Stagnation", 3: "Mit Verschlechterung"}
        for group_num in [1, 2, 3]:
            count = group_counts.get(group_num, 0)
            percentage = (count / total_patients * 100) if total_patients > 0 else 0
            print(f"  Gruppe {group_num} ({group_names[group_num]}): {count} ({percentage:.1f}%)")

        self.logger.info(f"Healing groups created. {total_patients} patients assigned")
        return self.patient_data

    def spearman_correlation_analysis(self):
        """Spearman correlation analysis between healing groups and contacts/duration"""
        print("\n" + "=" * 60)
        print("SPEARMAN KORRELATIONSANALYSE")
        print("=" * 60)

        # Filter valid data
        valid_data = self.patient_data[
            self.patient_data['Healing_Group'].notna() &
            self.patient_data['Contact_Count'].notna() &
            self.patient_data['Duration_Days'].notna()
            ].copy()

        print(f"📊 Gültige Daten für Korrelation: {len(valid_data)} Patienten")

        # 1. Correlation: Healing Group vs Number of Contacts
        print("\n1. HEILUNGSGRUPPE vs ANZAHL KONTAKTE")
        print("-" * 45)

        corr_contacts, p_contacts = stats.spearmanr(
            valid_data['Healing_Group'],
            valid_data['Contact_Count']
        )

        print(f"Spearman Korrelationskoeffizient: {corr_contacts:.4f}")
        print(f"P-Wert: {p_contacts:.4f}")
        print(f"Interpretation: {'Signifikant' if p_contacts < 0.05 else 'Nicht signifikant'} (α=0,05)")

        if abs(corr_contacts) < 0.1:
            strength = "vernachlässigbar"
        elif abs(corr_contacts) < 0.3:
            strength = "schwach"
        elif abs(corr_contacts) < 0.5:
            strength = "mäßig"
        elif abs(corr_contacts) < 0.7:
            strength = "stark"
        else:
            strength = "sehr stark"

        direction = "positiv" if corr_contacts > 0 else "negativ"
        print(f"Korrelationsstärke: {strength} {direction}")

        # 2. Correlation: Healing Group vs Duration
        print("\n2. HEILUNGSGRUPPE vs ANRUFDAUER")
        print("-" * 40)

        # Filter patients with multiple calls for duration analysis
        duration_data = valid_data[valid_data['Duration_Days'] > 0]
        print(f"Patienten mit mehreren Anrufen: {len(duration_data)}")

        if len(duration_data) > 10:  # Need sufficient data
            corr_duration, p_duration = stats.spearmanr(
                duration_data['Healing_Group'],
                duration_data['Duration_Days']
            )

            print(f"Spearman Korrelationskoeffizient: {corr_duration:.4f}")
            print(f"P-Wert: {p_duration:.4f}")
            print(f"Interpretation: {'Signifikant' if p_duration < 0.05 else 'Nicht signifikant'} (α=0,05)")

            if abs(corr_duration) < 0.1:
                strength_dur = "vernachlässigbar"
            elif abs(corr_duration) < 0.3:
                strength_dur = "schwach"
            elif abs(corr_duration) < 0.5:
                strength_dur = "mäßig"
            elif abs(corr_duration) < 0.7:
                strength_dur = "stark"
            else:
                strength_dur = "sehr stark"

            direction_dur = "positiv" if corr_duration > 0 else "negativ"
            print(f"Korrelationsstärke: {strength_dur} {direction_dur}")
        else:
            corr_duration, p_duration = None, None
            print("⚠️ Unzureichende Daten für Dauer-Korrelationsanalyse")

        # Create correlation plots with German labels
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Plot 1: Healing Group vs Contact Count
        ax1.scatter(valid_data['Healing_Group'], valid_data['Contact_Count'], alpha=0.6, color='steelblue')
        ax1.set_xlabel('Heilungsgruppe')
        ax1.set_ylabel('Anzahl Kontakte')
        ax1.set_title(f'Heilungsgruppe vs Kontaktanzahl\n(ρ={corr_contacts:.3f}, p={p_contacts:.4f})',
                      fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks([1, 2, 3])
        ax1.set_xticklabels(['Ohne\nStagnation', 'Mit\nStagnation', 'Mit\nVerschlechterung'])

        # Add trend line
        z = np.polyfit(valid_data['Healing_Group'], valid_data['Contact_Count'], 1)
        p = np.poly1d(z)
        ax1.plot(valid_data['Healing_Group'], p(valid_data['Healing_Group']), "r--", alpha=0.8, linewidth=2)

        # Plot 2: Healing Group vs Duration (if data available)
        if len(duration_data) > 10:
            ax2.scatter(duration_data['Healing_Group'], duration_data['Duration_Days'], alpha=0.6, color='darkgreen')
            ax2.set_xlabel('Heilungsgruppe')
            ax2.set_ylabel('Dauer (Tage)')
            ax2.set_title(f'Heilungsgruppe vs Anrufdauer\n(ρ={corr_duration:.3f}, p={p_duration:.4f})',
                          fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.set_xticks([1, 2, 3])
            ax2.set_xticklabels(['Ohne\nStagnation', 'Mit\nStagnation', 'Mit\nVerschlechterung'])

            # Add trend line
            z = np.polyfit(duration_data['Healing_Group'], duration_data['Duration_Days'], 1)
            p = np.poly1d(z)
            ax2.plot(duration_data['Healing_Group'], p(duration_data['Healing_Group']), "r--", alpha=0.8, linewidth=2)
        else:
            ax2.text(0.5, 0.5, 'Unzureichende Daten\nfür Dauer-Analyse',
                     transform=ax2.transAxes, ha='center', va='center', fontsize=12)
            ax2.set_title('Heilungsgruppe vs Anrufdauer', fontweight='bold')
            ax2.set_xlabel('Heilungsgruppe')
            ax2.set_ylabel('Dauer (Tage)')

        plt.tight_layout()
        plt.savefig(
            self.session_plot_folder / f"spearman_korrelation_{self.timestamp}.png",
            dpi=300, bbox_inches='tight'
        )
        plt.show()

        # Save correlation results
        correlation_results = {
            'Healing_Group_vs_Contacts': {
                'correlation': corr_contacts,
                'p_value': p_contacts,
                'significant': p_contacts < 0.05,
                'interpretation': f"{strength} {direction}"
            },
            'Healing_Group_vs_Duration': {
                'correlation': corr_duration,
                'p_value': p_duration,
                'significant': p_duration < 0.05 if p_duration is not None else None,
                'interpretation': f"{strength_dur} {direction_dur}" if corr_duration is not None else "Unzureichende Daten"
            }
        }

        # Save to CSV with German headers
        corr_df = pd.DataFrame([
            {
                'Analyse': 'Heilungsgruppe vs Kontakte',
                'Spearman_rho': corr_contacts,
                'P_Wert': p_contacts,
                'Signifikant': p_contacts < 0.05,
                'Stichprobengröße': len(valid_data),
                'Interpretation': correlation_results['Healing_Group_vs_Contacts']['interpretation']
            },
            {
                'Analyse': 'Heilungsgruppe vs Dauer',
                'Spearman_rho': corr_duration,
                'P_Wert': p_duration,
                'Signifikant': p_duration < 0.05 if p_duration is not None else None,
                'Stichprobengröße': len(duration_data) if corr_duration is not None else 0,
                'Interpretation': correlation_results['Healing_Group_vs_Duration']['interpretation']
            }
        ])

        corr_df.to_csv(
            self.session_output_folder / f"spearman_korrelation_ergebnisse_{self.timestamp}.csv",
            index=False
        )

        self.analysis_results['spearman_correlation'] = correlation_results
        self.logger.info("Spearman correlation analysis completed")
        return correlation_results

    def prepare_logistic_regression_data(self):
        """Prepare data for logistic regression analysis with proper German text conversion"""
        print("\n" + "=" * 60)
        print("LOGISTIC REGRESSION DATA PREPARATION")
        print("=" * 60)

        # Get patients with first visit data for logistic regression
        first_visits = self.df.groupby('Unique ID').first().reset_index()

        print(f"📊 First visits dataset: {len(first_visits)} patients")

        # Define variables for logistic regression
        dependent_var = 'Verlauf_entspricht_NBE'
        independent_vars = ['P', 'FLScore', 'StatusP', 'StatusFL', 'Geschlecht', 'Alter-Unfall', 'Risk Factor']

        print(f"\n📋 Logistic Regression Variables:")
        print(f"  Dependent Variable: {dependent_var} (NBE assessment)")
        print(f"  Independent Variables: {independent_vars}")

        # Filter data with valid dependent variable
        valid_nbe = first_visits[first_visits[dependent_var].notna()].copy()
        print(f"  Patients with valid NBE data: {len(valid_nbe)}")

        # Check dependent variable distribution
        nbe_counts = valid_nbe[dependent_var].value_counts()
        print(f"\n📊 NBE Distribution:")
        for value, count in nbe_counts.items():
            percentage = count / len(valid_nbe) * 100
            label = "NBE Yes" if value == 1 else "NBE No"
            print(f"  {label} ({value}): {count} patients ({percentage:.1f}%)")

        # Check if we have enough cases for both classes
        if len(nbe_counts) < 2 or min(nbe_counts) < 10:
            print("⚠️ Warning: Insufficient cases for one class. Consider different grouping.")

        # Prepare independent variables with proper data type conversion
        lr_data = valid_nbe.copy()

        print(f"\n🔧 Data Preprocessing & Type Conversion:")

        # Define status mapping for German text conversion
        status_mapping = {
            'verbessert': 2,  # getting better
            'unverändert': 1,  # no change
            'verschlechtert': 0  # getting worse
        }

        print(f"  Status mapping: {status_mapping}")

        # Handle each variable with proper type conversion
        processed_vars = {}

        # Process numeric variables (already numeric)
        numeric_vars = ['P', 'FLScore', 'Alter-Unfall', 'Risk Factor']
        for var in numeric_vars:
            if var in lr_data.columns:
                # Convert to numeric, handling any string/object types
                lr_data[var] = pd.to_numeric(lr_data[var], errors='coerce')
                processed_vars[var] = var
                print(f"  {var}: converted to numeric")

        # Process status variables (German text to numeric)
        status_vars = ['StatusP', 'StatusFL']
        for var in status_vars:
            if var in lr_data.columns:
                # Convert German text to numeric values
                lr_data[f'{var}_numeric'] = lr_data[var].map(status_mapping)
                processed_vars[f'{var}_numeric'] = var
                print(f"  {var}: German text → numeric ({var}_numeric)")

                # Show conversion stats
                conversion_counts = lr_data[[var, f'{var}_numeric']].dropna().groupby(var)[f'{var}_numeric'].first()
                for text, num in conversion_counts.items():
                    print(f"    '{text}' → {num}")

        # Handle categorical variables
        if 'Geschlecht' in lr_data.columns:
            # Convert gender to binary numeric
            lr_data['Gender_Male'] = (lr_data['Geschlecht'] == 'm').astype(int)
            processed_vars['Gender_Male'] = 'Geschlecht'
            print(f"  Gender: m=1, w=0 (binary numeric)")

        # Convert dependent variable to numeric
        lr_data[dependent_var] = pd.to_numeric(lr_data[dependent_var], errors='coerce')
        print(f"  {dependent_var}: converted to binary numeric")

        # Create final variable list
        final_independent_vars = list(processed_vars.keys())
        all_vars = final_independent_vars + [dependent_var]

        # Check data completeness after type conversion
        print(f"\n📋 Variable Completeness (after type conversion):")
        for var in final_independent_vars:
            valid_count = lr_data[var].notna().sum()
            missing_count = lr_data[var].isna().sum()
            print(f"  {var}: {valid_count} valid, {missing_count} missing")

        # Select only the variables we need
        lr_final = lr_data[all_vars].copy()

        # Remove rows with any missing values
        lr_complete = lr_final.dropna()

        # Final data type check and conversion
        print(f"\n🔧 Final Data Type Verification:")
        for col in lr_complete.columns:
            if col != dependent_var:
                # Ensure all independent variables are float64
                lr_complete[col] = lr_complete[col].astype(float)
                print(f"  {col}: {lr_complete[col].dtype}")

        # Ensure dependent variable is integer (0/1)
        lr_complete[dependent_var] = lr_complete[dependent_var].astype(int)
        print(f"  {dependent_var}: {lr_complete[dependent_var].dtype}")

        print(f"\n📊 Final Logistic Regression Dataset:")
        print(f"  Complete cases: {len(lr_complete)} patients")
        print(f"  Variables included: {list(lr_complete.columns)}")

        # Show final sample sizes and missing data analysis
        print(f"\n📋 Missing Data Analysis:")
        total_with_nbe = len(valid_nbe)

        # Calculate step-by-step exclusions
        step_sizes = {}
        step_sizes['Starting (valid NBE)'] = total_with_nbe

        # Check each variable's contribution to missing data
        temp_data = lr_data[all_vars].copy()  # Use lr_data instead of valid_nbe
        for var in final_independent_vars:
            temp_data = temp_data[temp_data[var].notna()]
            step_sizes[f'After {var}'] = len(temp_data)

        print(f"  Step-by-step exclusions:")
        for step, size in step_sizes.items():
            excluded = total_with_nbe - size
            print(f"    {step}: {size} patients ({excluded} excluded)")

        # Verify final data types
        print(f"\n✅ Final Data Summary:")
        for col in lr_complete.columns:
            dtype_str = str(lr_complete[col].dtype)
            sample_vals = lr_complete[col].head(3).tolist()
            print(f"  {col}: {dtype_str} (samples: {sample_vals})")

        excluded_count = len(valid_nbe) - len(lr_complete)
        exclusion_rate = (excluded_count / len(valid_nbe)) * 100
        print(f"\n📊 Final Statistics:")
        print(f"  Complete cases: {len(lr_complete)} patients")
        print(f"  Excluded (missing data): {excluded_count} patients ({exclusion_rate:.1f}%)")

        # Store for logistic regression
        self.lr_data = lr_complete
        self.lr_dependent_var = dependent_var
        self.lr_independent_vars = final_independent_vars

        self.logger.info(f"Logistic regression data prepared. {len(lr_complete)} complete cases")
        return lr_complete

    def run_logistic_regression(self):
        """Run logistic regression analysis"""
        print("\n" + "=" * 60)
        print("LOGISTIC REGRESSION ANALYSIS")
        print("=" * 60)

        if self.lr_data is None or len(self.lr_data) == 0:
            print("❌ No data available for logistic regression")
            return None

        # Prepare variables
        X = self.lr_data[self.lr_independent_vars]
        y = self.lr_data[self.lr_dependent_var]

        print(f"📊 Logistic Regression Setup:")
        print(f"  Sample size: {len(self.lr_data)}")
        print(f"  Dependent variable: {self.lr_dependent_var}")
        print(f"  Independent variables: {self.lr_independent_vars}")

        # Check class distribution
        class_counts = y.value_counts()
        print(f"\n📊 Class Distribution:")
        for class_val, count in class_counts.items():
            percentage = count / len(y) * 100
            label = "NBE Yes" if class_val == 1 else "NBE No"
            print(f"  {label}: {count} ({percentage:.1f}%)")

        # Run logistic regression with statsmodels for detailed statistics
        print(f"\n🔬 STATSMODELS LOGISTIC REGRESSION")
        print("-" * 45)

        # Add constant for intercept
        X_with_const = sm.add_constant(X)

        try:
            # Fit logistic regression
            logit_model = sm.Logit(y, X_with_const)
            result = logit_model.fit(disp=0)

            # Print summary
            print(result.summary())

            # Extract key results
            coefficients = result.params
            p_values = result.pvalues
            conf_intervals = result.conf_int()
            odds_ratios = np.exp(coefficients)

            # Create results DataFrame
            results_df = pd.DataFrame({
                'Variable': coefficients.index,
                'Coefficient': coefficients.values,
                'P_Value': p_values.values,
                'Odds_Ratio': odds_ratios.values,
                'CI_Lower_95': np.exp(conf_intervals[0].values),
                'CI_Upper_95': np.exp(conf_intervals[1].values),
                'Significant': p_values.values < 0.05
            })

            print(f"\n📊 DETAILED RESULTS:")
            print("-" * 30)

            for _, row in results_df.iterrows():
                if row['Variable'] == 'const':
                    print(f"Intercept:")
                else:
                    print(f"{row['Variable']}:")

                print(f"  Coefficient: {row['Coefficient']:.4f}")
                print(f"  P-value: {row['P_Value']:.4f}")
                print(f"  Odds Ratio: {row['Odds_Ratio']:.4f}")
                print(f"  95% CI: [{row['CI_Lower_95']:.4f}, {row['CI_Upper_95']:.4f}]")
                print(f"  Significant: {'Yes' if row['Significant'] else 'No'}")

                # Interpretation
                if row['Variable'] != 'const':
                    if row['Odds_Ratio'] > 1:
                        effect = f"increases odds by {((row['Odds_Ratio'] - 1) * 100):.1f}%"
                    else:
                        effect = f"decreases odds by {((1 - row['Odds_Ratio']) * 100):.1f}%"
                    print(f"  Interpretation: {effect}")
                print()

            # Model fit statistics
            print(f"📊 MODEL FIT STATISTICS:")
            print("-" * 30)
            print(f"Log-Likelihood: {result.llf:.4f}")
            print(f"AIC: {result.aic:.4f}")
            print(f"BIC: {result.bic:.4f}")
            print(f"Pseudo R²: {result.prsquared:.4f}")

            # Save detailed results
            results_df.to_csv(
                self.session_output_folder / f"logistic_regression_results_{self.timestamp}.csv",
                index=False
            )

            # Save model summary
            with open(self.session_output_folder / f"logistic_regression_summary_{self.timestamp}.txt", 'w') as f:
                f.write(str(result.summary()))

            # Create visualization
            self.plot_logistic_regression_results(results_df)

            # Store results
            self.analysis_results['logistic_regression'] = {
                'model_results': result,
                'results_dataframe': results_df,
                'sample_size': len(self.lr_data),
                'pseudo_r_squared': result.prsquared,
                'aic': result.aic
            }

            self.logger.info("Logistic regression analysis completed successfully")
            return result

        except Exception as e:
            print(f"❌ Error in logistic regression: {str(e)}")
            self.logger.error(f"Logistic regression error: {str(e)}")
            return None

    def plot_logistic_regression_results(self, results_df):
        """Create visualizations for logistic regression results with German labels"""
        # Filter out intercept for plotting
        plot_data = results_df[results_df['Variable'] != 'const'].copy()

        if len(plot_data) == 0:
            print("⚠️ No variables to plot")
            return

        # German variable names mapping
        german_labels = {
            'P': 'Schmerzwerte',
            'FLScore': 'Funktionseinschränkung',
            'StatusP_numeric': 'Schmerz-Status',
            'StatusFL_numeric': 'Funktions-Status',
            'Gender_Male': 'Geschlecht (männlich)',
            'Alter-Unfall': 'Alter bei Unfall',
            'Risk Factor': 'Risikofaktor'
        }

        # Add German labels to plot data
        plot_data['German_Label'] = plot_data['Variable'].map(german_labels).fillna(plot_data['Variable'])

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Plot 1: Coefficients
        y_pos = np.arange(len(plot_data))

        # Create horizontal bar chart for coefficients
        colors = ['red' if sig else 'steelblue' for sig in plot_data['Significant']]
        bars1 = ax1.barh(y_pos, plot_data['Coefficient'], color=colors, alpha=0.7)

        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(plot_data['German_Label'])
        ax1.set_xlabel('Koeffizient')
        ax1.set_title('Logistische Regression - Koeffizienten', fontsize=14, fontweight='bold')
        ax1.axvline(x=0, color='black', linestyle='--', alpha=0.5)
        ax1.grid(True, alpha=0.3)

        # Add significance markers
        for i, (_, row) in enumerate(plot_data.iterrows()):
            if row['Significant']:
                ax1.text(row['Coefficient'], i, ' *', fontsize=16, ha='left', va='center', fontweight='bold')

        # Plot 2: Odds Ratios with confidence intervals
        bars2 = ax2.barh(y_pos, plot_data['Odds_Ratio'], color=colors, alpha=0.7)

        # Add confidence interval lines
        for i, (_, row) in enumerate(plot_data.iterrows()):
            ax2.plot([row['CI_Lower_95'], row['CI_Upper_95']], [i, i], 'k-', alpha=0.8, linewidth=2)
            # Add CI markers
            ax2.plot([row['CI_Lower_95'], row['CI_Upper_95']], [i, i], 'k|', markersize=8, alpha=0.8)

        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(plot_data['German_Label'])
        ax2.set_xlabel('Odds Ratio')
        ax2.set_title('Odds Ratios mit 95% Konfidenzintervall', fontsize=14, fontweight='bold')
        ax2.axvline(x=1, color='black', linestyle='--', alpha=0.5)
        ax2.grid(True, alpha=0.3)

        # Add significance markers
        for i, (_, row) in enumerate(plot_data.iterrows()):
            if row['Significant']:
                ax2.text(row['Odds_Ratio'], i, ' *', fontsize=16, ha='left', va='center', fontweight='bold')

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='red', alpha=0.7, label='Signifikant (p < 0,05)'),
            Patch(facecolor='steelblue', alpha=0.7, label='Nicht signifikant'),
            plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='black',
                       markersize=12, label='* p < 0,05')
        ]
        fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=3)

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)  # Make space for legend
        plt.savefig(
            self.session_plot_folder / f"logistische_regression_ergebnisse_{self.timestamp}.png",
            dpi=300, bbox_inches='tight'
        )
        plt.show()

    def check_model_assumptions(self):
        """Check logistic regression assumptions and diagnostics"""
        print("\n" + "=" * 60)
        print("MODEL ASSUMPTIONS & DIAGNOSTICS")
        print("=" * 60)

        if 'logistic_regression' not in self.analysis_results:
            print("❌ Logistic regression must be run first")
            return

        model_result = self.analysis_results['logistic_regression']['model_results']
        X = self.lr_data[self.lr_independent_vars]
        y = self.lr_data[self.lr_dependent_var]

        print("🔍 CHECKING MODEL ASSUMPTIONS:")
        print("-" * 35)

        # 1. Multicollinearity check (VIF)
        print("1. MULTICOLLINEARITY (VIF):")
        X_with_const = sm.add_constant(X)

        vif_data = pd.DataFrame()
        vif_data["Variable"] = X_with_const.columns
        vif_data["VIF"] = [variance_inflation_factor(X_with_const.values, i)
                           for i in range(len(X_with_const.columns))]

        print(vif_data)

        # Check VIF values
        high_vif = vif_data[vif_data['VIF'] > 5]
        if len(high_vif) > 0:
            print("⚠️ Warning: High VIF detected (>5), possible multicollinearity:")
            print(high_vif)
        else:
            print("✅ No multicollinearity issues detected (all VIF < 5)")

        # 2. Sample size adequacy
        print(f"\n2. SAMPLE SIZE ADEQUACY:")
        n_predictors = len(self.lr_independent_vars)
        min_sample_rule1 = n_predictors * 10  # 10 events per variable
        min_sample_rule2 = n_predictors * 20  # Conservative rule
        actual_sample = len(self.lr_data)

        print(f"  Number of predictors: {n_predictors}")
        print(f"  Actual sample size: {actual_sample}")
        print(f"  Minimum required (10 per variable): {min_sample_rule1}")
        print(f"  Conservative minimum (20 per variable): {min_sample_rule2}")

        if actual_sample >= min_sample_rule2:
            print("✅ Sample size is adequate (conservative rule)")
        elif actual_sample >= min_sample_rule1:
            print("⚠️ Sample size meets minimum but could be larger")
        else:
            print("❌ Sample size may be insufficient")

        # 3. Outliers detection
        print(f"\n3. OUTLIER DETECTION:")

        # Calculate standardized residuals
        predicted_probs = model_result.predict()
        pearson_residuals = (y - predicted_probs) / np.sqrt(predicted_probs * (1 - predicted_probs))

        # Count extreme outliers (|residual| > 2.5)
        extreme_outliers = np.abs(pearson_residuals) > 2.5
        n_outliers = extreme_outliers.sum()

        print(f"  Extreme outliers (|residual| > 2.5): {n_outliers}")

        if n_outliers > 0:
            outlier_indices = np.where(extreme_outliers)[0]
            print(f"  Outlier patient indices: {outlier_indices[:10]}...")  # Show first 10
        else:
            print("✅ No extreme outliers detected")

        # Save diagnostics
        diagnostics_df = pd.DataFrame({
            'Patient_Index': range(len(y)),
            'Predicted_Probability': predicted_probs,
            'Pearson_Residual': pearson_residuals,
            'Is_Outlier': extreme_outliers
        })

        diagnostics_df.to_csv(
            self.session_output_folder / f"model_diagnostics_{self.timestamp}.csv",
            index=False
        )

        # Save VIF results
        vif_data.to_csv(
            self.session_output_folder / f"vif_analysis_{self.timestamp}.csv",
            index=False
        )

        print(f"\n✅ Model diagnostics saved to CSV files")
        self.logger.info("Model assumptions check completed")

    def generate_final_report(self):
        """Generate comprehensive final report with German labels"""
        print("\n" + "=" * 60)
        print("ABSCHLUSSBERICHT - REGRESSION & KORRELATIONSANALYSE")
        print("=" * 60)

        report_sections = []

        # Section 1: Spearman Correlation Results
        if 'spearman_correlation' in self.analysis_results:
            corr_results = self.analysis_results['spearman_correlation']

            contacts_corr = corr_results['Healing_Group_vs_Contacts']
            duration_corr = corr_results['Healing_Group_vs_Duration']

            report_sections.append({
                'Analyse': 'Spearman Korrelation: Heilungsgruppen vs Kontakte',
                'Ergebnis': f"ρ = {contacts_corr['correlation']:.4f}, p = {contacts_corr['p_value']:.4f}",
                'Signifikant': contacts_corr['significant'],
                'Interpretation': f"Korrelation ist {contacts_corr['interpretation']}"
            })

            if duration_corr['correlation'] is not None:
                report_sections.append({
                    'Analyse': 'Spearman Korrelation: Heilungsgruppen vs Anrufdauer',
                    'Ergebnis': f"ρ = {duration_corr['correlation']:.4f}, p = {duration_corr['p_value']:.4f}",
                    'Signifikant': duration_corr['significant'],
                    'Interpretation': f"Korrelation ist {duration_corr['interpretation']}"
                })

        # Section 2: Logistic Regression Results
        if 'logistic_regression' in self.analysis_results:
            lr_results = self.analysis_results['logistic_regression']
            results_df = lr_results['results_dataframe']

            # Get significant predictors
            significant_vars = results_df[
                (results_df['Significant'] == True) &
                (results_df['Variable'] != 'const')
                ]

            report_sections.append({
                'Analyse': 'Logistische Regression: NBE-Vorhersage',
                'Ergebnis': f"Modell mit {len(self.lr_independent_vars)} Prädiktoren, n={lr_results['sample_size']}",
                'Signifikant': len(significant_vars) > 0,
                'Interpretation': f"Pseudo R² = {lr_results['pseudo_r_squared']:.4f}"
            })

            # German variable names for interpretation
            german_var_names = {
                'P': 'Schmerzwerte',
                'FLScore': 'Funktionseinschränkung',
                'StatusP_numeric': 'Schmerz-Status',
                'StatusFL_numeric': 'Funktions-Status',
                'Gender_Male': 'Geschlecht (männlich)',
                'Alter-Unfall': 'Alter bei Unfall',
                'Risk Factor': 'Risikofaktor'
            }

            # Add details for significant predictors
            for _, var_result in significant_vars.iterrows():
                var_german = german_var_names.get(var_result['Variable'], var_result['Variable'])
                effect_direction = "erhöht" if var_result['Odds_Ratio'] > 1 else "verringert"
                effect_size = abs(var_result['Odds_Ratio'] - 1) * 100

                report_sections.append({
                    'Analyse': f"  Prädiktor: {var_german}",
                    'Ergebnis': f"OR = {var_result['Odds_Ratio']:.4f}, p = {var_result['P_Value']:.4f}",
                    'Signifikant': True,
                    'Interpretation': f"{effect_direction} NBE-Wahrscheinlichkeit um {effect_size:.1f}%"
                })

        # Display report
        print("\n📊 ZUSAMMENFASSUNG DER ERGEBNISSE:")
        print("-" * 50)

        for section in report_sections:
            status = "✅" if section['Signifikant'] else "❌"
            print(f"\n{status} {section['Analyse']}:")
            print(f"    Ergebnis: {section['Ergebnis']}")
            print(f"    Interpretation: {section['Interpretation']}")

        # Clinical interpretation
        print(f"\n🏥 KLINISCHE INTERPRETATION:")
        print("-" * 30)

        if 'spearman_correlation' in self.analysis_results:
            contacts_corr = self.analysis_results['spearman_correlation']['Healing_Group_vs_Contacts']
            if contacts_corr['significant']:
                print(f"✅ Patienten mit komplizierterem Heilungsverlauf benötigen mehr Kontakte")
                print(f"   (ρ = {contacts_corr['correlation']:.3f}, p < 0,05)")

            duration_corr = self.analysis_results['spearman_correlation']['Healing_Group_vs_Duration']
            if duration_corr['correlation'] is not None and duration_corr['significant']:
                print(f"✅ Patienten mit komplizierterem Heilungsverlauf haben längere Betreuungsdauer")
                print(f"   (ρ = {duration_corr['correlation']:.3f}, p < 0,05)")

        if 'logistic_regression' in self.analysis_results:
            lr_results = self.analysis_results['logistic_regression']
            if lr_results['sample_size'] > 0:
                print(f"✅ NBE-Vorhersagemodell erfolgreich erstellt mit {lr_results['sample_size']} Patienten")
                print(f"   Modellgüte: Pseudo R² = {lr_results['pseudo_r_squared']:.3f}")

        # Save comprehensive report
        report_df = pd.DataFrame(report_sections)
        report_df.to_csv(
            self.session_output_folder / f"abschlussbericht_regression_{self.timestamp}.csv",
            index=False
        )

        # Summary statistics
        print(f"\n📁 ERSTELLTE DATEIEN:")
        print(f"   📊 Korrelationsanalyse: spearman_korrelation_ergebnisse_{self.timestamp}.csv")
        if 'logistic_regression' in self.analysis_results:
            print(f"   📊 Logistische Regression: logistic_regression_results_{self.timestamp}.csv")
            print(f"   📊 Modell-Diagnostik: model_diagnostics_{self.timestamp}.csv")
        print(f"   📊 Abschlussbericht: abschlussbericht_regression_{self.timestamp}.csv")
        print(f"   📁 Plots: {self.session_plot_folder}")

        print(f"\n✅ Analyse abgeschlossen! Alle Ergebnisse in:")
        print(f"   📁 Logs: {self.session_log_folder}")
        print(f"   📁 Outputs: {self.session_output_folder}")
        print(f"   📁 Plots: {self.session_plot_folder}")

        self.logger.info("Final report generated successfully")

    def run_complete_analysis(self):
        """Run the complete regression and correlation analysis"""
        print("🚀 Starting Step 6: Regression & Korrelationsanalyse...")
        print("\n📋 Durchzuführende Analysen:")
        print("   1. Spearman Korrelation: Heilungsgruppen vs Kontakte/Dauer")
        print("   2. Logistische Regression: NBE-Vorhersage")
        print("   3. Modell-Diagnostik & Annahmenprüfung")
        print("-" * 60)

        try:
            # Step 1: Create healing groups and correlation analysis
            self.create_healing_groups()
            self.spearman_correlation_analysis()

            # Step 2: Prepare and run logistic regression
            self.prepare_logistic_regression_data()

            # Only run logistic regression if we have sufficient data
            if hasattr(self, 'lr_data') and len(self.lr_data) > 0:
                self.run_logistic_regression()
                self.check_model_assumptions()
            else:
                print("\n⚠️ Logistische Regression übersprungen - unzureichende Daten")
                print("   Mögliche Gründe:")
                print("   - Zu viele fehlende Werte in StatusP/StatusFL")
                print("   - Risk Factor hat viele fehlende Werte")
                print("   - Empfehlung: Modell ohne Risk Factor versuchen")

            # Step 3: Generate final report
            self.generate_final_report()

            print("\n✅ Vollständige Regressionsanalyse erfolgreich abgeschlossen!")
            self.logger.info("Complete regression analysis finished successfully")

        except Exception as e:
            print(f"❌ Fehler während der Analyse: {str(e)}")
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
    analyzer = LogisticRegressionAnalyzer(cleaned_dataset_path, log_folder, output_folder, plot_folder)
    analyzer.run_complete_analysis()