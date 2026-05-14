"""
Quick Start Script - Run Complete Pipeline
This script runs all steps of the crack detection pipeline in sequence
"""

import os
import sys
import subprocess
import time


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print_header(f"STEP: {description}")
    print(f"Running: {script_name}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False,
            text=True
        )
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ {description} completed successfully!")
        print(f"⏱️  Time taken: {elapsed_time:.2f} seconds")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running {script_name}")
        print(f"Error: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted by user")
        return False


def main():
    """Main function to run all scripts"""
    
    print("\n" + "="*80)
    print("  CONCRETE CRACK DETECTION - COMPLETE PIPELINE")
    print("="*80)
    print("\nThis script will run all steps of the crack detection pipeline:")
    print("  1. Data Analysis")
    print("  2. Data Loader Test")
    print("  3. Model Architecture Test")
    print("  4. Train/Val/Test Split")
    print("  5. Data Augmentation Visualization")
    print("  6. Model Training (This will take the longest!)")
    print("  7. Model Evaluation")
    print("  8. Prediction Demo")
    
    print("\n⚠️  WARNING: Step 6 (Training) can take 30+ minutes depending on your hardware!")
    print("You can skip training by pressing Ctrl+C when prompted.\n")
    
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Pipeline cancelled by user")
        return
    
    # Define pipeline steps
    steps = [
        ("01_data_analysis.py", "Data Analysis and Visualization"),
        ("02_data_loader.py", "Data Loader Test"),
        ("03_model.py", "Model Architecture Test"),
        ("04_train_val_test_split.py", "Create Train/Val/Test Splits"),
        ("05_data_augmentation.py", "Data Augmentation Visualization"),
    ]
    
    # Ask about training
    print("\n" + "-"*80)
    print("TRAINING STEP")
    print("-"*80)
    print("The training step can take 30+ minutes to several hours.")
    print("You can skip it and run 06_train.py manually later.")
    
    train_response = input("\nDo you want to run training now? (yes/no): ").strip().lower()
    
    if train_response in ['yes', 'y']:
        steps.append(("06_train.py", "Model Training"))
        include_eval = True
    else:
        print("\n⚠️  Skipping training step")
        print("You can run it later with: python 06_train.py")
        include_eval = False
    
    # Run all steps
    total_start_time = time.time()
    completed_steps = 0
    
    for script_name, description in steps:
        if not os.path.exists(script_name):
            print(f"\n❌ Error: {script_name} not found")
            continue
        
        success = run_script(script_name, description)
        
        if success:
            completed_steps += 1
        else:
            print(f"\n⚠️  Failed at step: {description}")
            retry = input("Do you want to continue with remaining steps? (yes/no): ").strip().lower()
            if retry not in ['yes', 'y']:
                break
    
    # Run evaluation and prediction if training was completed
    if include_eval and completed_steps == len(steps):
        # Check if model checkpoint exists
        if os.path.exists('checkpoints/best_model.pth'):
            run_script("07_evaluate.py", "Model Evaluation")
            run_script("08_predict.py", "Prediction Demo")
        else:
            print("\n⚠️  Model checkpoint not found. Skipping evaluation and prediction.")
    
    # Final summary
    total_time = time.time() - total_start_time
    
    print("\n" + "="*80)
    print("  PIPELINE SUMMARY")
    print("="*80)
    print(f"\nCompleted steps: {completed_steps}/{len(steps)}")
    print(f"Total time: {total_time/60:.2f} minutes")
    
    print("\n📁 Generated Files and Directories:")
    
    files_to_check = [
        ("dataset_samples.png", "Dataset sample visualization"),
        ("class_distribution.png", "Class distribution plot"),
        ("data_loader_samples.png", "Data loader samples"),
        ("augmentation_examples.png", "Augmentation examples"),
        ("augmentation_levels.png", "Augmentation levels"),
        ("data_splits/", "Train/val/test splits"),
        ("checkpoints/", "Model checkpoints"),
        ("evaluation_results/", "Evaluation results"),
        ("predictions_demo.png", "Prediction demo"),
    ]
    
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path:30s} - {description}")
        else:
            print(f"  ✗ {file_path:30s} - Not generated")
    
    print("\n" + "="*80)
    print("  ✅ PIPELINE COMPLETE!")
    print("="*80)
    
    print("\n📖 Next Steps:")
    print("  1. Check the generated visualizations")
    print("  2. Review training metrics in checkpoints/")
    print("  3. Examine evaluation results in evaluation_results/")
    print("  4. Use 08_predict.py to make predictions on new images")
    print("\n📚 See README.md for detailed documentation")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        print("You can run individual scripts manually:")
        print("  python 01_data_analysis.py")
        print("  python 02_data_loader.py")
        print("  ... etc.")
