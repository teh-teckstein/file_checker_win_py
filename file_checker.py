import os
import psutil
from collections import defaultdict

def get_size_format(b, factor=1024, suffix="B"):
#    Scale bytes to its proper byte format
 
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

def get_disk_space_info(drive):
    #returns used and unused space on the specified drive
    disk_usage = psutil.disk_usage(drive)._asdict()
    
    return {
        'total_space': get_size_format(disk_usage['total']),
        'used_space': get_size_format(disk_usage['used']),
        'unused_space': get_size_format(disk_usage['free']),
    }

def get_directory_size(directory):
    #Returns the `directory` size in bytes
    total = 0
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    except (NotADirectoryError, PermissionError):
        return os.path.getsize(directory)
        print(f"[!] Error accessing or calculating size for directory: {directory}")
    return total

def get_directory_sizes(base_directory):
    #Returns a list of directories and their sizes
    directory_sizes = []

    for entry in os.scandir(base_directory):
        if entry.is_dir():
            directory_path = entry.path
            directory_size = get_directory_size(directory_path)
            formatted_size = get_size_format(directory_size)

            directory_sizes.append({
                'path': directory_path,
                'size': formatted_size,
                'size_in_bytes': directory_size,  # New: Include the size in bytes for sorting
            })

    # Sort directories by size in bytes
    directory_sizes = sorted(directory_sizes, key=lambda x: x['size_in_bytes'], reverse=True)

    return directory_sizes
    
def calculate_file_extensions(directory):
    # Calculate the space taken by file extensions in the given directory
    file_extensions = defaultdict(int)

    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                _, ext = os.path.splitext(entry.name)
                file_extensions[ext] += entry.stat().st_size
            elif entry.is_dir():
                subdirectory_extensions = calculate_file_extensions(entry.path)
                for ext, size in subdirectory_extensions.items():
                    file_extensions[ext] += size
    except (NotADirectoryError, PermissionError):
        pass

    return file_extensions

def display_directory_sizes_and_disk_space(drive, num_files=5, num_directories=5):
    # Displays disk space information, top files, and top directories.
    while True:
        space_info = get_disk_space_info(drive)

        print(f"\n[+] Total space on {drive}: {space_info['total_space']}")
        print(f"[+] Used space on {drive}: {space_info['used_space']}")
        print(f"[+] Unused space on {drive}: {space_info['unused_space']}")

        print("\n[+] Top Directories:")
        directory_sizes = get_directory_sizes(drive)

        for i, entry in enumerate(directory_sizes[:num_directories], start=1):
            print(f"{i}. {entry['path']}: Size - {entry['size']}")

        selected_directory = select_directory(directory_sizes)
        if selected_directory is None:
            break

        while True:
            space_info = get_disk_space_info(drive)

            print(f"\n[+] Total space on {drive}: {space_info['total_space']}")
            print(f"[+] Used space on {drive}: {space_info['used_space']}")
            print(f"[+] Unused space on {drive}: {space_info['unused_space']}")

            print("\n[+] Selected Directory:")
            print(f"{selected_directory}")

            # Calculate and display top files
            files_in_selected_directory = calculate_file_extensions(selected_directory)
            sorted_files = sorted(files_in_selected_directory.items(), key=lambda x: x[1], reverse=True)[:num_files]

            if sorted_files:
                print("\n[+] Top Files:")
                for ext, size in sorted_files:
                    formatted_size = get_size_format(size)
                    print(f"    {ext}: Size - {formatted_size}")

            print("\n[+] Subdirectories:")
            subdirectory_sizes = get_directory_sizes(selected_directory)

            sub_selected_directory = select_directory(subdirectory_sizes)
            if sub_selected_directory is None:
                break
            else:
                selected_directory = sub_selected_directory
                
def select_directory(directory_sizes):
    #Prompt the user to select a directory.
    while True:
        try:
            print("\n[+] Directories:")
            for i, entry in enumerate(directory_sizes, start=1):
                print(f"{i}. {entry['path']}: Size - {entry['size']}")

            user_input = input(f"Enter the number of the directory to scan (or 'exit' to return to {drive}): ")
            if user_input.lower() == 'exit':
                return None
            elif user_input.isdigit():
                index = int(user_input)
                if 1 <= index <= len(directory_sizes):
                    return directory_sizes[index - 1]['path']
                else:
                    print("Invalid directory number. Please enter a valid number.")
            else:
                print("Invalid input. Please enter a valid number.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    drive = input("Enter the drive to scan (default, C:/):").upper() or "C:/"
    display_directory_sizes_and_disk_space(drive)