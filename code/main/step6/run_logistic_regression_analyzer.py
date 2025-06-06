"""
Step 6: Logistic Regression Analysis Runner Script
Run this script to perform regression and correlation analysis

Analysis Questions:
- Correlation: Is there a correlation between healing process group and number/duration of phone calls?
- Logistic Regression: Do ICUC scores influence NBE assessment? How do age, gender, and risk factors affect prediction?
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from logistic_regression_analyzer import LogisticRegressionAnalyzer

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
    """Main function to run the logistic regression analysis"""

    print("🔬 Step 6: Regression & Correlation Analysis")
    print("\n📋 Research Questions:")
    print("   1. CORRELATION ANALYSIS:")
    print("      • Is there a correlation between healing process group and number of phone calls?")
    print("      • Is there a correlation between healing process group and duration of phone calls?")
    print("   2. LOGISTIC REGRESSION:")
    print("      • Do ICUC scores (P/FL/StatusP/StatusFL) influence NBE assessment?")
    print("      • How do age, gender, and risk factors change the prediction?")
    print()
    print("🏥 Variables:")
    print("   Dependent: NBE (Nachbehandlungsempfehlungen) - binary (0=No, 1=Yes)")
    print("   Independent: P, FLScore, StatusP, StatusFL, Gender, Age, Risk Factor")
    print()
    print("📊 Methods:")
    print("   • Spearman correlation for healing groups vs contacts/duration")
    print("   • Logistic regression with odds ratios and significance testing")
    print("   • Model diagnostics and assumption checking")
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
        # Initialize and run logistic regression analysis
        analyzer = LogisticRegressionAnalyzer(
            cleaned_dataset_path=cleaned_dataset_path,
            log_folder=log_folder,
            output_folder=output_folder,
            plot_folder=plot_folder
        )

        analyzer.run_complete_analysis()

        print(f"\n🎉 Regression & Correlation Analysis completed successfully!")
        print(f"\n📋 ANALYSES COMPLETED:")
        print(f"✅ Spearman Correlation: Healing Groups vs Contacts")
        print(f"✅ Spearman Correlation: Healing Groups vs Call Duration")
        print(f"✅ Logistic Regression: NBE Prediction Model")
        print(f"✅ Model Diagnostics: VIF, Outliers, Sample Size")
        print(f"✅ Results: Coefficients, P-values, Odds Ratios")
        print(f"✅ Comprehensive Final Report")
        print(f"\n📁 Check the output folders for:")
        print(f"   • Detailed statistical results (CSV files)")
        print(f"   • Visualization plots (PNG files)")
        print(f"   • Model diagnostics and assumptions")
        print(f"   • Comprehensive final report")

    except Exception as e:
        print(f"❌ Regression analysis failed: {str(e)}")
        return


if __name__ == "__main__":
    main()