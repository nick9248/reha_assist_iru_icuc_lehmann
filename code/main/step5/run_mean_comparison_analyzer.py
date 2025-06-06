"""
Step 5: Mean Comparison Analysis Runner Script
Run this script to perform mean comparison analysis (Mittelwertvergleichsanalyse)

Analysis Questions:
- Q1: What is the average age of respondents per healing process and does the average age differ between groups?
- Q2: How many contacts were made on average per healing process and do they differ significantly between groups?
- Q3: How many women/men are represented in the groups? Does the gender distribution differ per group?
- T-test for statistical mean comparison for each mean comparison
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from mean_comparison_analyzer import MeanComparisonAnalyzer

# Load environment variables from .env file
load_dotenv()


def find_latest_cleaned_dataset(output_folder):
    """Find the most recent cleaned dataset from Step 2"""
    output_path = Path(output_folder)

    # Look for Step 2 cleaning folders
    step2_folders = [f for f in output_path.iterdir()
                     if f.is_dir() and f.name.startswith('step2_data_cleaning_')]

    if not step2_folders:
        raise FileNotFoundError("No Step 2 cleaning results found. Please run Step 2 first.")

    # Get the most recent folder by modification time
    latest_folder = max(step2_folders, key=lambda x: x.stat().st_mtime)

    # Look for cleaned dataset file in the folder
    cleaned_files = list(latest_folder.glob('dataset_cleaned_*.csv'))

    if not cleaned_files:
        raise FileNotFoundError(f"No cleaned dataset found in {latest_folder}")

    # Get the most recent cleaned file
    latest_cleaned_file = max(cleaned_files, key=lambda x: x.stat().st_mtime)

    return latest_cleaned_file


def main():
    """Main function to run the mean comparison analysis"""

    print("🔬 Step 5: Mittelwertvergleichsanalyse (Mean Comparison Analysis)")
    print("📋 Fragestellungen:")
    print("   Q1: Durchschnittsalter pro Heilungsprozess und Gruppenvergleich")
    print("   Q2: Durchschnittliche Kontakte pro Heilungsprozess und Gruppenvergleich")
    print("   Q3: Geschlechterverteilung in den Gruppen und Vergleich")
    print("   Alle mit statistischen Tests (ANOVA, t-Tests, Chi²-Test)")
    print()
    print("🏥 Heilungsprozess-Gruppen:")
    print("   Gruppe 1: Ohne Stagnation (nur 'verbessert')")
    print("   Gruppe 2: Mit Stagnation (mind. 1x 'unverändert', kein 'verschlechtert')")
    print("   Gruppe 3: Mit Verschlechterung (mind. 1x 'verschlechtert')")
    print("-" * 70)

    # Load environment variables
    log_folder = os.getenv('LOG_FOLDER', 'logs')
    output_folder = os.getenv('OUTPUT_FOLDER', 'output')
    plot_folder = os.getenv('PLOT_FOLDER', 'plots')

    # Option 1: Use environment variable for cleaned dataset
    cleaned_dataset_path = os.getenv('DATASET_CLEANED')

    # Option 2: If no env variable, find the latest cleaned dataset
    if not cleaned_dataset_path:
        try:
            cleaned_dataset_file = find_latest_cleaned_dataset(output_folder)
            cleaned_dataset_path = str(cleaned_dataset_file)
            print(f"📊 Using latest cleaned dataset: {cleaned_dataset_file.name}")
        except FileNotFoundError as e:
            print(f"❌ Error: {str(e)}")
            print("Please run Step 2 (data cleaning) first, or set DATASET_CLEANED environment variable.")
            return

    # Validate cleaned dataset path
    if not Path(cleaned_dataset_path).exists():
        print(f"❌ Error: Cleaned dataset file not found at: {cleaned_dataset_path}")
        return

    print(f"📊 Cleaned dataset: {cleaned_dataset_path}")
    print(f"📁 Log folder: {log_folder}")
    print(f"📁 Output folder: {output_folder}")
    print(f"📁 Plot folder: {plot_folder}")
    print("-" * 70)

    try:
        # Initialize and run mean comparison analysis
        analyzer = MeanComparisonAnalyzer(
            cleaned_dataset_path=cleaned_dataset_path,
            log_folder=log_folder,
            output_folder=output_folder,
            plot_folder=plot_folder
        )

        analyzer.run_complete_analysis()

        print(f"\n🎉 Mittelwertvergleichsanalyse erfolgreich abgeschlossen!")
        print(f"\n📋 BEANTWORTETE FRAGEN:")
        print(f"✅ Q1: Durchschnittsalter pro Heilungsprozess mit ANOVA & t-Tests")
        print(f"✅ Q2: Durchschnittliche Kontakte pro Heilungsprozess mit ANOVA & t-Tests")
        print(f"✅ Q3: Geschlechterverteilung mit Chi²-Test")
        print(f"✅ Alle statistischen Mittelwertvergleiche mit Bonferroni-Korrektur")
        print(f"\n📁 Prüfen Sie die Output-Ordner für detaillierte Ergebnisse, Plots und Logs!")

    except Exception as e:
        print(f"❌ Mean comparison analysis failed: {str(e)}")
        return


if __name__ == "__main__":
    main()