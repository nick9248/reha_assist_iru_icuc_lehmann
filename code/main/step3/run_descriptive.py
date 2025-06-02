"""
Step 3: Descriptive Analysis Runner Script
Run this script to perform descriptive analysis on the cleaned dataset
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from descriptive_analyzer import DescriptiveAnalyzer

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
    """Main function to run the descriptive analysis"""

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
            print("Please run Step 2 (data cleaning) first, or set CLEANED_DATASET environment variable.")
            return

    # Validate cleaned dataset path
    if not Path(cleaned_dataset_path).exists():
        print(f"❌ Error: Cleaned dataset file not found at: {cleaned_dataset_path}")
        return

    print(f"📊 Cleaned dataset: {cleaned_dataset_path}")
    print(f"📁 Log folder: {log_folder}")
    print(f"📁 Output folder: {output_folder}")
    print(f"📁 Plot folder: {plot_folder}")
    print("-" * 50)

    try:
        # Initialize and run descriptive analysis
        analyzer = DescriptiveAnalyzer(
            cleaned_dataset_path=cleaned_dataset_path,
            log_folder=log_folder,
            output_folder=output_folder,
            plot_folder=plot_folder
        )

        analyzer.run_complete_analysis()

        print(f"\n🎉 Descriptive analysis completed successfully!")
        print(f"\n📋 ANALYSIS QUESTIONS ANSWERED:")
        print(f"✅ How many cases were advised in total?")
        print(f"✅ How many women and men were advised in total (with normality testing)?")
        print(f"✅ What is the average age of the respondents overall?")
        print(f"\n📁 Check the output folder for detailed results and plots!")

    except Exception as e:
        print(f"❌ Descriptive analysis failed: {str(e)}")
        return


if __name__ == "__main__":
    main()