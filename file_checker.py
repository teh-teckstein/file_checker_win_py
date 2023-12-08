
def display_directory_sizes_and_disk_space(drive, num_files=5, num_directories=5):
    # Displays disk space information, top files, and top directories.
    while True:
        space_info = get_disk_space_info(drive)

        print(f"\n[+] Total space on {drive}: {space_info['total_space']}")
        print(f"[+] Used space on {drive}: {space_info['used_space']}")
        print(f"[+] Unused space on {drive}: {space_info['unused_space']}")

        print("\n[+] Top Directories:")
        directory_sizes = get_directory_sizes(drive)

        total_directory_space = sum(entry['size_in_bytes'] for entry in directory_sizes)
        for i, entry in enumerate(directory_sizes[:num_directories], start=1):
            percentage = (entry['size_in_bytes'] / total_directory_space) * 100
            print(f"{i}. {entry['path']}: Size - {entry['size']} ({percentage:.2f}%)")

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
                total_file_space = sum(size for ext, size in sorted_files)
                for ext, size in sorted_files:
                    percentage = (size / total_file_space) * 100
                    formatted_size = get_size_format(size)
                    print(f"    {ext}: Size - {formatted_size} ({percentage:.2f}%)")

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