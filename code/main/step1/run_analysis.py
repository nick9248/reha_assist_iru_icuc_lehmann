"""
Quick runner script for dataset analysis
Run this script to start the analysis process
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from dataset_analyzer import DatasetAnalyzer

# Load environment variables from .env file
load_dotenv()

def main():
    """Main function to run the dataset analysis"""

    # Load environment variables
    dataset_path = os.getenv('DATASET')
    log_folder = os.getenv('LOG_FOLDER', 'logs')
    output_folder = os.getenv('OUTPUT_FOLDER', 'output')
    plot_folder = os.getenv('PLOT_FOLDER', 'plots')
    headers_file = os.getenv('HEADERS_FILE')  # Optional headers file

    # Validate dataset path
    if not dataset_path:
        print("❌ Error: DATASET environment variable not set!")
        print("Please set the DATASET environment variable to your dataset file path")
        return

    if not Path(dataset_path).exists():
        print(f"❌ Error: Dataset file not found at: {dataset_path}")
        return

    print(f"📊 Dataset: {dataset_path}")
    print(f"📁 Log folder: {log_folder}")
    print(f"📁 Output folder: {output_folder}")
    print(f"📁 Plot folder: {plot_folder}")
    if headers_file:
        print(f"📋 Headers file: {headers_file}")
    print("-" * 50)

    try:
        # Initialize and run analysis
        analyzer = DatasetAnalyzer(dataset_path, log_folder, output_folder, plot_folder, headers_file)
        analyzer.run_complete_analysis()

    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return

if __name__ == "__main__":
    main()