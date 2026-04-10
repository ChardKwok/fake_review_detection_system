"""
Model Training Script
Downloads (if needed) and trains the TF-IDF + Naive Bayes model.

Usage:
    python train_model.py

This script will:
1. Look for CSV dataset in the data/ directory
2. Train the TF-IDF + Naive Bayes classifier
3. Save the trained model to models/ directory
4. Print accuracy metrics and classification report

Dataset:
    Place your dataset CSV in the data/ folder.
    Recommended: Download from Kaggle - "Fake Reviews Dataset"
    https://www.kaggle.com/datasets/mexwell/fake-reviews-dataset

    Expected CSV columns:
    - 'category': Product category (e.g., Home_and_Kitchen_5)
    - 'rating': Star rating (1-5)
    - 'label': 'CG' (Computer Generated = Fake) or 'OR' (Original = Genuine)
    - 'text_': The review text
"""
import os
import sys
import glob

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.ml_model import FakeReviewModel
from utils.database import init_database
from config import Config


def find_dataset():
    """Find CSV dataset in the data/ directory."""
    data_dir = os.path.join(os.path.dirname(Config.DATABASE_PATH))
    os.makedirs(data_dir, exist_ok=True)

    # Look for CSV files
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))

    if not csv_files:
        print("=" * 60)
        print("  ERROR: No dataset found!")
        print("=" * 60)
        print()
        print("  Please download a fake reviews dataset and place it")
        print(f"  in the '{data_dir}/' directory.")
        print()
        print("  Recommended datasets:")
        print()
        print("  1. Fake Reviews Dataset (40K reviews, recommended)")
        print("     https://www.kaggle.com/datasets/mexwell/fake-reviews-dataset")
        print("     - Columns: category, rating, label (CG/OR), text_")
        print()
        print("  2. Amazon Labeled Fake Reviews")
        print("     https://www.kaggle.com/datasets/malikawaispy/amazon-labeled-fake-reviews")
        print()
        print("  3. Fake Reviews Detection Dataset")
        print("     https://www.kaggle.com/datasets/syntheticprogrammer/fake-reviews-detection-dataset")
        print()
        print("  After downloading, place the CSV file in:")
        print(f"    {os.path.abspath(data_dir)}/")
        print()
        return None

    if len(csv_files) == 1:
        return csv_files[0]

    # Multiple CSV files found, let user choose
    print("Multiple CSV files found in data/ directory:")
    for i, f in enumerate(csv_files):
        print(f"  [{i + 1}] {os.path.basename(f)}")

    while True:
        try:
            choice = input(f"\nSelect dataset (1-{len(csv_files)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(csv_files):
                return csv_files[idx]
        except (ValueError, KeyboardInterrupt):
            pass
        print("Invalid choice. Please try again.")


def main():
    print("=" * 60)
    print("  Fake Review Detection - Model Training")
    print("=" * 60)

    # Initialize database (for rules)
    print("\n[1/4] Initializing database...")
    init_database()

    # Find dataset
    print("\n[2/4] Looking for dataset...")
    dataset_path = find_dataset()
    if dataset_path is None:
        sys.exit(1)

    print(f"  Using dataset: {dataset_path}")

    # Train model
    print("\n[3/4] Training TF-IDF + Naive Bayes model...")
    print("  This may take a few minutes depending on dataset size...\n")

    model = FakeReviewModel()
    result = model.train(dataset_path)

    # Summary
    print("\n" + "=" * 60)
    print("  Training Complete!")
    print("=" * 60)
    print(f"  Accuracy:          {result['accuracy']:.4f} ({result['accuracy'] * 100:.2f}%)")
    print(f"  Total Samples:     {result['total_samples']}")
    print(f"  Training Samples:  {result['training_samples']}")
    print(f"  Test Samples:      {result['test_samples']}")
    print(f"  Model saved to:    {Config.MODEL_PATH}")
    print(f"  Vectorizer saved:  {Config.VECTORIZER_PATH}")
    print()
    print("  You can now start the server with: python run.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
