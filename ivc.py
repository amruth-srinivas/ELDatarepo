import os
import shutil
from datetime import datetime

def duplicate_ivc_files(source_folder, target_folder, prefix, target_count):
    # Create the target folder if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # Get the list of .ivc files in the source folder
    ivc_files = [f for f in os.listdir(source_folder) 
                 if os.path.isfile(os.path.join(source_folder, f)) and f.lower().endswith('.ivc')]
    
    # Calculate how many times to duplicate each file
    num_files = len(ivc_files)
    if num_files == 0:
        print("No .ivc files found in the source folder.")
        return
    
    print(f"Found {num_files} .ivc files in the source folder.")
    
    # First, copy all original files to target folder
    print("Copying original files to target folder...")
    copied_count = 0
    for original_file in ivc_files:
        original_path = os.path.join(source_folder, original_file)
        target_path = os.path.join(target_folder, original_file)
        
        try:
            shutil.copyfile(original_path, target_path)
            copied_count += 1
        except Exception as e:
            print(f"Error copying {original_file}: {str(e)}")
    
    print(f"Successfully copied {copied_count} original .ivc files to target folder.")
    
    # Calculate how many more files are needed
    files_needed = target_count - num_files
    if files_needed <= 0:
        print("The target count is already reached with original files.")
        return
    
    print(f"Need to create {files_needed} additional duplicate .ivc files.")
    
    # Generate unique numbers for naming (continuing from existing pattern)
    # Extract existing numbers to find the next available number
    existing_numbers = set()
    for file in ivc_files:
        # Extract number from filename like A7F2555.ivc -> 2555
        if file.startswith(prefix[:3]):  # A7F
            try:
                number_part = file[3:7]  # Get 4 digits after A7F
                existing_numbers.add(int(number_part))
            except:
                pass
    
    # Find next available number
    next_number = max(existing_numbers) + 1 if existing_numbers else 1000
    
    # Loop to duplicate files with proper naming
    duplicated_count = 0
    for i in range(files_needed):
        # Select a file to duplicate (cycle through available files)
        original_file = ivc_files[i % num_files]
        original_path = os.path.join(source_folder, original_file)
        
        # Generate new filename following the pattern A7F####.ivc
        new_filename = f"A7F{next_number + i:04d}.ivc"
        new_path = os.path.join(target_folder, new_filename)
        
        # Copy the file to the new filename
        try:
            shutil.copyfile(original_path, new_path)
            duplicated_count += 1
            
            # Optional: Print progress for large operations
            if duplicated_count % 10 == 0:
                print(f"Progress: {duplicated_count}/{files_needed} files duplicated...")
                
        except Exception as e:
            print(f"Error copying {original_file}: {str(e)}")
    
    print(f"Successfully duplicated {duplicated_count} .ivc files.")
    print(f"Total .ivc files in target folder: {copied_count + duplicated_count}")

# Parameters for .ivc files
source_folder = 'D:\\ivc_source'
target_folder = 'D:\\ivc_target'
prefix = 'A7F'  # This will be used for pattern matching
target_count = 10

# Call the function
duplicate_ivc_files(source_folder, target_folder, prefix, target_count)