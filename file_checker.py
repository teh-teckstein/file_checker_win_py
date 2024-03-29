import os
import psutil
from collections import defaultdict
import matplotlib.pyplot as plt
import smtplib
from email.message import EmailMessage

class DiskAnalyzer:
    def __init__(self, drive):
        self.drive = drive

    def get_disk_space_info(self):
        disk_usage = psutil.disk_usage(self.drive)._asdict()
        return {
            'total_space': disk_usage['total'],
            'used_space': disk_usage['used'],
            'unused_space': disk_usage['free'],
        }

    def get_directory_sizes(self, base_directory):
        return DirectorySizeCalculator.calculate(base_directory)

    def calculate_file_extensions(self, directory):
        return FileExtensionCalculator.calculate(directory)

    def plot_pie_chart(self, labels, sizes, title, filename):
        PieChartPlotter.plot(labels, sizes, title, filename)

    def send_email_with_attachments(self, recipient_email, attachment_paths):
        EmailSender.send(recipient_email, attachment_paths)

    def display_directory_sizes_and_disk_space(self, num_files=10, num_directories=5, recipient_email=None):
        space_info = self.get_disk_space_info()

        print(f"\n[+] Total space on {self.drive}: {space_info['total_space']}")
        print(f"[+] Used space on {self.drive}: {space_info['used_space']}")
        print(f"[+] Unused space on {self.drive}: {space_info['unused_space']}")

        print("\n[+] Top Directories:")
        directory_sizes = self.get_directory_sizes(self.drive)

        total_directory_space = sum(entry['size_in_bytes'] for entry in directory_sizes)
        for i, entry in enumerate(directory_sizes[:num_directories], start=1):
            percentage = (entry['size_in_bytes'] / total_directory_space) * 100
            print(f"{i}. {entry['path']}: Size - {entry['size']} ({percentage:.2f}%)")

        self.plot_pie_chart(
            labels=[entry['path'] for entry in directory_sizes[:num_directories]],
            sizes=[entry['size_in_bytes'] for entry in directory_sizes[:num_directories]],
            title='Top Directories',
            filename='top_directories.png'
        )

        selected_directory = input(f"\nEnter the number of the directory to explore (1-{num_directories}) or 'exit' to quit: ")
        if selected_directory.lower() == 'exit':
            return

        selected_directory = directory_sizes[int(selected_directory) - 1]['path']
        self.display_directory_info(selected_directory, num_files)

        if recipient_email:
            attachment_paths = ['top_directories.png', 'top_files.png']
            self.send_email_with_attachments(recipient_email, attachment_paths)

    def display_directory_info(self, directory, num_files=10):
        print(f"\n[+] Selected Directory: {directory}")

        files_in_selected_directory = self.calculate_file_extensions(directory)
        sorted_files = sorted(files_in_selected_directory.items(), key=lambda x: x[1], reverse=True)[:num_files]

        if sorted_files:
            print("\n[+] Top Files:")
            total_file_space = sum(size for ext, size in sorted_files)
            for ext, size in sorted_files:
                percentage = (size / total_file_space) * 100
                print(f"    {ext}: Size - {size} bytes ({percentage:.2f}%)")

        self.plot_pie_chart(
            labels=[ext for ext, _ in sorted_files],
            sizes=[size for _, size in sorted_files],
            title='Top Files',
            filename='top_files.png'
        )

class DirectorySizeCalculator:
    @staticmethod
    def calculate(base_directory):
        directory_sizes = []
        for entry in os.scandir(base_directory):
            if entry.is_dir():
                directory_path = entry.path
                directory_size = DirectorySizeCalculator.get_directory_size(directory_path)
                formatted_size = DiskAnalyzer.get_size_format(directory_size)

                directory_sizes.append({
                    'path': directory_path,
                    'size': formatted_size,
                    'size_in_bytes': directory_size,
                })

        directory_sizes = sorted(directory_sizes, key=lambda x: x['size_in_bytes'], reverse=True)
        return directory_sizes

    @staticmethod
    def get_directory_size(directory):
        total = 0
        try:
            for entry in os.scandir(directory):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += DirectorySizeCalculator.get_directory_size(entry.path)
        except (NotADirectoryError, PermissionError):
            return os.path.getsize(directory)
        return total

class FileExtensionCalculator:
    @staticmethod
    def calculate(directory):
        file_extensions = defaultdict(int)
        try:
            for entry in os.scandir(directory):
                if entry.is_file():
                    _, ext = os.path.splitext(entry.name)
                    file_extensions[ext] += entry.stat().st_size
                elif entry.is_dir():
                    subdirectory_extensions = FileExtensionCalculator.calculate(entry.path)
                    for ext, size in subdirectory_extensions.items():
                        file_extensions[ext] += size
        except (NotADirectoryError, PermissionError):
            pass
        return file_extensions

class PieChartPlotter:
    @staticmethod
    def plot(labels, sizes, title, filename):
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title(title)
        plt.savefig(filename)
        plt.close()

class EmailSender:
    @staticmethod
    def send(recipient_email, attachment_paths):
        sender_email = "your_email@example.com"  # Update with your email address
        password = "your_password"  # Update with your email password

        msg = EmailMessage()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = 'Disk Analysis Report'

        for attachment_path in attachment_paths:
            with open(attachment_path, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(attachment_path)
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, password)
            smtp.send_message(msg)

# Main program
if __name__ == "__main__":
    drive = input("Enter the drive to scan (default, C:/): ").upper() or "C:/"
    recipient_email = input("Enter recipient's email address to share the analysis (leave blank to skip): ")
    
    analyzer = DiskAnalyzer(drive)
    analyzer.display_directory_sizes_and_disk_space(recipient_email=recipient_email)