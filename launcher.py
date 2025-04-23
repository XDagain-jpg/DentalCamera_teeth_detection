import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import os
import sys


class TeethApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Teeth Detection Launcher")
        self.root.geometry("700x450")
        self.root.resizable(False, False)
        self.root.configure(bg = "#FFFFCC")

        self.isTest = tk.BooleanVar()
        self.test_check = ttk.Checkbutton(root, text="Enable Test Mode", variable=self.isTest, style="TestCheck.TCheckbutton")
        self.test_check.pack(pady=5)

        # Progress bar
        # self.progress = ttk.Progressbar(root, mode='indeterminate', length=400)
        # self.progress.pack(pady=5)
        # self.progress.stop()
        # self.progress.pack_forget()

        # Style setup
        style = ttk.Style() 

        #Toggle
        style.configure("TestCheck.TCheckbutton",
                background="#ffffff",
                foreground="#5acdaa",
                font=("Segoe UI", 8))
        
        # Button
        style.configure("TButton", foreground = "#5acdaa", background = "#5acdaa", font = ("Segoe UI", 11), padding = 6)
        style.map("TButton",
                  background=[("active", "#3ea590")],
                  foreground=[("active", "white")]
                  )
        
        # Header
        style.configure("Header.TLabel", font = ("Segoe UI", 18, "bold"), foreground = "#ae7ee4")
        style.configure("Log.TLabel", font = ("Consolas", 12))

        #Drop down menu style
        style.configure("CustomCombobox.TCombobox",
        foreground="#5ACDAA",     
        fieldbackground="#ae7ee4", # ?
        background="#ae7ee4",      # ?
        font=("Segoe UI", 10)
        )

        # Title
        self.title_label = ttk.Label(root, text = "Teeth Cleaning Robot Launcher", style = "Header.TLabel")
        self.title_label.pack(pady = 10)

        # frame
        # btn_frame = ttk.Frame(root)
        style.configure("Custom.TFrame", background="#ffffcc")
        btn_frame = ttk.Frame(root, style="Custom.TFrame")
        btn_frame.pack(pady = 5)


        # Dropdown Menu For script selection
        self.script_options = ["workflow.py", "self-trained.py"]
        self.selected_script = tk.StringVar(value=self.script_options[0])

        self.script_dropdown = ttk.Combobox(
            root,
            textvariable=self.selected_script,
            values=self.script_options,
            state="readonly",
            style="CustomCombobox.TCombobox"
        )
        self.script_dropdown.pack(pady=5)




        self.start_button = ttk.Button(btn_frame, text = "Start", command = self.start_pipeline)
        self.start_button.grid(row = 0, column = 0, padx = 10)

        self.exit_button = ttk.Button(btn_frame, text = "Exit", command = self.exit_app)
        self.exit_button.grid(row = 0, column = 1, padx = 10) 

        # Log viewer
        self.log_display = scrolledtext.ScrolledText(root, height = 18, width = 85, state = "disabled", font = ("Consolas", 10), bg = "#ffffff")
        self.log_display.pack(pady = 10)

        self.pipeline_process = None


    # def start_pipeline(self):
    #     self.start_button.config(state = "disabled")
    #     self.write_log("Launching pipeline...")

    #     # Progress Bar
    #     # self.progress.pack(pady=5)
    #     # self.progress.start(10)

    #     def run():
    #         selected_script = self.selected_script.get()

    #         self.pipeline_process = subprocess.Popen(
    #             [sys.executable, selected_script],
    #             stdout = subprocess.PIPE,
    #             stderr = subprocess.STDOUT,
    #             universal_newlines = True
    #         )

    #         # for line in self.pipeline_process.stdout:
    #         #     self.write_log(line.strip())
    #         for line in self.pipeline_process.stdout:
    #             line = line.strip()

    #             # Progress Bar
    #             # if self.progress.winfo_ismapped():
    #             #     self.progress.stop()
    #             #     self.progress.pack_forget()

    #             if self.isTest.get():
    #                 self.write_log(line)
    #             else:
    #                 if any(keyword in line.lower() for keyword in ["start", "launch", "initialized", "loading", "ready", "success", "successfully", "error"]):
    #                     self.write_log(line)

    #     threading.Thread(target = run, daemon = True).start()


    def start_pipeline(self):
        self.start_button.config(state="disabled")

        script = self.selected_script.get()

        # Determine actual script based on test mode toggle
        if self.isTest.get():
            self.write_log(f"Launching TEST version of: {script}")
            if script == "workflow.py":
                script_to_run = "workflow_test.py"
            elif script == "self-trained.py":
                script_to_run = "self-trained_test.py"
            else:
                self.write_log("Unknown test script.")
                return
        else:
            self.write_log(f"Launching pipeline: {script}")
            script_to_run = script

        def run():
            self.pipeline_process = subprocess.Popen(
                [sys.executable, script_to_run],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            for line in self.pipeline_process.stdout:
                line = line.strip()

                if self.isTest.get():
                    self.write_log(line)  # show all logs
                else:
                    if any(kw in line.lower() for kw in ["start", "launch", "initialized", "loading", "ready", "success", "error"]):
                        self.write_log(line)

        threading.Thread(target=run, daemon=True).start()


    def write_log(self, text):
        self.log_display.config(state="normal")

        # Matching tags to specific colors
        if "error" in text.lower():
            self.log_display.insert(tk.END, text + "\n", "tag_error")
        elif "success" in text.lower() or "detected" in text.lower():
            self.log_display.insert(tk.END, text + "\n", "tag_success")
        elif "start" in text.lower() or "launch" in text.lower():
            self.log_display.insert(tk.END, text + "\n", "tag_info")
        else:
            self.log_display.insert(tk.END, text + "\n", "tag_default")

        # Define tag styles using your selected colors
        self.log_display.tag_config("tag_error", foreground="#FFFFCC")     
        self.log_display.tag_config("tag_success", foreground="#5ACDAA")   
        self.log_display.tag_config("tag_info", foreground="#AE7EE4")      
        self.log_display.tag_config("tag_default", foreground="#5ACDAA") ## 818985  

        self.log_display.yview(tk.END)
        self.log_display.config(state="disabled")


    # def exit_app(self):
    #     if self.pipeline_process:
    #         self.write_log("Terminating pipeline...")
    #         self.pipeline_process.terminate()
    #     self.root.destroy()

    def exit_app(self):
        if self.pipeline_process:
            self.write_log("Terminating pipeline...")
            self.pipeline_process.terminate()
            self.pipeline_process = None
            self.write_log("Pipeline terminated Successfully.")
            self.start_button.config(state="normal")  # Re-enable start button so that user can can run the pipeline process again without restart the UI
        else:
            self.write_log("No pipeline is currently running.")


if __name__ ==  "__main__":
    root = tk.Tk()
    app = TeethApp(root)
    root.mainloop()
