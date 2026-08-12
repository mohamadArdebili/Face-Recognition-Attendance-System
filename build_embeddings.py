#!/usr/bin/env python3
"""
Build Face Embeddings
Creates face encodings from employee photos in dataset folder (incremental mode)
"""

import os
import cv2
import face_recognition
import pickle
from pathlib import Path
import config

def build_embeddings():
    """
    Build face encodings from dataset (incremental mode)
    - Load existing encodings if available
    - Add new employees
    - Remove deleted employees
    - Only encode what's needed
    """
    print("=" * 60)
    print("Building Face Embeddings")
    print("=" * 60)
    print()
    
    # Check dataset path
    if not os.path.exists(config.DATASET_PATH):
        print(f"ERROR: Dataset not found at {config.DATASET_PATH}")
        print("Please create the dataset folder and add employee photos.")
        return False
    
    # Get employee folders
    employee_folders = [f for f in os.listdir(config.DATASET_PATH) 
                       if os.path.isdir(os.path.join(config.DATASET_PATH, f))]
    
    if not employee_folders:
        print(f"ERROR: No employee folders found in {config.DATASET_PATH}")
        print("Please create folders for each employee and add their photos.")
        return False
    
    print(f"Found {len(employee_folders)} employee folders:")
    for folder in employee_folders:
        print(f"  - {folder}")
    print()
    
    # Load existing encodings if available
    all_encodings = []
    all_names = []
    existing_employees = set()
    
    if os.path.exists(config.ENCODINGS_PATH):
        try:
            print("Loading existing encodings...")
            with open(config.ENCODINGS_PATH, 'rb') as f:
                data = pickle.load(f)
                all_encodings = data.get('encodings', [])
                all_names = data.get('names', [])
                existing_employees = set(all_names)
            print(f"  Loaded {len(all_encodings)} existing encodings")
            print(f"  Existing employees: {sorted(set(all_names))}")
            print()
        except Exception as e:
            print(f"  Warning: Could not load existing encodings: {str(e)}")
            print(f"  Starting fresh build...")
            all_encodings = []
            all_names = []
            existing_employees = set()
            print()
    else:
        print("No existing encodings found. Building from scratch...")
        print()
    
    # Determine what needs to be done
    current_employees = set(employee_folders)
    new_employees = current_employees - existing_employees
    removed_employees = existing_employees - current_employees
    
    if removed_employees:
        print(f"Employees to remove: {sorted(removed_employees)}")
        # Remove encodings for deleted employees
        indices_to_keep = [i for i, name in enumerate(all_names) if name not in removed_employees]
        all_encodings = [all_encodings[i] for i in indices_to_keep]
        all_names = [all_names[i] for i in indices_to_keep]
        print(f"  Removed {len(removed_employees)} employee(s)")
        print()
    
    if new_employees:
        print(f"New employees to encode: {sorted(new_employees)}")
        print()
    else:
        print("No new employees to encode.")
        print()
    
    if not new_employees and not removed_employees:
        print("All encodings are up to date!")
        print()
        return True
    
    # Process only new employees
    total_images = 0
    successful_encodings = 0
    
    for employee_name in sorted(new_employees):
        employee_path = os.path.join(config.DATASET_PATH, employee_name)
        
        print(f"Processing: {employee_name}")
        
        # Get all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(Path(employee_path).glob(f"*{ext}"))
            image_files.extend(Path(employee_path).glob(f"*{ext.upper()}"))
        
        if not image_files:
            print(f"  WARNING: No images found for {employee_name}")
            continue
        
        employee_encodings = 0
        
        for image_path in image_files:
            total_images += 1
            
            try:
                # Load image
                image = cv2.imread(str(image_path))
                
                if image is None:
                    print(f"  - Skipped (cannot read): {image_path.name}")
                    continue
                
                # Convert BGR to RGB
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                face_locations = face_recognition.face_locations(
                    rgb_image,
                    model=config.RECOGNITION_MODEL
                )
                
                if not face_locations:
                    print(f"  - Skipped (no face): {image_path.name}")
                    continue
                
                # Encode faces
                face_encodings = face_recognition.face_encodings(
                    rgb_image,
                    face_locations
                )
                
                # Use first face only
                if face_encodings:
                    all_encodings.append(face_encodings[0])
                    all_names.append(employee_name)
                    employee_encodings += 1
                    successful_encodings += 1
                    print(f"  + Encoded: {image_path.name}")
                
            except Exception as e:
                print(f"  - Error processing {image_path.name}: {str(e)}")
        
        print(f"  Total encodings: {employee_encodings}")
        print()
    
    # Save encodings
    if not all_encodings:
        print("ERROR: No face encodings created!")
        print("Please check your dataset images.")
        return False
    
    print(f"Summary:")
    if new_employees:
        print(f"  New images processed: {total_images}")
        print(f"  New encodings added: {successful_encodings}")
    if removed_employees:
        print(f"  Employees removed: {len(removed_employees)}")
    print(f"  Total employees in system: {len(set(all_names))}")
    print(f"  Total encodings stored: {len(all_encodings)}")
    print()
    
    # Create data directory if needed
    data_dir = os.path.dirname(config.ENCODINGS_PATH)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Save to pickle file
    data = {
        'encodings': all_encodings,
        'names': all_names
    }
    
    # Save safely with backup
    temp_path = config.ENCODINGS_PATH + '.tmp'
    backup_path = config.ENCODINGS_PATH + '.backup'
    
    try:
        # Write to temp file first
        with open(temp_path, 'wb') as f:
            pickle.dump(data, f)
        
        # Backup existing file if it exists
        if os.path.exists(config.ENCODINGS_PATH):
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(config.ENCODINGS_PATH, backup_path)
        
        # Move temp to final location
        os.rename(temp_path, config.ENCODINGS_PATH)
        
        # Remove backup after successful save
        if os.path.exists(backup_path):
            os.remove(backup_path)
            
    except Exception as e:
        print(f"ERROR: Failed to save encodings: {str(e)}")
        # Restore backup if save failed
        if os.path.exists(backup_path) and not os.path.exists(config.ENCODINGS_PATH):
            os.rename(backup_path, config.ENCODINGS_PATH)
        return False
    
    print(f"Face encodings saved to: {config.ENCODINGS_PATH}")
    print()
    print("=" * 60)
    print("Build Complete!")
    print("You can now run: python app.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = build_embeddings()
        if not success:
            input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n\nFATAL ERROR: {str(e)}")
        input("\nPress Enter to exit...")
