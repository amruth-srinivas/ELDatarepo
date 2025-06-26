def get_next_sequence_number(base_target_folder):
    """
    Find the highest existing sequence number across all folders and return the next number
    """
    max_number = 50339  # Starting number (A50339B.jpg -> 50339)
    
    # Walk through all subdirectories to find existing files
    for root, dirs, files in os.walk(base_target_folder):
        for file in files:
            # Check if filename matches pattern A[NUMBER]B.jpg
            if file.startswith('A') and file.endswith('B.jpg') and len(file) >= 11:
                try:
                    # Extract number from filename (e.g., A50339B.jpg -> 50339)
                    number_part = file[1:-5]  # Remove 'A' and 'B.jpg'
                    if number_part.isdigit():
                        current_number = int(number_part)
                        max_number = max(max_number, current_number)
                except ValueError:
                    continue
    
    return max_number + 1

import os
import shutil
from datetime import datetime

def create_date_folder_structure(base_folder):
    """Create folder structure: base_folder/YYYY/MM/DD/"""
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    
    date_path = os.path.join(base_folder, year, month, day)
    
    # Create the date-based folder structure if it doesn't exist
    if not os.path.exists(date_path):
        os.makedirs(date_path)
    
    return date_path

def duplicate_images(source_folder, base_target_folder, category, start_number, target_count):
    """
    Duplicate images from source to target folder with date-based structure
    
    Args:
        source_folder (str): Path to source images
        base_target_folder (str): Base path for target (e.g., 'D:\\Amruth\\processed_data')
        category (str): Either 'NG' or 'NORMAL'
        start_number (int): Starting sequence number for this category
        target_count (int): Total number of images needed
    
    Returns:
        int: Next available sequence number
    """
    
    # Create date-based folder structure
    date_folder = create_date_folder_structure(base_target_folder)
    
    # Create category folder (NG or NORMAL) inside the date folder
    category_folder = os.path.join(date_folder, category)
    if not os.path.exists(category_folder):
        os.makedirs(category_folder)

    # Get the list of images in the source folder
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    image_files = [f for f in os.listdir(source_folder) 
                   if os.path.isfile(os.path.join(source_folder, f)) 
                   and any(f.lower().endswith(ext) for ext in image_extensions)]

    # Calculate how many times to duplicate each image
    num_images = len(image_files)
    if num_images == 0:
        print(f"No images found in the source folder: {source_folder}")
        return

    print(f"Found {num_images} images in source folder")
    
    # Check if we already have enough images in the target folder
    existing_images = [f for f in os.listdir(category_folder) 
                      if os.path.isfile(os.path.join(category_folder, f)) 
                      and f.startswith('A') and f.endswith('B.jpg')]
    
    current_count = len(existing_images)
    print(f"Current images in {category} folder: {current_count}")
    
    # Calculate how many more images are needed
    images_needed = target_count - current_count
    if images_needed <= 0:
        print(f"The {category} folder already contains enough images ({current_count}/{target_count}).")
        return start_number

    print(f"Need to add {images_needed} more images to reach target of {target_count}")

    # Loop to duplicate images
    duplicated_count = 0
    current_sequence = start_number
    
    for i in range(images_needed):
        # Select an image to duplicate (cycle through available images)
        original_image = image_files[i % num_images]
        original_path = os.path.join(source_folder, original_image)
        
        # Generate sequential filename: A[NUMBER]B.jpg
        new_filename = f"A{current_sequence}B.jpg"
        new_path = os.path.join(category_folder, new_filename)

        # Ensure the filename is unique (skip if exists)
        while os.path.exists(new_path):
            current_sequence += 1
            new_filename = f"A{current_sequence}B.jpg"
            new_path = os.path.join(category_folder, new_filename)

        # Copy the actual image content and save as .jpg
        try:
            # Copy the image file content to the new path as .jpg
            shutil.copy2(original_path, new_path)
            print(f"{new_filename}")  # Just show the new filename
            duplicated_count += 1
            current_sequence += 1
        except Exception as e:
            print(f"Error copying {original_image}: {e}")
            # Skip to next sequence number even if copy failed
            current_sequence += 1

    print(f"Successfully duplicated {duplicated_count} images to {category_folder}")
    print(f"Total images in {category} folder: {current_count + duplicated_count}")
    print(f"Next sequence number: A{current_sequence}B.jpg")
    
    return current_sequence

def process_both_categories(ng_source, normal_source, base_target_folder, target_count):
    """
    Process both NG and NORMAL categories
    
    Args:
        ng_source (str): Path to NG (not good) images
        normal_source (str): Path to NORMAL (good) images  
        base_target_folder (str): Base target folder path
        target_count (int): Target count for each category
    """
    
    print("="*60)
    print(f"Starting image duplication process...")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target folder structure: {base_target_folder}/YYYY/MM/DD/[NG|NORMAL]")
    print("="*60)
    
    # Get the next available sequence number
    next_number = get_next_sequence_number(base_target_folder)
    print(f"Starting sequence number: A{next_number}B.jpg")
    
    # Process NG images
    if os.path.exists(ng_source):
        print("\nProcessing NG (Not Good) images...")
        next_number = duplicate_images(ng_source, base_target_folder, 'NG', next_number, target_count)
    else:
        print(f"\nWarning: NG source folder not found: {ng_source}")
    
    # Process NORMAL images  
    if os.path.exists(normal_source):
        print("\nProcessing NORMAL (Good) images...")
        next_number = duplicate_images(normal_source, base_target_folder, 'NORMAL', next_number, target_count)
    else:
        print(f"\nWarning: NORMAL source folder not found: {normal_source}")
    
    print("\n" + "="*60)
    print("Image duplication process completed!")
    print(f"Next available sequence number: A{next_number}B.jpg")
    print("="*60)

# Parameters - Update these paths according to your setup
ng_source_folder = 'D:\\ng'          # Path to NG images
normal_source_folder = 'D:\\normal'   # Path to NORMAL images
base_target_folder = 'D:\\ELimagesnew'           # Base folder for date structure
target_count = 10    
                                       

# Call the function
if __name__ == "__main__":
    process_both_categories(
        ng_source=ng_source_folder,
        normal_source=normal_source_folder, 
        base_target_folder=base_target_folder,
        target_count=target_count
    )