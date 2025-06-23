import os
import shutil
import pandas as pd
import random
from datetime import datetime, timedelta

def duplicate_pdf_files(source_folder, target_folder, prefix, target_count):
    """Duplicate PDF files to reach target count"""
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

def duplicate_ivc_files(source_folder, target_folder, prefix, target_count):
    """Duplicate IVC files to reach target count"""
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

def generate_dummy_csv(output_path, num_rows=100):
    """Generate dummy CSV data with solar cell measurements"""
    # Headers taken from DataLog2025-01.csv
    headers = [
        'Cell(title)', 'Comment(EFF)', 'User', 'Ref', 'ID', 'Date', 'Time',
        'Module type', 'Pmax', 'FF', 'Voc', 'Isc', 'Vpmax', 'Ipmax', 'Irr',
        'CIrr', 'TMod', 'CTMod', 'Rs', 'Rsh', 'CellEff', 'ModEff', 'LTI',
        'PN', 'ClassBin', 'MeasStat', 'MachStat'
    ]

    # Function to generate dummy values for each column
    def generate_dummy_row():
        base_date = datetime.now()
        return {
            'Cell(title)': f"PR{random.randint(1000,9999)}D{random.randint(1,9)}",
            'Comment(EFF)': f"EFF-{round(random.uniform(18, 23), 2)}%",
            'User': f"{random.randint(100000,999999)}AB",
            'Ref': f"I5{random.randint(100000,999999)}{random.choice(['A', 'B'])}",
            'ID': f"{random.randint(1000,9999)}",
            'Date': base_date.strftime("%d-%m-%Y"),
            'Time': base_date.strftime("%H:%M:%S"),
            'Module type': random.choice(["Low Power", "Medium Power", "High Power"]),
            'Pmax': round(random.uniform(400, 600), 3),
            'FF': round(random.uniform(0.7, 0.85), 6),
            'Voc': round(random.uniform(30, 55), 6),
            'Isc': round(random.uniform(8, 15), 6),
            'Vpmax': round(random.uniform(25, 45), 6),
            'Ipmax': round(random.uniform(7, 14), 6),
            'Irr': round(random.uniform(800, 1000), 6),
            'CIrr': 1000,
            'TMod': round(random.uniform(25, 35), 1),
            'CTMod': 25,
            'Rs': round(random.uniform(0.1, 0.3), 5),
            'Rsh': round(random.uniform(200, 400), 5),
            'CellEff': round(random.uniform(19, 22), 6),
            'ModEff': 40,
            'LTI': random.choice(["Isc-Voc", "Constant"]),
            'PN': random.choice(["Linear IV", "Step IV"]),
            'ClassBin': random.choice(["yes", "no"]),
            'MeasStat': round(random.uniform(0.0001, 0.001), 6),
            'MachStat': round(random.uniform(0.1, 0.3), 7),
        }

    # Generate dummy data
    data = [generate_dummy_row() for _ in range(num_rows)]

    # Create DataFrame and save to CSV
    df_dummy = pd.DataFrame(data)
    df_dummy.to_csv(output_path, index=False)

    print(f"Data Log CSV file '{output_path}' created successfully with {num_rows} rows.")

def duplicate_images(source_folder, target_folder, prefix, target_count):
    """Duplicate image files to reach target count"""
    # Create the target folder if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # Get the list of images in the source folder
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    image_files = [f for f in os.listdir(source_folder) 
                   if os.path.isfile(os.path.join(source_folder, f)) and 
                   any(f.lower().endswith(ext) for ext in image_extensions)]
    
    # Calculate how many times to duplicate each image
    num_images = len(image_files)
    if num_images == 0:
        print("No images found in the source folder.")
        return
    
    print(f"Found {num_images} images in the source folder.")
    
    # First, copy all original files to target folder
    print("Copying original images to target folder...")
    copied_count = 0
    for original_image in image_files:
        original_path = os.path.join(source_folder, original_image)
        target_path = os.path.join(target_folder, original_image)
        
        try:
            shutil.copyfile(original_path, target_path)
            copied_count += 1
        except Exception as e:
            print(f"Error copying {original_image}: {str(e)}")
    
    print(f"Successfully copied {copied_count} original images to target folder.")
    
    # Calculate how many more images are needed
    images_needed = target_count - num_images
    if images_needed <= 0:
        print("The target count is already reached with original images.")
        return
    
    print(f"Need to create {images_needed} additional duplicate images.")
    
    # Loop to duplicate images
    duplicated_count = 0
    for i in range(images_needed):
        # Select an image to duplicate (cycle through available images)
        original_image = image_files[i % num_images]
        original_path = os.path.join(source_folder, original_image)
        
        # Get the original file extension
        _, ext = os.path.splitext(original_image)
        
        # Generate a new filename with datetime and index to ensure uniqueness
        datetime_suffix = datetime.now().strftime('%y%m%d_%H%M%S')
        new_filename = f"{prefix}{datetime_suffix}_{i}{ext}"
        new_path = os.path.join(target_folder, new_filename)
        
        # Copy the image to the new filename
        try:
            shutil.copyfile(original_path, new_path)
            duplicated_count += 1
            
            # Optional: Print progress for large operations
            if duplicated_count % 10 == 0:
                print(f"Progress: {duplicated_count}/{images_needed} images duplicated...")
                
        except Exception as e:
            print(f"Error copying {original_image} to {new_filename}: {str(e)}")
    
    print(f"Successfully duplicated {duplicated_count} images.")
    print(f"Total images in target folder: {copied_count + duplicated_count}")

def main():
    """Main function to demonstrate usage of all functions"""
    print("File Duplication and Data Generation Tool")
    print("=" * 50)
    
    # Example usage - uncomment and modify as needed
    
    # 1. Duplicate PDF files
    print("\n1. Duplicating PDF files...")
    duplicate_pdf_files(
        source_folder='D:\\pdf_source',
        target_folder='D:\\pdf_target',
        prefix='A8E4A',
        target_count=5
    )
    
    # 2. Duplicate IVC files
    print("\n2. Duplicating IVC files...")
    duplicate_ivc_files(
        source_folder='D:\\ivc_source',
        target_folder='D:\\ivc_target',
        prefix='A7F',
        target_count=10
    )
    
    # 3. Generate dummy CSV data
    print("\n3. Generating dummy CSV data...")
    generate_dummy_csv(
        output_path="D:\\csv\\DataLog.csv",
        num_rows=100
    )
    
    # 4. Duplicate images
    print("\n4. Duplicating images...")
    duplicate_images(
        source_folder='D:\\new_data',
        target_folder='D:\\new_data1',
        prefix='A50339B_JIN_A_',
        target_count=50
    )
    
    print("\nAll functions are available. Uncomment the sections in main() to use them.")

if __name__ == "__main__":
    main()