import json
import os
import time
import shutil
import win32net
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
import hashlib
import re
import threading

# Production line credentials
PRODUCTION_LINES = [
    {
        'address': '172.18.100.90', 
        'username': 'SDC5', 
        'password': 'mnbvcxz123', 
        'alias': 'Galaxy',
        'suffix': 'GAL'
    },
    {
        'address': '172.18.100.116', 
        'username': 'SDC3', 
        'password': 'Zxcvbnm123', 
        'alias': 'Jigani',
        'suffix': 'JIG'
    },
    {
        'address': '172.18.7.74', 
        'username': 'SDC2', 
        'password': 'Mnbvcxz123', 
        'alias': 'vega',
        'suffix': 'VEGA'
    },
    {
        'address': '172.18.100.214', 
        'username': 'SDC5', 
        'password': 'poiuytrewq123', 
        'alias': 'Mecury',
        'suffix': 'MERC'
    }
]

# Shared folder name
SHARED_FOLDER_NAME = 'ELimagesnew'

# Centralized server folder path (where processed images will be stored)
centralized_folder = "D:\\ELimagesnew\\Data_processed_new"

# Archive base folder path
archive_base_folder = "D:\\ELimagesnew\\Data_processed_new\\archive"

# Shift duration in hours (configurable)
shift_duration = 0.01  # 5 seconds for testing purposes

# File processing record (shared across all production lines)
processed_files = set()
processed_files_lock = threading.Lock()

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

def file_exists_in_archive(file_name, alias):
    """Check if a file with the same name exists in the archive for a specific alias."""
    alias_archive_path = os.path.join(archive_base_folder, alias)
    if not os.path.exists(alias_archive_path):
        return False
    
    for root, dirs, files in os.walk(alias_archive_path):
        if file_name in files:
            return True
    return False

def get_file_hash(file_path):
    """Get MD5 hash of a file."""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error getting hash for {file_path}: {e}")
        return None

def get_quality_suffix(file_path):
    """Determine quality suffix based on folder structure."""
    # Check if the file path contains 'NG' or 'Normal' folders
    path_parts = file_path.replace('\\', '/').split('/')
    
    for part in path_parts:
        if 'NG' in part.upper():
            return 'Z'
        elif 'NORMAL' in part.upper():
            return 'A'
    
    # Default to 'A' if neither NG nor Normal is found
    return 'A'

def generate_new_filename(original_filename, source_path, production_suffix):
    """Generate new filename with the required format."""
    # Extract original filename without extension
    name_without_ext = os.path.splitext(original_filename)[0]
    extension = os.path.splitext(original_filename)[1]
    
    # Get quality suffix based on path
    quality_suffix = get_quality_suffix(source_path)
    
    # Get current timestamp (YY format for year)
    timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
    
    # Generate new filename: ORIGINALNAME_PRODUCTION_QUALITY_TIMESTAMP
    new_filename = f"{name_without_ext}_{production_suffix}_{quality_suffix}_{timestamp}{extension}"
    
    return new_filename

def replicate_folder_structure(source_root, dest_root, production_suffix, alias):
    """Replicate folder structure and process files."""
    if not os.path.exists(source_root):
        print(f"Source folder does not exist: {source_root}")
        return
    
    processed_count = 0
    
    # Walk through all directories and files in source
    for root, dirs, files in os.walk(source_root):
        # Calculate relative path from source root
        rel_path = os.path.relpath(root, source_root)
        
        # Create corresponding directory in destination with alias first
        if rel_path == '.':
            dest_dir = os.path.join(dest_root, alias)
        else:
            dest_dir = os.path.join(dest_root, alias, rel_path)
        
        os.makedirs(dest_dir, exist_ok=True)
        
        # Process each file
        for file_name in files:
            source_file = os.path.join(root, file_name)
            
            # Only process JPEG files
            if file_name.lower().endswith(('.jpg', '.jpeg')):
                # Skip if already processed (thread-safe)
                with processed_files_lock:
                    if source_file in processed_files:
                        continue
                
                # Check if file already exists in archive
                if file_exists_in_archive(file_name, alias):
                    print(f"[{alias}] File {file_name} already exists in archive. Skipping...")
                    with processed_files_lock:
                        processed_files.add(source_file)
                    continue
                
                # Generate new filename
                new_filename = generate_new_filename(file_name, source_file, production_suffix)
                dest_file = os.path.join(dest_dir, new_filename)
                
                try:
                    # Copy file with new name
                    shutil.copy2(source_file, dest_file)
                    with processed_files_lock:
                        processed_files.add(source_file)
                    processed_count += 1
                    
                    print(f"[{alias}] Processed: {file_name} -> {new_filename}")
                    print(f"  Source: {source_file}")
                    print(f"  Destination: {dest_file}")
                    print(f"  Quality: {'NG' if get_quality_suffix(source_file) == 'Z' else 'Normal'}")
                    print("-" * 50)
                    
                except Exception as e:
                    print(f"[{alias}] Error copying {source_file} to {dest_file}: {e}")
    
    if processed_count > 0:
        print(f"[{alias}] Total files processed: {processed_count}")
    else:
        print(f"[{alias}] No new files to process.")

# Event Handler Class
class ProductionLineFileHandler(FileSystemEventHandler):
    def __init__(self, production_line):
        self.production_line = production_line
        self.production_suffix = production_line['suffix']
        self.alias = production_line['alias']

    def on_created(self, event):
        if not event.is_directory:
            source = event.src_path
            _, file_extension = os.path.splitext(source)
            if file_extension.lower() in ['.jpg', '.jpeg']:
                with processed_files_lock:
                    if source not in processed_files:
                        original_filename = os.path.basename(source)
                        if not file_exists_in_archive(original_filename, self.alias):
                            print(f"[{self.alias}] New JPEG file detected: {source}")
                            self.process_single_file(source)

    def on_modified(self, event):
        if not event.is_directory:
            source = event.src_path
            _, file_extension = os.path.splitext(source)
            if file_extension.lower() in ['.jpg', '.jpeg']:
                with processed_files_lock:
                    if source not in processed_files:
                        original_filename = os.path.basename(source)
                        if not file_exists_in_archive(original_filename, self.alias):
                            print(f"[{self.alias}] Modified JPEG file detected: {source}")
                            self.process_single_file(source)

    def process_single_file(self, source_file):
        """Process a single file that was detected by the file watcher."""
        try:
            # Get relative path from the shared folder root
            shared_folder_root = f"\\\\{self.production_line['address']}\\{SHARED_FOLDER_NAME}"
            rel_path = os.path.relpath(os.path.dirname(source_file), shared_folder_root)
            
            # Create destination directory with alias first
            if rel_path == '.':
                dest_dir = os.path.join(centralized_folder, self.alias)
            else:
                dest_dir = os.path.join(centralized_folder, self.alias, rel_path)
            
            os.makedirs(dest_dir, exist_ok=True)
            
            # Generate new filename
            original_filename = os.path.basename(source_file)
            new_filename = generate_new_filename(original_filename, source_file, self.production_suffix)
            dest_file = os.path.join(dest_dir, new_filename)
            
            # Copy file with new name
            shutil.copy2(source_file, dest_file)
            with processed_files_lock:
                processed_files.add(source_file)
            
            print(f"[{self.alias}] Processed: {original_filename} -> {new_filename}")
            print(f"  Source: {source_file}")
            print(f"  Destination: {dest_file}")
            print(f"  Quality: {'NG' if get_quality_suffix(source_file) == 'Z' else 'Normal'}")
            print("-" * 50)
            
        except Exception as e:
            print(f"[{self.alias}] Error processing {source_file}: {e}")

def process_existing_files():
    """Process all existing files in all production line shared folders."""
    print("Processing existing files from all production lines...")
    
    for line in PRODUCTION_LINES:
        print(f"\n[{line['alias']}] Processing existing files...")
        shared_folder_path = f"\\\\{line['address']}\\{SHARED_FOLDER_NAME}"
        
        if not os.path.exists(shared_folder_path):
            print(f"[{line['alias']}] Shared folder not accessible: {shared_folder_path}")
            continue
        
        replicate_folder_structure(shared_folder_path, centralized_folder, line['suffix'], line['alias'])

def archive_files():
    """Archive files from the centralized folder to the archive location."""
    current_time = datetime.now()
    print(f"\n{'='*60}")
    print(f"STARTING ARCHIVAL PROCESS AT {current_time}")
    print(f"{'='*60}")
    
    # Create the directory structure for archiving
    # year = current_time.strftime('%Y')
    # month = current_time.strftime('%m')
    # day = current_time.strftime('%d')
    
    archived_count = 0
    total_files = 0
    
    # Process each production line alias folder
    for line in PRODUCTION_LINES:
        alias = line['alias']
        source_folder = os.path.join(centralized_folder, alias)
        
        # Create archive path structure: archive/YYYY/MM/DD/alias
        archive_path = os.path.join(archive_base_folder, alias)
        
        # Skip if source folder doesn't exist
        if not os.path.exists(source_folder):
            print(f"[{alias}] Source folder not found: {source_folder}")
            continue
        
        # Count files in source folder
        files_in_source = []
        for root, dirs, files in os.walk(source_folder):
            for file_name in files:
                if file_name.lower().endswith(('.jpg', '.jpeg')):
                    files_in_source.append(os.path.join(root, file_name))
        
        if not files_in_source:
            print(f"[{alias}] No JPEG files found to archive")
            continue
        
        total_files += len(files_in_source)
        
        # Create archive directory if it doesn't exist
        os.makedirs(archive_path, exist_ok=True)
        
        # Move files to archive, preserving folder structure
        try:
            files_moved = 0
            for source_file in files_in_source:
                # Get relative path from source folder
                rel_path = os.path.relpath(source_file, source_folder)
                dest_file = os.path.join(archive_path, rel_path)
                
                # Create destination directory if needed
                dest_dir = os.path.dirname(dest_file)
                os.makedirs(dest_dir, exist_ok=True)
                
                # Move file to archive
                shutil.move(source_file, dest_file)
                files_moved += 1
                print(f"[{alias}] Archived: {os.path.basename(source_file)} -> {archive_path}")
            
            archived_count += files_moved
            print(f"[{alias}] Successfully archived {files_moved} files")
                
        except Exception as e:
            print(f"[{alias}] Error archiving files from {source_folder}: {e}")
    
    print(f"\n{'='*60}")
    if archived_count == 0:
        print("ARCHIVAL COMPLETED - No new files to archive")
    else:
        print(f"ARCHIVAL COMPLETED - {archived_count}/{total_files} files archived successfully")
    print(f"Archive location: {archive_base_folder}")
    print(f"{'='*60}\n")

def start_monitoring():
    """Start monitoring all production line shared folders."""
    observers = []
    running = True
    last_heartbeat = time.time()
    heartbeat_interval = 60  # Print a heartbeat every 60 seconds
    last_archive_check = time.time()
    archive_check_interval = shift_duration * 3600  # Convert hours to seconds
    connected_lines = []

    # Handle Ctrl+C
    import signal
    def signal_handler(sig, frame):
        nonlocal running
        print("\nShutdown signal received. Stopping monitoring...")
        running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Connect to all production line shared folders
        for line in PRODUCTION_LINES:
            folder_to_watch = f"\\\\{line['address']}\\{SHARED_FOLDER_NAME}"
            print(f"\n[{line['alias']}] Attempting to connect: {folder_to_watch}")
            
            if not connect_to_shared_folder(line['address'], line['username'], line['password']):
                print(f"[{line['alias']}] Failed to connect to {folder_to_watch}. Skipping...")
                continue
            
            # Verify the path is accessible
            if not is_network_path_accessible(folder_to_watch):
                print(f"[{line['alias']}] Path {folder_to_watch} is not accessible. Skipping...")
                continue
            
            connected_lines.append(line)
            print(f"[{line['alias']}] Successfully connected to {folder_to_watch}")
        
        if not connected_lines:
            print("No production lines could be connected. Exiting...")
            return
        
        # Process existing files before starting to monitor
        process_existing_files()

        # Initialize observers for each connected production line
        for line in connected_lines:
            folder_to_watch = f"\\\\{line['address']}\\{SHARED_FOLDER_NAME}"
            
            try:
                observer = Observer()
                event_handler = ProductionLineFileHandler(line)
                observer.schedule(event_handler, folder_to_watch, recursive=True)
                observers.append((observer, line))
                print(f"[{line['alias']}] Successfully set up monitoring for: {folder_to_watch}")
            except Exception as e:
                print(f"[{line['alias']}] Error setting up observer for {folder_to_watch}: {e}")

        if not observers:
            print("No observers could be set up. Exiting...")
            return

        # Start all observers
        for observer, line in observers:
            observer.start()
            print(f"[{line['alias']}] Started monitoring")

        print(f"\nMonitoring started for {len(observers)} production lines:")
        for _, line in observers:
            print(f"- {line['alias']} ({line['address']}) - Suffix: {line['suffix']}")
        print(f"Output directory: {centralized_folder}")
        print(f"Archive directory: {archive_base_folder}")
        print(f"Shift duration: {shift_duration} hours")
        print("\nPress Ctrl+C to stop monitoring...")

        # Main monitoring loop
        while running:
            try:
                current_time = time.time()
                
                # Debug: Show archive timing every 10 seconds
                if int(current_time) % 10 == 0:
                    time_until_archive = int((last_archive_check + archive_check_interval) - current_time)
                    if time_until_archive <= 0:
                        print(f"[DEBUG] Archive should trigger NOW! ({time_until_archive} seconds)")
                    else:
                        print(f"[DEBUG] Archive in {time_until_archive} seconds")
                
                # Print a heartbeat message periodically
                if current_time - last_heartbeat >= heartbeat_interval:
                    active_lines = [line['alias'] for _, line in observers if _.is_alive()]
                    next_archive = datetime.fromtimestamp(last_archive_check + archive_check_interval)
                    time_until_archive = int((last_archive_check + archive_check_interval) - current_time)
                    print(f"\n[Heartbeat] Monitoring active at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Active lines: {', '.join(active_lines)}")
                    print(f"Next archive check: {next_archive.strftime('%Y-%m-%d %H:%M:%S')} (in {time_until_archive} seconds)")
                    
                    # Show current file counts in each folder
                    for line in PRODUCTION_LINES:
                        alias_folder = os.path.join(centralized_folder, line['alias'])
                        if os.path.exists(alias_folder):
                            file_count = 0
                            for root, dirs, files in os.walk(alias_folder):
                                file_count += len([f for f in files if f.lower().endswith(('.jpg', '.jpeg'))])
                            print(f"  {line['alias']}: {file_count} JPEG files pending archive")
                    
                    last_heartbeat = current_time
                
                # Check if it's time to archive files
                if current_time - last_archive_check >= archive_check_interval:
                    print(f"\n*** ARCHIVE TRIGGER *** Shift ended at {datetime.now()}. Starting archival process...")
                    print(f"Time since last archive: {(current_time - last_archive_check):.2f} seconds")
                    print(f"Archive interval: {archive_check_interval} seconds")
                    archive_files()
                    last_archive_check = current_time
                    print("*** ARCHIVE COMPLETED ***")
                
                # Check if any observers have died
                dead_observers = [(obs, line) for obs, line in observers if not obs.is_alive()]
                if dead_observers:
                    for obs, line in dead_observers:
                        print(f"\n[{line['alias']}] Observer thread has died.")
                    print("Some observers have died. Consider restarting the application.")
                    
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
        # Stop all observers
        for observer, line in observers:
            if observer.is_alive():
                print(f"[{line['alias']}] Stopping observer...")
                observer.stop()
                observer.join(timeout=5)
                if observer.is_alive():
                    print(f"[{line['alias']}] Warning: Observer did not shut down cleanly")
        
        # Clean up network connections
        for line in PRODUCTION_LINES:
            try:
                unc = f"\\\\{line['address']}\\{SHARED_FOLDER_NAME}"
                win32net.NetUseDel(unc, 0)
                print(f"[{line['alias']}] Disconnected from {unc}")
            except Exception as e:
                print(f"[{line['alias']}] Error disconnecting: {e}")
        
        print("Monitoring stopped.")

if __name__ == "__main__":
    # Create necessary local directories
    os.makedirs(centralized_folder, exist_ok=True)
    os.makedirs(archive_base_folder, exist_ok=True)
    
    print("=" * 70)
    print("MULTI PRODUCTION LINE MONITOR WITH ARCHIVAL")
    print("=" * 70)
    print("Production Lines:")
    for line in PRODUCTION_LINES:
        print(f"- {line['alias']}: {line['address']} (Suffix: {line['suffix']})")
    print(f"Shared Folder: {SHARED_FOLDER_NAME}")
    print(f"Output Directory: {centralized_folder}")
    print(f"Archive Directory: {archive_base_folder}")
    print(f"Shift Duration: {shift_duration} hours")
    print("=" * 70)
    
    # Start the monitoring
    start_monitoring()