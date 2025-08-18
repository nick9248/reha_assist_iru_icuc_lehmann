import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from scipy.stats import f_oneway, ttest_ind, chi2_contingency
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


class MeanComparisonAnalyzer:
    def __init__(self, cleaned_dataset_path, log_folder, output_folder, plot_folder):
        """
        Initialize the MeanComparisonAnalyzer for Step 5: Mittelwertvergleichsanalyse

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
        self.session_folder = f"step5_mean_comparison_{self.timestamp}"

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
        self.patient_groups_df = None
        self.analysis_results = {}
        self.exclusion_log = []

        # Load dataset
        self.load_dataset()

    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.session_log_folder / f"mean_comparison_log_{self.timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Mean comparison analysis started at {datetime.now()}")

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

    def assign_healing_groups(self):
        """
        Assign patients to healing process groups based on StatusFL and StatusP across all visits

        Groups:
        1 - Ohne Stagnation: No "unverändert" (1) or "verschlechtert" (0) in any visit
        2 - Mit Stagnation: At least one "unverändert" (1) but no "verschlechtert" (0)
        3 - Mit Verschlechterung: At least one "verschlechtert" (0)
        """
        print("\n" + "=" * 60)
        print("GRUPPENZUWEISUNG NACH HEILUNGSPROZESS")
        print("=" * 60)

        if 'Unique ID' not in self.df.columns:
            raise ValueError("'Unique ID' column not found in dataset")

        # Status value mapping (from problem explanation)
        status_mapping = {
            'verbessert': 2,  # getting better
            'unverändert': 1,  # no change
            'verschlechtert': 0  # getting worse
        }

        print("📋 Gruppendefinitionen:")
        print("  Gruppe 1 - Ohne Stagnation: Nur 'verbessert' (2) in allen Besuchen")
        print("  Gruppe 2 - Mit Stagnation: Mindestens ein 'unverändert' (1), aber kein 'verschlechtert' (0)")
        print("  Gruppe 3 - Mit Verschlechterung: Mindestens ein 'verschlechtert' (0)")

        # Collect patient data
        patient_data = {}

        for _, row in self.df.iterrows():
            patient_id = row['Unique ID']
            if pd.isna(patient_id):
                continue

            if patient_id not in patient_data:
                patient_data[patient_id] = {
                    'status_values': [],
                    'contact_count': 0,
                    'age': row['Alter-Unfall'],
                    'gender': row['Geschlecht']
                }

            patient_data[patient_id]['contact_count'] += 1

            # Collect status values (both StatusFL and StatusP)
            for status_col in ['StatusFL', 'StatusP']:
                if not pd.isna(row[status_col]):
                    if row[status_col] in status_mapping:
                        patient_data[patient_id]['status_values'].append(status_mapping[row[status_col]])
                    else:
                        # Handle direct numeric values (0, 1, 2)
                        if row[status_col] in [0, 1, 2]:
                            patient_data[patient_id]['status_values'].append(row[status_col])

        # Assign groups
        group_assignments = []
        excluded_patients = 0

        for patient_id, data in patient_data.items():
            status_values = data['status_values']

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
                'Age': data['age'],
                'Gender': data['gender'],
                'Status_Values': status_values,
                'Unique_Status_Values': list(set(status_values))
            })

        # Create DataFrame
        self.patient_groups_df = pd.DataFrame(group_assignments)

        # Group statistics
        group_counts = self.patient_groups_df['Healing_Group'].value_counts().sort_index()
        total_patients = len(self.patient_groups_df)

        print(f"\n📊 Gruppenzusammensetzung:")
        print(f"  Gesamtzahl gültiger Patienten: {total_patients}")
        print(f"  Ausgeschlossene Patienten (keine Status-Daten): {excluded_patients}")
        print()

        group_names = {
            1: "Ohne Stagnation",
            2: "Mit Stagnation",
            3: "Mit Verschlechterung"
        }

        for group_num in [1, 2, 3]:
            count = group_counts.get(group_num, 0)
            percentage = (count / total_patients * 100) if total_patients > 0 else 0
            print(f"  Gruppe {group_num} ({group_names[group_num]}): {count} Patienten ({percentage:.1f}%)")

        # Save group assignments
        self.patient_groups_df.to_csv(
            self.session_output_folder / f"healing_group_assignments_{self.timestamp}.csv",
            index=False
        )

        self.logger.info(f"Healing group assignment completed. {total_patients} patients assigned to groups")
        return self.patient_groups_df

    def analyze_age_by_group(self):
        """
        Q1: What is the average age of respondents per healing process
        and does the average age differ between groups?
        """
        print("\n" + "=" * 60)
        print("ANALYSE Q1: DURCHSCHNITTSALTER NACH HEILUNGSPROZESS")
        print("=" * 60)

        # Filter valid age data
        valid_age_data = self.patient_groups_df[
            self.patient_groups_df['Age'].notna() &
            (self.patient_groups_df['Age'] >= 0) &
            (self.patient_groups_df['Age'] <= 120)
            ].copy()

        excluded_age = len(self.patient_groups_df) - len(valid_age_data)
        if excluded_age > 0:
            print(f"⚠️ {excluded_age} Patienten mit ungültigen Altersangaben ausgeschlossen")

        # Calculate descriptive statistics by group
        age_stats = []
        group_names = {1: "Ohne Stagnation", 2: "Mit Stagnation", 3: "Mit Verschlechterung"}

        print("\n📊 Deskriptive Statistiken - Alter nach Gruppe:")
        print("-" * 50)

        for group in [1, 2, 3]:
            group_data = valid_age_data[valid_age_data['Healing_Group'] == group]['Age']

            if len(group_data) > 0:
                stats_dict = {
                    'Gruppe': group,
                    'Gruppenname': group_names[group],
                    'N': len(group_data),
                    'Mittelwert': group_data.mean(),
                    'Median': group_data.median(),
                    'Standardabweichung': group_data.std(),
                    'Min': group_data.min(),
                    'Max': group_data.max()
                }
                age_stats.append(stats_dict)

                print(f"Gruppe {group} ({group_names[group]}):")
                print(f"  N = {stats_dict['N']}")
                print(f"  Mittelwert = {stats_dict['Mittelwert']:.2f} Jahre")
                print(f"  Median = {stats_dict['Median']:.2f} Jahre")
                print(f"  SD = {stats_dict['Standardabweichung']:.2f}")
                print(f"  Bereich = {stats_dict['Min']:.0f} - {stats_dict['Max']:.0f} Jahre")
                print()

        # One-way ANOVA
        print("🔬 STATISTISCHE TESTS - ALTER")
        print("-" * 30)

        groups_age_data = [
            valid_age_data[valid_age_data['Healing_Group'] == 1]['Age'].values,
            valid_age_data[valid_age_data['Healing_Group'] == 2]['Age'].values,
            valid_age_data[valid_age_data['Healing_Group'] == 3]['Age'].values
        ]

        # Remove empty groups
        groups_age_data = [group for group in groups_age_data if len(group) > 0]

        if len(groups_age_data) >= 2:
            f_stat, p_anova = f_oneway(*groups_age_data)

            print(f"One-way ANOVA:")
            print(f"  F-Statistik = {f_stat:.4f}")
            print(f"  p-Wert = {p_anova:.4f}")
            print(
                f"  Ergebnis: {'Signifikante Unterschiede' if p_anova < 0.05 else 'Keine signifikanten Unterschiede'} zwischen Gruppen (α=0.05)")

            # Post-hoc t-tests if ANOVA significant
            pairwise_results = []
            if p_anova < 0.05:
                print(f"\n📋 Post-hoc t-Tests (Welch's t-test):")

                pairs = [(1, 2), (1, 3), (2, 3)]
                alpha_bonferroni = 0.05 / len(pairs)

                for group1, group2 in pairs:
                    data1 = valid_age_data[valid_age_data['Healing_Group'] == group1]['Age']
                    data2 = valid_age_data[valid_age_data['Healing_Group'] == group2]['Age']

                    if len(data1) > 0 and len(data2) > 0:
                        t_stat, p_ttest = ttest_ind(data1, data2, equal_var=False)

                        result = {
                            'Gruppe_1': group1,
                            'Gruppe_2': group2,
                            'Vergleich': f"{group_names[group1]} vs {group_names[group2]}",
                            'Mean_1': data1.mean(),
                            'Mean_2': data2.mean(),
                            'Mean_Diff': data1.mean() - data2.mean(),
                            't_Statistik': t_stat,
                            'p_Wert': p_ttest,
                            'p_Bonferroni': p_ttest * len(pairs),
                            'Signifikant_005': p_ttest < 0.05,
                            'Signifikant_Bonferroni': p_ttest < alpha_bonferroni
                        }
                        pairwise_results.append(result)

                        print(f"  {result['Vergleich']}:")
                        print(f"    Mittelwerte: {result['Mean_1']:.2f} vs {result['Mean_2']:.2f}")
                        print(f"    Differenz: {result['Mean_Diff']:.2f} Jahre")
                        print(f"    t = {result['t_Statistik']:.4f}, p = {result['p_Wert']:.4f}")
                        print(f"    Bonferroni-korrigiert: p = {result['p_Bonferroni']:.4f}")
                        print(f"    Signifikant (α=0.05): {'Ja' if result['Signifikant_005'] else 'Nein'}")
                        print(f"    Signifikant (Bonferroni): {'Ja' if result['Signifikant_Bonferroni'] else 'Nein'}")
                        print()

        # Create box plot
        plt.figure(figsize=(12, 8))

        # Prepare data for box plot
        age_by_group = []
        group_labels = []

        for group in [1, 2, 3]:
            group_ages = valid_age_data[valid_age_data['Healing_Group'] == group]['Age']
            if len(group_ages) > 0:
                age_by_group.append(group_ages)
                group_labels.append(f"Gruppe {group}\n{group_names[group]}\n(n={len(group_ages)})")

        if age_by_group:
            bp = plt.boxplot(age_by_group, labels=group_labels, patch_artist=True)

            # Color the boxes
            colors = ['lightblue', 'lightgreen', 'lightcoral']
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)

            plt.title('Altersverteilung nach Heilungsprozess-Gruppe', fontsize=16, fontweight='bold')
            plt.xlabel('Heilungsprozess-Gruppe')
            plt.ylabel('Alter (Jahre)')
            plt.grid(True, alpha=0.3)

            # Add ANOVA result to plot
            if len(groups_age_data) >= 2:
                plt.text(0.02, 0.98, f'ANOVA: F={f_stat:.3f}, p={p_anova:.4f}',
                         transform=plt.gca().transAxes, verticalalignment='top',
                         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            plt.tight_layout()
            plt.savefig(
                self.session_plot_folder / f"alter_nach_gruppe_boxplot_{self.timestamp}.png",
                dpi=300, bbox_inches='tight'
            )
            plt.show()

        # Save results
        age_stats_df = pd.DataFrame(age_stats)
        age_stats_df.to_csv(
            self.session_output_folder / f"alter_deskriptive_statistiken_{self.timestamp}.csv",
            index=False
        )

        if 'pairwise_results' in locals():
            pairwise_df = pd.DataFrame(pairwise_results)
            pairwise_df.to_csv(
                self.session_output_folder / f"alter_paarweise_tests_{self.timestamp}.csv",
                index=False
            )

        # Store results
        self.analysis_results['age_analysis'] = {
            'descriptive_stats': age_stats,
            'anova_f': f_stat if 'f_stat' in locals() else None,
            'anova_p': p_anova if 'p_anova' in locals() else None,
            'pairwise_tests': pairwise_results if 'pairwise_results' in locals() else []
        }

        self.logger.info("Age analysis completed")
        return self.analysis_results['age_analysis']

    def analyze_contacts_by_group(self):
        """
        Q2: How many contacts were made on average per healing process
        and do they differ significantly between groups?
        """
        print("\n" + "=" * 60)
        print("ANALYSE Q2: DURCHSCHNITTLICHE KONTAKTE NACH HEILUNGSPROZESS")
        print("=" * 60)

        # All patients should have valid contact counts (>= 1)
        valid_contact_data = self.patient_groups_df[
            self.patient_groups_df['Contact_Count'].notna() &
            (self.patient_groups_df['Contact_Count'] >= 1)
            ].copy()

        excluded_contacts = len(self.patient_groups_df) - len(valid_contact_data)
        if excluded_contacts > 0:
            print(f"⚠️ {excluded_contacts} Patienten mit ungültigen Kontaktzahlen ausgeschlossen")

        # Calculate descriptive statistics by group
        contact_stats = []
        group_names = {1: "Ohne Stagnation", 2: "Mit Stagnation", 3: "Mit Verschlechterung"}

        print("\n📊 Deskriptive Statistiken - Kontakte nach Gruppe:")
        print("-" * 55)

        for group in [1, 2, 3]:
            group_data = valid_contact_data[valid_contact_data['Healing_Group'] == group]['Contact_Count']

            if len(group_data) > 0:
                stats_dict = {
                    'Gruppe': group,
                    'Gruppenname': group_names[group],
                    'N': len(group_data),
                    'Mittelwert': group_data.mean(),
                    'Median': group_data.median(),
                    'Standardabweichung': group_data.std(),
                    'Min': group_data.min(),
                    'Max': group_data.max()
                }
                contact_stats.append(stats_dict)

                print(f"Gruppe {group} ({group_names[group]}):")
                print(f"  N = {stats_dict['N']}")
                print(f"  Mittelwert = {stats_dict['Mittelwert']:.2f} Kontakte")
                print(f"  Median = {stats_dict['Median']:.2f} Kontakte")
                print(f"  SD = {stats_dict['Standardabweichung']:.2f}")
                print(f"  Bereich = {stats_dict['Min']:.0f} - {stats_dict['Max']:.0f} Kontakte")
                print()

        # One-way ANOVA
        print("🔬 STATISTISCHE TESTS - KONTAKTE")
        print("-" * 35)

        groups_contact_data = [
            valid_contact_data[valid_contact_data['Healing_Group'] == 1]['Contact_Count'].values,
            valid_contact_data[valid_contact_data['Healing_Group'] == 2]['Contact_Count'].values,
            valid_contact_data[valid_contact_data['Healing_Group'] == 3]['Contact_Count'].values
        ]

        # Remove empty groups
        groups_contact_data = [group for group in groups_contact_data if len(group) > 0]

        if len(groups_contact_data) >= 2:
            f_stat, p_anova = f_oneway(*groups_contact_data)

            print(f"One-way ANOVA:")
            print(f"  F-Statistik = {f_stat:.4f}")
            print(f"  p-Wert = {p_anova:.4f}")
            print(
                f"  Ergebnis: {'Signifikante Unterschiede' if p_anova < 0.05 else 'Keine signifikanten Unterschiede'} zwischen Gruppen (α=0.05)")

            # Post-hoc t-tests if ANOVA significant
            pairwise_results = []
            if p_anova < 0.05:
                print(f"\n📋 Post-hoc t-Tests (Welch's t-test):")

                pairs = [(1, 2), (1, 3), (2, 3)]
                alpha_bonferroni = 0.05 / len(pairs)

                for group1, group2 in pairs:
                    data1 = valid_contact_data[valid_contact_data['Healing_Group'] == group1]['Contact_Count']
                    data2 = valid_contact_data[valid_contact_data['Healing_Group'] == group2]['Contact_Count']

                    if len(data1) > 0 and len(data2) > 0:
                        t_stat, p_ttest = ttest_ind(data1, data2, equal_var=False)

                        result = {
                            'Gruppe_1': group1,
                            'Gruppe_2': group2,
                            'Vergleich': f"{group_names[group1]} vs {group_names[group2]}",
                            'Mean_1': data1.mean(),
                            'Mean_2': data2.mean(),
                            'Mean_Diff': data1.mean() - data2.mean(),
                            't_Statistik': t_stat,
                            'p_Wert': p_ttest,
                            'p_Bonferroni': p_ttest * len(pairs),
                            'Signifikant_005': p_ttest < 0.05,
                            'Signifikant_Bonferroni': p_ttest < alpha_bonferroni
                        }
                        pairwise_results.append(result)

                        print(f"  {result['Vergleich']}:")
                        print(f"    Mittelwerte: {result['Mean_1']:.2f} vs {result['Mean_2']:.2f}")
                        print(f"    Differenz: {result['Mean_Diff']:.2f} Kontakte")
                        print(f"    t = {result['t_Statistik']:.4f}, p = {result['p_Wert']:.4f}")
                        print(f"    Bonferroni-korrigiert: p = {result['p_Bonferroni']:.4f}")
                        print(f"    Signifikant (α=0.05): {'Ja' if result['Signifikant_005'] else 'Nein'}")
                        print(f"    Signifikant (Bonferroni): {'Ja' if result['Signifikant_Bonferroni'] else 'Nein'}")
                        print()

        # Create box plot
        plt.figure(figsize=(12, 8))

        # Prepare data for box plot
        contacts_by_group = []
        group_labels = []

        for group in [1, 2, 3]:
            group_contacts = valid_contact_data[valid_contact_data['Healing_Group'] == group]['Contact_Count']
            if len(group_contacts) > 0:
                contacts_by_group.append(group_contacts)
                group_labels.append(f"group {group}\n(n={len(group_contacts)})")
        if contacts_by_group:
            bp = plt.boxplot(contacts_by_group, labels=group_labels, patch_artist=True)

            # Color the boxes
            colors = ['lightblue', 'lightgreen', 'lightcoral']
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)

            plt.title('Number of contacts per healing process group', fontsize=16, fontweight='bold')
            plt.xlabel('group 1, group 2, group 3 (over all healing process group)')
            plt.ylabel('number of contacts')
            plt.grid(True, alpha=0.3)

            # Add ANOVA result to plot
            if len(groups_contact_data) >= 2:
                plt.text(0.02, 0.98, f'ANOVA=F{f_stat:.3f}; p={p_anova:.4f}',                         transform=plt.gca().transAxes, verticalalignment='top',
                         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            plt.tight_layout()
            plt.savefig(
                self.session_plot_folder / f"kontakte_nach_gruppe_boxplot_{self.timestamp}.png",
                dpi=300, bbox_inches='tight'
            )
            plt.show()

        # Save results
        contact_stats_df = pd.DataFrame(contact_stats)
        contact_stats_df.to_csv(
            self.session_output_folder / f"kontakte_deskriptive_statistiken_{self.timestamp}.csv",
            index=False
        )

        if 'pairwise_results' in locals():
            pairwise_df = pd.DataFrame(pairwise_results)
            pairwise_df.to_csv(
                self.session_output_folder / f"kontakte_paarweise_tests_{self.timestamp}.csv",
                index=False
            )

        # Store results
        self.analysis_results['contacts_analysis'] = {
            'descriptive_stats': contact_stats,
            'anova_f': f_stat if 'f_stat' in locals() else None,
            'anova_p': p_anova if 'p_anova' in locals() else None,
            'pairwise_tests': pairwise_results if 'pairwise_results' in locals() else []
        }

        self.logger.info("Contacts analysis completed")
        return self.analysis_results['contacts_analysis']

    def analyze_gender_by_group(self):
        """
        Q3: How many women/men are represented in the groups?
        Does the gender distribution differ per group?
        """
        print("\n" + "=" * 60)
        print("ANALYSE Q3: GESCHLECHTERVERTEILUNG NACH HEILUNGSPROZESS")
        print("=" * 60)

        # Filter valid gender data
        valid_gender_data = self.patient_groups_df[
            self.patient_groups_df['Gender'].notna() &
            self.patient_groups_df['Gender'].isin(['m', 'w'])
            ].copy()

        excluded_gender = len(self.patient_groups_df) - len(valid_gender_data)
        if excluded_gender > 0:
            print(f"⚠️ {excluded_gender} Patienten mit ungültigen Geschlechtsangaben ausgeschlossen")

        # Create contingency table
        contingency_table = pd.crosstab(
            valid_gender_data['Healing_Group'],
            valid_gender_data['Gender'],
            margins=True
        )

        print("\n📊 Kontingenztabelle - Geschlecht nach Gruppe:")
        print("-" * 50)

        # Rename for better display
        group_names = {1: "Ohne Stagnation", 2: "Mit Stagnation", 3: "Mit Verschlechterung"}
        gender_names = {'m': 'Männlich', 'w': 'Weiblich'}

        # Display counts and percentages
        for group in [1, 2, 3]:
            if group in contingency_table.index:
                male_count = contingency_table.loc[group, 'm'] if 'm' in contingency_table.columns else 0
                female_count = contingency_table.loc[group, 'w'] if 'w' in contingency_table.columns else 0
                total_group = male_count + female_count

                male_pct = (male_count / total_group * 100) if total_group > 0 else 0
                female_pct = (female_count / total_group * 100) if total_group > 0 else 0

                print(f"Gruppe {group} ({group_names[group]}):")
                print(f"  Männlich: {male_count} ({male_pct:.1f}%)")
                print(f"  Weiblich: {female_count} ({female_pct:.1f}%)")
                print(f"  Gesamt: {total_group}")
                print()

        # Chi-square test
        print("🔬 STATISTISCHE TESTS - GESCHLECHTERVERTEILUNG")
        print("-" * 50)

        # Remove margins for chi-square test
        test_table = contingency_table.iloc[:-1, :-1]  # Remove 'All' row and column

        if test_table.shape[0] >= 2 and test_table.shape[1] >= 2:
            chi2_stat, p_chi2, dof, expected = chi2_contingency(test_table)

            print(f"Chi-Quadrat-Test:")
            print(f"  Chi²-Statistik = {chi2_stat:.4f}")
            print(f"  Freiheitsgrade = {dof}")
            print(f"  p-Wert = {p_chi2:.4f}")
            print(
                f"  Ergebnis: {'Signifikante Unterschiede' if p_chi2 < 0.05 else 'Keine signifikanten Unterschiede'} in der Geschlechterverteilung (α=0.05)")

            # Check assumptions
            print(f"\n📋 Testvoraussetzungen:")
            min_expected = expected.min()
            cells_below_5 = (expected < 5).sum()
            total_cells = expected.size

            print(f"  Minimale erwartete Häufigkeit: {min_expected:.2f}")
            print(f"  Zellen mit erwarteter Häufigkeit < 5: {cells_below_5}/{total_cells}")
            print(f"  Voraussetzungen erfüllt: {'Ja' if min_expected >= 5 else 'Nein (min. erw. Häufigkeit < 5)'}")

        # Create stacked bar chart
        plt.figure(figsize=(12, 8))

        # Prepare data for plotting
        plot_data = []
        group_labels = []

        for group in [1, 2, 3]:
            if group in contingency_table.index:
                male_count = contingency_table.loc[group, 'm'] if 'm' in contingency_table.columns else 0
                female_count = contingency_table.loc[group, 'w'] if 'w' in contingency_table.columns else 0
                total = male_count + female_count

                plot_data.append({
                    'group': group,
                    'male_count': male_count,
                    'female_count': female_count,
                    'male_pct': (male_count / total * 100) if total > 0 else 0,
                    'female_pct': (female_count / total * 100) if total > 0 else 0
                })
                group_labels.append(f"group {group}\n(n={total})")

        if plot_data:
            # Create percentage stacked bar chart
            groups = [f"Gruppe {d['group']}" for d in plot_data]
            male_pcts = [d['male_pct'] for d in plot_data]
            female_pcts = [d['female_pct'] for d in plot_data]

            bar_width = 0.6
            x = np.arange(len(groups))

            p1 = plt.bar(x, male_pcts, bar_width, label='male', color='lightblue', alpha=0.8)
            p2 = plt.bar(x, female_pcts, bar_width, bottom=male_pcts, label='female', color='lightpink', alpha=0.8)

            plt.title('Gender distribution per healing group', fontsize=16, fontweight='bold')
            plt.xlabel('group 1, group 2, group 3 (over all healing process group)')
            plt.ylabel('percentages')
            plt.xticks(x, group_labels)
            plt.legend()
            plt.grid(True, alpha=0.3, axis='y')

            # Add percentage labels on bars
            for i, (male_pct, female_pct) in enumerate(zip(male_pcts, female_pcts)):
                if male_pct > 5:  # Only show label if bar is big enough
                    plt.text(i, male_pct / 2, f'{male_pct:.1f}%', ha='center', va='center', fontweight='bold')
                if female_pct > 5:
                    plt.text(i, male_pct + female_pct / 2, f'{female_pct:.1f}%', ha='center', va='center',
                             fontweight='bold')

            # Add chi-square result to plot
            if 'chi2_stat' in locals():
                plt.text(0.02, 0.98, f'Chi²={chi2_stat:.3f}; p={p_chi2:.4f}',
                         transform=plt.gca().transAxes, verticalalignment='top',
                         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            plt.tight_layout()
            plt.savefig(
                self.session_plot_folder / f"geschlecht_nach_gruppe_barplot_{self.timestamp}.png",
                dpi=300, bbox_inches='tight'
            )
            plt.show()

        # Save results
        contingency_table.to_csv(
            self.session_output_folder / f"geschlecht_kontingenztabelle_{self.timestamp}.csv"
        )

        # Store results
        self.analysis_results['gender_analysis'] = {
            'contingency_table': contingency_table,
            'chi2_statistic': chi2_stat if 'chi2_stat' in locals() else None,
            'chi2_p_value': p_chi2 if 'p_chi2' in locals() else None,
            'degrees_of_freedom': dof if 'dof' in locals() else None,
            'expected_frequencies': expected if 'expected' in locals() else None
        }

        self.logger.info("Gender analysis completed")
        return self.analysis_results['gender_analysis']

    def generate_final_summary_report(self):
        """Generate comprehensive final summary report"""
        print("\n" + "=" * 60)
        print("ABSCHLUSSBERICHT - MITTELWERTVERGLEICHSANALYSE")
        print("=" * 60)

        summary_data = []

        # Q1: Age analysis
        if 'age_analysis' in self.analysis_results:
            age_results = self.analysis_results['age_analysis']

            # Get group means
            group_means = {stat['Gruppe']: stat['Mittelwert'] for stat in age_results['descriptive_stats']}

            anova_result = "Signifikant" if age_results.get('anova_p', 1) < 0.05 else "Nicht signifikant"

            summary_data.append({
                'Analysefrage': 'Q1: Durchschnittsalter nach Heilungsprozess',
                'Ergebnis': f"Gruppe 1: {group_means.get(1, 'N/A'):.1f}, Gruppe 2: {group_means.get(2, 'N/A'):.1f}, Gruppe 3: {group_means.get(3, 'N/A'):.1f} Jahre",
                'Statistischer_Test': f"ANOVA: F={age_results.get('anova_f', 'N/A'):.3f}, p={age_results.get('anova_p', 'N/A'):.4f}",
                'Signifikanz': anova_result,
                'Interpretation': f"Altersunterschiede zwischen Gruppen sind {anova_result.lower()}"
            })

        # Q2: Contacts analysis
        if 'contacts_analysis' in self.analysis_results:
            contact_results = self.analysis_results['contacts_analysis']

            # Get group means
            group_means = {stat['Gruppe']: stat['Mittelwert'] for stat in contact_results['descriptive_stats']}

            anova_result = "Signifikant" if contact_results.get('anova_p', 1) < 0.05 else "Nicht signifikant"

            summary_data.append({
                'Analysefrage': 'Q2: Durchschnittliche Kontakte nach Heilungsprozess',
                'Ergebnis': f"Gruppe 1: {group_means.get(1, 'N/A'):.2f}, Gruppe 2: {group_means.get(2, 'N/A'):.2f}, Gruppe 3: {group_means.get(3, 'N/A'):.2f} Kontakte",
                'Statistischer_Test': f"ANOVA: F={contact_results.get('anova_f', 'N/A'):.3f}, p={contact_results.get('anova_p', 'N/A'):.4f}",
                'Signifikanz': anova_result,
                'Interpretation': f"Kontaktunterschiede zwischen Gruppen sind {anova_result.lower()}"
            })

        # Q3: Gender analysis
        if 'gender_analysis' in self.analysis_results:
            gender_results = self.analysis_results['gender_analysis']

            chi2_result = "Signifikant" if gender_results.get('chi2_p_value', 1) < 0.05 else "Nicht signifikant"

            summary_data.append({
                'Analysefrage': 'Q3: Geschlechterverteilung nach Heilungsprozess',
                'Ergebnis': 'Siehe Kontingenztabelle für detaillierte Verteilung',
                'Statistischer_Test': f"Chi²={gender_results.get('chi2_statistic', 'N/A'):.3f}, p={gender_results.get('chi2_p_value', 'N/A'):.4f}",
                'Signifikanz': chi2_result,
                'Interpretation': f"Geschlechterverteilung unterscheidet sich {chi2_result.lower()} zwischen Gruppen"
            })

        # Display summary
        print("\n📊 ZUSAMMENFASSUNG DER ERGEBNISSE:")
        print("-" * 60)

        for result in summary_data:
            print(f"\n{result['Analysefrage']}:")
            print(f"  Ergebnis: {result['Ergebnis']}")
            print(f"  Test: {result['Statistischer_Test']}")
            print(f"  Signifikanz: {result['Signifikanz']}")
            print(f"  Interpretation: {result['Interpretation']}")

        # Save comprehensive summary
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(
            self.session_output_folder / f"mittelwertvergleich_abschlussbericht_{self.timestamp}.csv",
            index=False
        )

        # Save exclusion log
        if self.exclusion_log:
            exclusion_df = pd.DataFrame(self.exclusion_log)
            exclusion_df.to_csv(
                self.session_output_folder / f"ausschluss_log_{self.timestamp}.csv",
                index=False
            )

        print(f"\n✅ Analyse abgeschlossen! Ergebnisse gespeichert in:")
        print(f"   📁 Logs: {self.session_log_folder}")
        print(f"   📁 Outputs: {self.session_output_folder}")
        print(f"   📁 Plots: {self.session_plot_folder}")

        print(f"\n📋 BEANTWORTETE FRAGEN:")
        print(f"✅ Durchschnittsalter der Befragten pro Heilungsprozess")
        print(f"✅ Unterschiede im Durchschnittsalter zwischen Gruppen (ANOVA + t-Tests)")
        print(f"✅ Durchschnittliche Kontakte pro Heilungsprozess")
        print(f"✅ Signifikante Unterschiede in Kontakten zwischen Gruppen (ANOVA + t-Tests)")
        print(f"✅ Geschlechterverteilung in den Gruppen (Chi²-Test)")
        print(f"✅ T-Tests für statistische Mittelwertvergleiche")

        self.logger.info("Mean comparison analysis completed successfully")

    def run_complete_analysis(self):
        """Run the complete mean comparison analysis (Step 5)"""
        print("🚀 Starting Step 5: Mittelwertvergleichsanalyse...")
        print("📋 Analysefragen:")
        print("   Q1: Durchschnittsalter der Befragten pro Heilungsprozess")
        print("   Q2: Durchschnittliche Kontakte pro Heilungsprozess")
        print("   Q3: Geschlechterverteilung in den Gruppen")
        print("   Alle mit statistischen Tests (ANOVA, t-Tests, Chi²)")

        try:
            # Step 1: Assign healing groups
            self.assign_healing_groups()

            # Step 2: Analyze age by group
            self.analyze_age_by_group()

            # Step 3: Analyze contacts by group
            self.analyze_contacts_by_group()

            # Step 4: Analyze gender by group
            self.analyze_gender_by_group()

            # Step 5: Generate final report
            self.generate_final_summary_report()

            print("\n✅ Mittelwertvergleichsanalyse erfolgreich abgeschlossen!")
            self.logger.info("Complete mean comparison analysis finished successfully")

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
    analyzer = MeanComparisonAnalyzer(cleaned_dataset_path, log_folder, output_folder, plot_folder)
    analyzer.run_complete_analysis()