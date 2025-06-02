"""
Step 4: Case Analysis Runner Script
Run this script to perform case analysis on the cleaned dataset

Analysis Questions:
- Q1: How many phone calls per case were made on average?
- Q2: How long did the phone calls last on average per case?
- Q3: How often were risk factors indicated?
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from case_analyzer import CaseAnalyzer

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
    """Main function to run the case analysis"""

    print("🔍 Step 4: Case Analysis - Fallanalyse")
    print("📋 Questions to be answered:")
    print("   Q1: How many phone calls per case were made on average?")
    print("   Q2: How long did the phone calls last on average per case?")
    print("   Q3: How often were risk factors indicated?")
    print("-" * 60)

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
    print("-" * 60)

    try:
        # Initialize and run case analysis
        analyzer = CaseAnalyzer(
            cleaned_dataset_path=cleaned_dataset_path,
            log_folder=log_folder,
            output_folder=output_folder,
            plot_folder=plot_folder
        )

        analyzer.run_complete_analysis()

        print(f"\n🎉 Case analysis completed successfully!")
        print(f"\n📋 ANALYSIS QUESTIONS ANSWERED:")
        print(f"✅ Q1: Average phone calls per case")
        print(f"✅ Q2: Average duration of phone calls per case (with box plots)")
        print(f"✅ Q3: Risk factor frequency and consistency analysis")
        print(f"\n📁 Check the output folder for detailed results, plots, and logs!")

    except Exception as e:
        print(f"❌ Case analysis failed: {str(e)}")
        return


if __name__ == "__main__":
    main()