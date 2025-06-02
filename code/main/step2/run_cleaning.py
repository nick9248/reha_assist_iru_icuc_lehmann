"""
Step 2: Data Cleaning Runner Script
Run this script to clean the dataset based on Step 1 analysis results
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from data_cleaner import DataCleaner

# Load environment variables from .env file
load_dotenv()


def find_latest_step1_folder(output_folder):
    """Find the most recent Step 1 analysis folder"""
    output_path = Path(output_folder)

    step1_folders = [f for f in output_path.iterdir()
                     if f.is_dir() and f.name.startswith('step1_dataset_analysis_')]

    if not step1_folders:
        raise FileNotFoundError("No Step 1 analysis results found. Please run Step 1 first.")

    # Get the most recent folder by modification time
    latest_folder = max(step1_folders, key=lambda x: x.stat().st_mtime)
    return latest_folder


def main():
    """Main function to run the data cleaning process"""

    # Load environment variables
    dataset_path = os.getenv('DATASET')
    log_folder = os.getenv('LOG_FOLDER', 'logs')
    output_folder = os.getenv('OUTPUT_FOLDER', 'output')

    # Validate dataset path
    if not dataset_path:
        print("❌ Error: DATASET environment variable not set!")
        print("Please set the DATASET environment variable to your dataset file path")
        return

    if not Path(dataset_path).exists():
        print(f"❌ Error: Dataset file not found at: {dataset_path}")
        return

    # Find Step 1 results
    try:
        step1_folder = find_latest_step1_folder(output_folder)
        print(f"📊 Dataset: {dataset_path}")
        print(f"📁 Using Step 1 results: {step1_folder.name}")
        print(f"📁 Log folder: {log_folder}")
        print(f"📁 Output folder: {output_folder}")
        print("-" * 50)

    except FileNotFoundError as e:
        print(f"❌ Error: {str(e)}")
        print("Please run Step 1 (dataset analysis) first before cleaning.")
        return

    try:
        # Initialize and run data cleaning
        cleaner = DataCleaner(
            dataset_path=dataset_path,
            step1_output_folder=step1_folder,
            log_folder=log_folder,
            output_folder=output_folder
        )

        cleaned_file_path = cleaner.run_complete_cleaning()

        print(f"\n🎉 Data cleaning completed successfully!")
        print(f"📄 Cleaned dataset ready at: {cleaned_file_path}")

    except Exception as e:
        print(f"❌ Cleaning failed: {str(e)}")
        return


if __name__ == "__main__":
    main()