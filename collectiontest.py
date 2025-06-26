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
    }
]

# Shared folder name
SHARED_FOLDER_NAME = 'ELimagesnew'

# Centralized server folder path (where processed images will be stored)
centralized_folder = "D:\\ELimagesnew\\Data_processed"

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
                        print(f"[{self.alias}] New JPEG file detected: {source}")
                        self.process_single_file(source)

    def on_modified(self, event):
        if not event.is_directory:
            source = event.src_path
            _, file_extension = os.path.splitext(source)
            if file_extension.lower() in ['.jpg', '.jpeg']:
                with processed_files_lock:
                    if source not in processed_files:
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

def start_monitoring():
    """Start monitoring all production line shared folders."""
    observers = []
    running = True
    last_heartbeat = time.time()
    heartbeat_interval = 60  # Print a heartbeat every 60 seconds
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
        print("\nPress Ctrl+C to stop monitoring...")

        # Main monitoring loop
        while running:
            try:
                current_time = time.time()
                
                # Print a heartbeat message periodically
                if current_time - last_heartbeat >= heartbeat_interval:
                    active_lines = [line['alias'] for _, line in observers if _.is_alive()]
                    print(f"\n[Heartbeat] Monitoring active at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Active lines: {', '.join(active_lines)}")
                    last_heartbeat = current_time
                
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
    
    print("=" * 70)
    print("MULTI PRODUCTION LINE MONITOR")
    print("=" * 70)
    print("Production Lines:")
    for line in PRODUCTION_LINES:
        print(f"- {line['alias']}: {line['address']} (Suffix: {line['suffix']})")
    print(f"Shared Folder: {SHARED_FOLDER_NAME}")
    print(f"Output Directory: {centralized_folder}")
    print("=" * 70)
    
    # Start the monitoring
    start_monitoring()