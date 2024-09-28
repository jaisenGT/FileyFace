import os
import time
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import Requests

# Set source root folder path (default=Downloads)
SRC_ROOT = os.path.expanduser("~/Downloads")

USERNAME = os.environ.get('USER') or os.environ.get('USERNAME')

class FileHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        #self.processed_files = set()
        
    def on_created(self, event):
        # Ignore directory creation events
        if event.is_directory:
            return
        
        time.sleep(0.2)
        file_name = os.path.basename(event.src_path)
        print(f"Detected change: {file_name}")      # Temp debug statement
        
        # Logic to ignore temporary files
        if file_name.endswith(('.tmp', '.crdownload')):
            print(f"Ignoring temporary file: {file_name}")     # Temp debug statement        
            return
        else:
            print(f"Processing file: {file_name}")      # Temp debug statement
            #if file_name not in self.processed_files:
                #self.processed_files.add(file_name)
            self.organize_file(file_name)
            # else:
            #     print(f"'{file_name}' has already been processed.")     # Temp debug statement
                
    def organize_file(self, file_name):
        src_file_path = os.path.join(SRC_ROOT, file_name)
        
        # Check if the file still exists
        if not os.path.exists(src_file_path):
            print(f"Source file '{src_file_path}' does not exist. Skipping.")
            return
        
        dst_file_filepath = Requests.ask_for_file(src_file_path, USERNAME)
        dst_file_filepath = Path(str(dst_file_filepath))
        print(dst_file_filepath)
        
        # Creates destination if it doesn't exist
        os.makedirs(dst_file_filepath.parent, exist_ok=True)
        
        # Prompt the user for confirmation to move the file
        new_file_name = self.prompt_user(file_name, dst_file_filepath)
        if new_file_name:
            file_ext = os.path.splitext(file_name)[1]
            final_file_name = new_file_name + file_ext
            dst_file_filepath = dst_file_filepath.parent / final_file_name
            os.rename(src_file_path, dst_file_filepath)
            print(f"Moved '{file_name}' to '{dst_file_filepath.parent}' as '{final_file_name}'")
        

    def prompt_user(self, file_name, destination_folder):
        print(f"Prompting user to move '{file_name}' to '{destination_folder}'")  # Debug statement

        # Create a new top-level window for user input
        prompt_window = tk.Tk()
        prompt_window.title("FileyFace")
        prompt_window.attributes('-topmost', True)  # Make the window stay on top
        # prompt_window.geometry("400x200+500+500")  # Set the size of the window MAKE THIS BIGGER OR SMALLER ACCORDINGLY

        popup_width = 400
        popup_height = 200

        # get the screen dimension
        screen_width = prompt_window.winfo_screenwidth()
        screen_height = prompt_window.winfo_screenheight()

        # find the center point
        center_x = int(screen_width/2 - popup_width / 2)
        center_y = int(screen_height/2 - popup_height / 2)

        # set the position of the window to the center of the screen
        prompt_window.geometry(f'{popup_width}x{popup_height}+{center_x}+{center_y}')

        # Set a theme color
        prompt_window.configure(bg="#f0f0f0")  # Light gray background


        # Set the small window icon (this is for the title bar)
        small_icon = Image.open("FileyFaceLogo.png")
        small_icon = small_icon.resize((32, 32), Image.Resampling.LANCZOS)  # Use 32x32 for the title bar icon size
        small_icon_image = ImageTk.PhotoImage(small_icon)
        prompt_window.iconphoto(False, small_icon_image)  # Set the window icon

        tk.Label(prompt_window, text="Do you want to move:", bg="#f0f0f0", font=("Arial", 12)).pack(pady=10)

        # Get the original file name without extension
        base_file_name = os.path.splitext(file_name)[0]
        file_extension = os.path.splitext(file_name)[1]

        # Create a frame to hold the entry and label
        input_frame = tk.Frame(prompt_window, bg="#f0f0f0")
        input_frame.pack(pady=5)

        # Create the entry for the new file name
        new_file_name_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        new_file_name_entry.insert(0, base_file_name)  # Default to the base name
        new_file_name_entry.pack(side=tk.LEFT)  # Place it on the left side

        # Create the label for the file extension
        extension_label = tk.Label(input_frame, text=file_extension, bg="#f0f0f0", font=("Arial", 12))
        extension_label.pack(side=tk.LEFT)  # Place it on the right side

        # Update the label to show the correct prompt
        tk.Label(prompt_window, text=f"to '{destination_folder}'?", bg="#f0f0f0", font=("Arial", 12)).pack(pady=10)
        # tk.Label(prompt_window, text=f"Do you want to move '{new_file_name_entry.get()} {file_extension}' to '{destination_folder}'?", bg="#f0f0f0", font=("Arial", 12)).pack(pady=10)

        # Variable to store user choice
        user_choice = [None]  # Using a list to hold reference

        def on_yes():
            user_choice[0] = new_file_name_entry.get().strip()  # Get new file name
            prompt_window.destroy()  # Close the prompt window

        def on_no():
            user_choice[0] = None  # Indicate to keep the file in Downloads
            prompt_window.destroy()  # Close the prompt window

        button_frame = tk.Frame(prompt_window, bg="#f0f0f0")  # Frame for buttons
        button_frame.pack(pady=20)

        yes_button = tk.Button(button_frame, text="Yes", command=on_yes, font=("Arial", 12), bg="#4CAF50", fg="white")
        yes_button.pack(side=tk.LEFT, padx=10)

        no_button = tk.Button(button_frame, text="No", command=on_no, font=("Arial", 12), bg="#f44336", fg="white")
        no_button.pack(side=tk.RIGHT, padx=10)

        prompt_window.protocol("WM_DELETE_WINDOW", prompt_window.destroy)  # Handle window close
        prompt_window.mainloop()  # Start the event loop

        return user_choice[0]  # Return the user's choice

def start_monitoring():
    observer = Observer()
    event_handler = FileHandler()
    observer.schedule(event_handler, SRC_ROOT, recursive=False)
    observer.start()
    print(f"Monitoring folder: {SRC_ROOT}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_monitoring()
    