import os
import zipfile
import customtkinter as ctk
from tkinter import filedialog
import time
import shutil
import sys
import threading

class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, master, text):
        super().__init__(master)
        self.geometry("300x150")
        self.title("Confirm")
        self.result = False

        label = ctk.CTkLabel(self, text=text)
        label.pack(pady=20)

        yes_button = ctk.CTkButton(self, text="Yes", command=self.yes_clicked)
        yes_button.pack(side="left", padx=20)

        no_button = ctk.CTkButton(self, text="No", command=self.no_clicked)
        no_button.pack(side="right", padx=20)

        self.wait_window()

    def yes_clicked(self):
        self.result = True
        self.destroy()

    def no_clicked(self):
        self.result = False
        self.destroy()

class ConsoleNotification(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.geometry("400x100")
        self.title("Extraction in Progress")
        
        label = ctk.CTkLabel(self, text="Check the program console for extraction details.")
        label.pack(pady=20)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        self.destroy()

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.0f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    else:
        return f"{seconds/3600:.1f} hours"

def print_progress(progress, speed, eta, current_file):
    os.system('cls')
    bar_length = 30
    filled_length = int(bar_length * progress)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    percent = progress * 100
    
    print("Extraction progress:")
    print(f"[{bar}] {percent:.1f}%")
    print(f"Speed: {speed}/s")
    print(f"ETA: {eta}")
    print(f"Current file: {current_file}")

def extract_with_progress(zip_file, extract_path):
    with zipfile.ZipFile(zip_file, 'r') as zf:
        total_size = sum(file.file_size for file in zf.infolist())
        extracted_size = 0
        start_time = time.time()

        for file in zf.infolist():
            zf.extract(file, extract_path)
            extracted_size += file.file_size
            elapsed_time = time.time() - start_time
            speed = extracted_size / elapsed_time if elapsed_time > 0 else 0
            eta = (total_size - extracted_size) / speed if speed > 0 else 0
            progress = extracted_size / total_size

            print_progress(
                progress,
                format_size(speed),
                format_time(eta),
                os.path.basename(file.filename)
            )

    os.system('cls')
    print("Extraction completed.")

def extract_and_organize(zip_file=None):
    if zip_file is None:
        zip_file = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip")])
        if not zip_file:
            return

    if not os.path.exists(zip_file):
        print(f"Error: The file '{zip_file}' does not exist.")
        return

    dest_folder = filedialog.askdirectory()
    if not dest_folder:
        return

    zip_name = os.path.splitext(os.path.basename(zip_file))[0]
    extract_path = os.path.join(dest_folder, zip_name)
    os.makedirs(extract_path, exist_ok=True)

    root = ctk.CTk()
    root.withdraw()

    notification = ConsoleNotification(root)
    
    print("Starting extraction...")
    extraction_thread = threading.Thread(target=extract_with_progress, args=(zip_file, extract_path), daemon=True)
    extraction_thread.start()
    
    while extraction_thread.is_alive():
        root.update()
        time.sleep(0.1)
    
    notification.destroy()

    contents = os.listdir(extract_path)
    if len(contents) == 1 and os.path.isdir(os.path.join(extract_path, contents[0])):
        single_folder = os.path.join(extract_path, contents[0])
        shutil.move(single_folder, dest_folder)
        os.rmdir(extract_path)
        print(f"Moved single folder '{contents[0]}' to '{dest_folder}'")

    dialog = ConfirmDialog(root, "Do you want to delete the original zip file?")
    if dialog.result:
        os.remove(zip_file)
        print("Original zip file deleted.")
    else:
        print("Original zip file kept.")

    root.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    if len(sys.argv) > 1:
        zip_file = sys.argv[1]
        extract_and_organize(zip_file)
    else:
        extract_and_organize()