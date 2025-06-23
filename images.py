import os
import shutil
from datetime import datetime

def duplicate_images(source_folder, target_folder, prefix, target_count):
    # Create the target folder if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Get the list of images in the source folder
    image_files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]

    # Calculate how many times to duplicate each image
    num_images = len(image_files)
    if num_images == 0:
        print("No images found in the source folder.")
        return

    # Calculate how many more images are needed
    images_needed = target_count - num_images
    if images_needed <= 0:
        print("The folder already contains enough images.")
        return

    # Loop to duplicate images
    for i in range(images_needed):
        # Select an image to duplicate
        original_image = image_files[i % num_images]
        original_path = os.path.join(source_folder, original_image)

        # Generate a new filename with datetime and index to ensure uniqueness
        datetime_suffix = datetime.now().strftime('%y%m%d_%H%M%S')
        new_filename = f"{prefix}{datetime_suffix}_{i}.jpg"  # Assuming images are in jpg format
        new_path = os.path.join(target_folder, new_filename)

        # Copy the image to the new filename
        shutil.copyfile(original_path, new_path)

    print(f"Duplicated images to reach a total of {target_count} images.")

# Parameters
source_folder = 'D:\\Amruth\\new_data'
target_folder = 'D:\\Amruth\\new_data1'
prefix = 'A50339B_JIN_A_'
target_count = 50

# Call the function
duplicate_images(source_folder, target_folder, prefix, target_count)