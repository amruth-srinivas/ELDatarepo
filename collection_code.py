import json
import os
import time
import shutil
import win32net
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
import hashlib

# PC credentials for accessing shared folders
PC_CREDENTIALS = [
    {'address': '172.18.7.27', 'username': 'SDC3', 'password': 'Zxcvbnm123', 'alias': 'Jigani'},
    
    {'address': '172.18.7.74', 'username': 'SDC2', 'password': 'Mnbvcxz123', 'alias': 'vega'},

    {'address': '172.18.100.33', 'username': 'SDC4', 'password': 'MZnbvcx123', 'alias': 'Mecury'},

    {'address': '172.18.100.90', 'username': 'SDC5', 'password': 'mnbvcxz123', 'alias': 'Galaxy'},

]

# Shared folder and local save directory
SHARED_FOLDER_NAME = 'ELimages'

# Centralized server folder path
centralized_folder = "D:\\ELimages\\Data_recieved"

# Archive base folder path
archive_base_folder = "D:\\ELimages\\Data_recieved\\archive"

# Shift duration in hours
shift_duration = 0.01

# Mapping of IP address to folder alias
ip_to_alias = {pc['address']: pc['alias'] for pc in PC_CREDENTIALS}

# File processing record
processed_files = set()

def is_network_path_accessible(path, max_retries=3, retry_delay=2):
    """Check if a network path is accessible with retries."""
    for attempt in range(max_retries):
        try:
            if os.path.exists(path):
                return True
            time.sleep(retry_delay)
        except Exception:
            time.sleep(retry_delay)
    return False

# Function to connect to a shared folder
def connect_to_shared_folder(address, username, password, max_retries=3, retry_delay=2):
    """Enhanced connection function with retry logic."""
    unc = f"\\\\{address}\\{SHARED_FOLDER_NAME}"
    for attempt in range(max_retries):
        try:
            win32net.NetUseAdd(None, 2, {
                'remote': unc,
                'password': password,
                'username': username,
                'asg_type': 0,
                'local': '',
            })
            print(f"Connected to {unc}")
            # Verify the connection by checking if the path exists
            if is_network_path_accessible(unc):
                return True
            else:
                print(f"Warning: Connected to {unc} but path is not accessible")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed to connect to {unc}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    return False

# Function to check if file exists in archive
def file_exists_in_archive(file_path):
    file_name = os.path.basename(file_path)
    for root, dirs, files in os.walk(archive_base_folder):
        if file_name in files:
            return True
    return False

# Function to get file hash
def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

# Event Handler Class
class JPEGFileHandler(FileSystemEventHandler):
    def __init__(self, alias):
        self.alias = alias

    def on_created(self, event):
        if not event.is_directory:
            source = event.src_path
            _, file_extension = os.path.splitext(source)
            if file_extension.lower() in ['.jpg', '.jpeg']:
                if source not in processed_files and not file_exists_in_archive(source):
                    print(f"New JPEG file detected: {source}")
                    destination_folder = os.path.join(centralized_folder, self.alias)
                    os.makedirs(destination_folder, exist_ok=True)
                    destination = os.path.join(destination_folder, os.path.basename(source))
                    shutil.copy2(source, destination)
                    processed_files.add(source)
                    print(f"JPEG file copied to centralized server: {destination}")

def process_existing_files():
    for pc in PC_CREDENTIALS:
        folder_to_watch = f"\\\\{pc['address']}\\{SHARED_FOLDER_NAME}"
        alias = ip_to_alias[pc['address']]
        source_folder = os.path.join(centralized_folder, alias)
        os.makedirs(source_folder, exist_ok=True)
        if os.path.exists(folder_to_watch):
            for file_name in os.listdir(folder_to_watch):
                file_path = os.path.join(folder_to_watch, file_name)
                if os.path.isfile(file_path) and file_name.lower().endswith(('.jpg', '.jpeg')):
                    if file_path not in processed_files and not file_exists_in_archive(file_path):
                        destination = os.path.join(source_folder, file_name)
                        shutil.copy2(file_path, destination)
                        processed_files.add(file_path)
                        print(f"Existing JPEG file copied to centralized server: {destination}")

def start_monitoring():
    observer = None
    running = True
    last_heartbeat = time.time()
    heartbeat_interval = 60  # Print a heartbeat every 60 seconds
    last_archive_check = time.time()
    archive_check_interval = 3600  # Check for archiving every hour

    # Handle Ctrl+C
    import signal
    def signal_handler(sig, frame):
        nonlocal running
        print("\nShutdown signal received. Stopping monitoring...")
        running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Process existing files before starting to monitor
        process_existing_files()

        # Initialize observer
        observer = Observer()
        active_observers = []

        for pc in PC_CREDENTIALS:
            if not running:
                break
                
            folder_to_watch = f"\\\\{pc['address']}\\{SHARED_FOLDER_NAME}"
            print(f"\nAttempting to monitor: {folder_to_watch}")
            
            # Try to connect to the shared folder
            if not connect_to_shared_folder(pc['address'], pc['username'], pc['password']):
                print(f"Failed to connect to {folder_to_watch}. Skipping...")
                continue
            
            # Verify the path is accessible before adding to observer
            if not is_network_path_accessible(folder_to_watch):
                print(f"Path {folder_to_watch} is not accessible. Skipping...")
                continue
            
            try:
                event_handler = JPEGFileHandler(pc['alias'])
                observer.schedule(event_handler, folder_to_watch, recursive=False)
                active_observers.append(folder_to_watch)
                print(f"Successfully started monitoring: {folder_to_watch}")
            except Exception as e:
                print(f"Error setting up observer for {folder_to_watch}: {e}")

        if not active_observers:
            print("No valid paths to monitor. Exiting.")
            return

        # Start the observer
        observer.start()
        print("\nMonitoring started on the following paths:")
        for path in active_observers:
            print(f"- {path}")
        print("\nPress Ctrl+C to stop monitoring...")

        # Main monitoring loop
        while running:
            try:
                current_time = time.time()
                
                # Print a heartbeat message periodically
                if current_time - last_heartbeat >= heartbeat_interval:
                    print(f"\n[Heartbeat] Monitoring active at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    last_heartbeat = current_time
                
                # Check if it's time to archive files
                if current_time - last_archive_check >= shift_duration * 3600:  # Convert hours to seconds
                    print(f"\nShift ended at {datetime.now()}. Archiving JPEG files...")
                    archive_files()
                    last_archive_check = current_time
                    print("Archiving completed.")
                
                # Check if any observers have died
                if not observer.is_alive():
                    print("\nObserver thread has died. Restarting monitoring...")
                    break
                    
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\nShutdown requested by user...")
                running = False
            except Exception as e:
                print(f"\nUnexpected error in monitoring loop: {e}")
                running = False

    except Exception as e:
        print(f"\nError in monitoring setup: {e}")
    finally:
        print("\nShutting down...")
        # Stop the observer if it was started
        if observer and observer.is_alive():
            print("Stopping observer...")
            observer.stop()
            observer.join(timeout=5)
            if observer.is_alive():
                print("Warning: Observer did not shut down cleanly")
        
        # Clean up any network connections
        for pc in PC_CREDENTIALS:
            try:
                unc = f"\\\\{pc['address']}\\{SHARED_FOLDER_NAME}"
                win32net.NetUseDel(unc, 0)
                print(f"Disconnected from {unc}")
            except Exception as e:
                print(f"Error disconnecting from {pc['address']}: {e}")
        
        print("Monitoring stopped.")

def archive_files():
    """Archive files from the centralized folder to the archive location."""
    current_time = datetime.now()
    print(f"Starting archiving process at {current_time}...")
    
    # Create the directory structure for archiving
    year = current_time.strftime('%Y')
    month = current_time.strftime('%m')
    day = current_time.strftime('%d')
    
    archived_count = 0
    
    # Process each alias folder
    for alias in ip_to_alias.values():
        source_folder = os.path.join(centralized_folder, alias)
        archive_path = os.path.join(archive_base_folder, year, month, day, alias)
        
        # Skip if source folder doesn't exist
        if not os.path.exists(source_folder):
            print(f"Source folder not found: {source_folder}")
            continue
            
        # Create archive directory if it doesn't exist
        os.makedirs(archive_path, exist_ok=True)
        
        # Move files to archive
        try:
            files_moved = 0
            for file_name in os.listdir(source_folder):
                source_file = os.path.join(source_folder, file_name)
                if os.path.isfile(source_file) and file_name.lower().endswith(('.jpg', '.jpeg')):
                    dest_file = os.path.join(archive_path, file_name)
                    shutil.move(source_file, dest_file)
                    files_moved += 1
                    print(f"Archived: {file_name} to {archive_path}")
            
            archived_count += files_moved
            if files_moved > 0:
                print(f"Moved {files_moved} files from {alias} to archive")
                
        except Exception as e:
            print(f"Error archiving files from {source_folder}: {e}")
    
    if archived_count == 0:
        print("No new files to archive.")
    else:
        print(f"Archiving completed. Total files archived: {archived_count}")

if __name__ == "__main__":
    # Create necessary local directories
    os.makedirs(centralized_folder, exist_ok=True)
    os.makedirs(archive_base_folder, exist_ok=True)
    
    # Start the monitoring
    start_monitoring()