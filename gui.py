# importing necessary libraries
# fmt: off
import os
import sys
from pickle import dump, load
from platform import system
from tkinter import (CENTER, HORIZONTAL,  # tkinter for the user interface
                     LEFT, Button, Entry, IntVar, Label, LabelFrame,
                     OptionMenu, Scale, StringVar, Tk, scrolledtext, ttk)
from tkinter.filedialog import askdirectory
from tkinter.ttk import Progressbar
from webbrowser import open_new_tab
from customtkinter import *

from PIL import (  # Python Imaging Library(PIL) for inserting images into the user interface
    Image, ImageTk)

import downloader
# fmt: on


set_appearance_mode("System")  # Modes: system (default), light, dark
set_default_color_theme("blue")   # Themes: blue (default), dark-blue, green




class App(Tk):
    def __init__(self):
        super().__init__()

        self.tk.call('source', 'forest-dark.tcl')
        ttk.Style().theme_use('forest-dark')
        # Configuring Window
        self.geometry("600x600")
        self.resizable(False, False)
        self.configure(bg="#333333")
        self.title("Spotitube Downloader")
        self.iconphoto(True, self.image_import("./img/logo.ico", 32, 32))



        # Getting path to the directory
        if getattr(sys, "frozen", False):
            self.application_path = os.path.dirname(sys.executable)
        elif __file__:
            self.application_path = os.path.dirname(__file__)

        # Get previous configuration
        self.config_data = None
        if os.path.exists(os.path.join(self.application_path, "spdconfig.dat")):
            with open(os.path.join(self.application_path, "spdconfig.dat"), "rb") as f:
                self.config_data = load(f)

        # Setting download location
        if self.config_data:
            self.location = self.config_data["location"]
        elif system() == "Darwin":
            self.location = os.path.join(
                os.path.expanduser("~/Music"), "Spotify Downloader/Downloads"
            )
        else:
            self.location = os.path.join(self.application_path, "Downloads").replace(
                "\\", "/"
            )

        # Widgets in the window
        self.logo = self.image_import("img/logo.png", 48, 48)
        title = ttk.Label(
            self,
            text=" SPOTITUBE DOWNLOADER",
            image=self.logo,
            compound=LEFT,
            font=("Helvetica", 20),
        )
        title.place(relx=0.5, rely=0.05, anchor=CENTER)

        entry_label = ttk.Label(
            self,
            text="Song/Playlist Link:",
            font=("Helvetica", 12),
        )
        entry_label.place(relx=0.15, rely=0.12, anchor=CENTER)

        output_label = ttk.Label(
            self, text="OUTPUT:"
        )
        output_label.place(relx=0.5, rely=0.17, anchor=CENTER)

        self.location_label = ttk.Label(
            self,
            text="Download location:" + str(self.location),
            justify=LEFT,
            font=("Helvetica", 10),
        )
        self.location_label.place(relx=0.5, rely=0.84, anchor=CENTER)
        self.location_label.config(text="Download location:" + str(self.location))

        thread_number = ttk.Label(
            self,
            text="Thread count:",
            font=("Helvetica", 10),
        )
        thread_number.place(relx=0.12, rely=0.78, anchor=CENTER)

        filetype = ttk.Label(
            self, text="Filetype:",
            font=("Helvetica", 10),
        )
        filetype.place(relx=0.45, rely=0.78, anchor=CENTER)

        bitrate = ttk.Label(
            self, text="Bitrate:",
            font=("Helvetica", 10),
        )
        bitrate.place(relx=0.73, rely=0.78, anchor=CENTER)

        self.progress = Progressbar(
            self, orient=HORIZONTAL, mode="determinate", length=100
        )
        self.progress.place(relx=0.5, rely=0.7, width=400, anchor=CENTER)

        self.output_box = scrolledtext.ScrolledText(
            self, font=("Helvetica", 10), state="disabled", fg="#00ff00", bg="#333333"
        )
        self.output_box.place(relx=0.5, rely=0.43, height=280, width=500, anchor=CENTER)

        self.download_logo = self.image_import("img/dl_logo.png", 20, 20)
        self.download_button = ttk.Button(
            self,
            text="Download songs",
            image=self.download_logo,
            compound=LEFT,
            command=lambda: self.start_downloader(),
        )
        self.download_button.place(relx=0.7, rely=0.91, anchor=CENTER)

        dl_location_button = ttk.Button(
            self,
            text="Change download folder",
            command=lambda: self.directory(),
        )
        dl_location_button.place(
            relx=0.3,
            rely=0.91,
            anchor=CENTER,
        )

        filetypes = ["fast .m4a", "quality .m4a", ".mp3", ".wav", ".flac"]
        self.filetype_default = StringVar(value="fast .m4a")
        filetype_dropdown = ttk.OptionMenu(self, self.filetype_default, *filetypes)
        filetype_dropdown.place(relx=0.51, rely=0.755)
        # Save variable value when it is modified
        self.filetype_default.trace_add("write", self.saveconf)

        bitrates = ["96k", "128k", "192k", "320k"]
        self.bitrate_default = StringVar(value="192k")
        bitrate_dropdown = ttk.OptionMenu(self, self.bitrate_default, *bitrates)
        bitrate_dropdown.place(relx=0.78, rely=0.755)
        # Save variable value when it is modified
        self.bitrate_default.trace_add("write", self.saveconf)

        self.threads_default = IntVar(value=4)
        thread_scale = ttk.Scale(
            self,
            variable=self.threads_default,
            from_=1,
            to=20,
            orient=HORIZONTAL,
        )
        thread_scale.place(relx=0.2, rely=0.765)
        # Save variable value when it is modified
        self.threads_default.trace_add("write", self.saveconf)

        # Setting previous configuration if it exists
        if self.config_data:
            self.filetype_default.set(self.config_data["filetype"])
            self.bitrate_default.set(self.config_data["bitrate"])
            self.threads_default.set(self.config_data["threads"])

        entry_cont = ttk.LabelFrame(
            self,
            borderwidth=5,
            labelanchor="n",
        )
        # entry_cont.place(relx=0.62, rely=0.12, width=394, height=24, anchor=CENTER)

        self.playlist_link = ttk.Entry(self)
        self.playlist_link.place(
            relx=0.62, rely=0.12, width=390, height=30, anchor=CENTER, bordermode=OUTSIDE
        )
        self.playlist_link.bind("<Return>", lambda e: self.start_downloader())

        discord_link = ttk.Label(
            self,
            text="Click here to contact us on discord if you have any problems",
            cursor="hand2",
        )
        discord_link.place(relx=0.5, rely=0.97, anchor=CENTER)
        discord_link.bind("<Button-1>", lambda event: self.server_invite(event))



    def server_invite(self, event):
        open_new_tab("https://discord.gg/8pTQAfAAbm")
        event.widget.config(fg="#5c67f6")

    # function for importing pictures into the gui
    def image_import(self, filepath, height, width):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        try:
            image_path = os.path.join(base_path, filepath)
            img = Image.open(image_path)
        except:
            image_path = os.path.join(self.application_path, filepath)
            img = Image.open(image_path)
        img = img.resize((height, width), Image.Resampling.BOX)
        pic = ImageTk.PhotoImage(img)
        return pic

    # download location related stuff
    def directory(self):
        location = askdirectory()
        if location:
            self.location = location
            config_data = {
                "location": location,
                "bitrate": self.bitrate_default.get(),
                "filetype": self.filetype_default.get(),
                "threads": self.threads_default.get(),
            }
            with open(os.path.join(self.application_path, "spdconfig.dat"), "wb") as f:
                dump(config_data, f)
            self.location_label.config(text="Download location:" + str(location))

    def saveconf(self, *args):
        config_data = {
            "location": self.location,
            "bitrate": self.bitrate_default.get(),
            "filetype": self.filetype_default.get(),
            "threads": self.threads_default.get(),
        }
        with open(os.path.join(self.application_path, "spdconfig.dat"), "wb") as f:
            dump(config_data, f)

    def start_downloader(self):
        link = self.playlist_link.get()
        self.playlist_link.delete(0, len(link))
        threads = self.threads_default.get()
        filetype = self.filetype_default.get()
        bitrate = self.bitrate_default.get()
        downloader.start(
            dlbut=self.download_button,
            link=link,
            path=self.location,
            threadno=threads,
            filetype=filetype,
            scrltxt=self.output_box,
            progress=self.progress,
            bitrate=bitrate,
        )


# Starting GUI
App().mainloop()
