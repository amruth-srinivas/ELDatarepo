import os
import shutil
from datetime import datetime

def duplicate_pdf_files(source_folder, target_folder, prefix, target_count):
    # Create the target folder if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # Get the list of .pdf files in the source folder
    pdf_files = [f for f in os.listdir(source_folder) 
                 if os.path.isfile(os.path.join(source_folder, f)) and f.lower().endswith('.pdf')]
    
    # Calculate how many times to duplicate each file
    num_files = len(pdf_files)
    if num_files == 0:
        print("No .pdf files found in the source folder.")
        return
    
    print(f"Found {num_files} .pdf files in the source folder.")
    
    # First, copy all original files to target folder
    print("Copying original files to target folder...")
    copied_count = 0
    for original_file in pdf_files:
        original_path = os.path.join(source_folder, original_file)
        target_path = os.path.join(target_folder, original_file)
        
        try:
            shutil.copyfile(original_path, target_path)
            copied_count += 1
        except Exception as e:
            print(f"Error copying {original_file}: {str(e)}")
    
    print(f"Successfully copied {copied_count} original .pdf files to target folder.")
    
    # Calculate how many more files are needed
    files_needed = target_count - num_files
    if files_needed <= 0:
        print("The target count is already reached with original files.")
        return
    
    print(f"Need to create {files_needed} additional duplicate .pdf files.")
    
    # Generate unique numbers for naming (continuing from existing pattern)
    # Extract existing numbers to find the next available number
    existing_numbers = set()
    for file in pdf_files:
        # Extract number from filename like A8E4A84.pdf -> 84
        if file.startswith(prefix):  # A8E4A
            try:
                # Remove prefix and .pdf extension, get the remaining number
                name_without_ext = file.replace('.pdf', '')
                number_part = name_without_ext[len(prefix):]  # Get part after A8E4A
                if number_part.isdigit():
                    existing_numbers.add(int(number_part))
            except:
                pass
    
    # Find next available number
    if existing_numbers:
        next_number = max(existing_numbers) + 1
    else:
        # If no pattern found, use datetime-based naming
        next_number = None
    
    # Loop to duplicate files with proper naming
    duplicated_count = 0
    for i in range(files_needed):
        # Select a file to duplicate (cycle through available files)
        original_file = pdf_files[i % num_files]
        original_path = os.path.join(source_folder, original_file)
        
        # Generate new filename
        if next_number is not None:
            # Follow the existing pattern (e.g., A8E4A##.pdf)
            new_filename = f"{prefix}{next_number + i:02d}.pdf"
        else:
            # Use datetime-based naming if no pattern detected
            datetime_suffix = datetime.now().strftime('%y%m%d_%H%M%S_%f')[:-3]
            new_filename = f"{prefix}DUPLICATE_{datetime_suffix}_{i}.pdf"
        
        new_path = os.path.join(target_folder, new_filename)
        
        # Copy the file to the new filename
        try:
            shutil.copyfile(original_path, new_path)
            duplicated_count += 1
            
            # Optional: Print progress for large operations
            if duplicated_count % 10 == 0:
                print(f"Progress: {duplicated_count}/{files_needed} files duplicated...")
                
        except Exception as e:
            print(f"Error copying {original_file} to {new_filename}: {str(e)}")
    
    print(f"Successfully duplicated {duplicated_count} .pdf files.")
    print(f"Total .pdf files in target folder: {copied_count + duplicated_count}")

# Parameters for .pdf files
source_folder = 'D:\\pdf_source'
target_folder = 'D:\\pdf_target'
prefix = 'A8E4A'  # Your PDF naming pattern
target_count = 5

# Call the function
duplicate_pdf_files(source_folder, target_folder, prefix, target_count)
