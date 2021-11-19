import sys
import tkinter
from os import path as ospath
from os import remove, rename
from threading import Thread
from tkinter import scrolledtext, filedialog, messagebox
from urllib import request
from datetime import datetime
from mutagen import easymp4, mp4
from PIL import Image, ImageTk
from pytube import YouTube
from spotipy import Spotify
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch


class GUI(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.geometry('550x600')
        self.resizable(False, False)
        self.configure(background='#323232')
        self.title('Spotify playlist downloader')
        self.protocol('WM_DELETE_WINDOW', self.stoptrue)

        for i in range(14):
            self.rowconfigure(i, weight=1)
        for i in range(8):
            self.columnconfigure(i, weight=1)
        
        #scope='user-library-read'
        client_credentials_manager = SpotifyClientCredentials(
            client_id='', client_secret='')
        self.sp = Spotify(client_credentials_manager=client_credentials_manager)

        self.stop = False
        if getattr(sys, 'frozen', False):
            self.application_path = ospath.dirname(sys.executable)
        elif __file__:
            self.application_path = ospath.dirname(__file__)

        self.logo = self.image_import('logo.png', 48, 48)
        header = tkinter.Label(self, text=' SPOTIFY PLAYLIST DOWNLOADER', font=(
            "Arial Bold", 20), background='#323232', foreground='white', image=self.logo, compound='left')
        header.grid(row=0, column=0, columnspan=9, sticky="NSEW")

        url_label = tkinter.Label(self, text='Enter playlist link: ', font=(
            "Arial Bold", 12), background='#323232', foreground='white')
        url_label.grid(row=1, column=1, sticky="E")

        self.url = tkinter.Entry(self)
        self.url.grid(row=1, column=2, columnspan=4, sticky="EW")
        self.url.bind('<Return>', self.start_downloader)

        output_label = tkinter.Label(self, text="OUTPUT", font=(
            "Arial Bold", 15), background="#323232", foreground="white")
        output_label.grid(row=2, column=1, columnspan=6, sticky="NSEW")

        scrolled_cont = tkinter.LabelFrame(self, font=(
            "Arial Bold", 15), background='#1DB954', foreground='white', borderwidth=5, labelanchor="n")
        scrolled_cont.grid(row=3, column=1, rowspan=8,
                           columnspan=6, sticky="NSEW")
        scrolled_cont.grid_propagate(False)

        scrolled_cont.rowconfigure(0, weight=1)
        scrolled_cont.columnconfigure(0, weight=1)

        self.scrolled = scrolledtext.ScrolledText(
            scrolled_cont, font=("Arial", 10),  state="disabled")
        self.scrolled.grid(row=0, column=0)

        cnvrt_label = tkinter.Label(self, text='Convert songs:', font=(
            "Arial Bold", 12), background='#323232', foreground='white')
        cnvrt_label.grid(row=11, column=1, sticky="SE")

        self.cnvrt_bool = True
        self.cnvrt_button = tkinter.Button(
            self, text='ON', bd=0, background='#d3d3d3', foreground='black', highlightcolor="#1DB954", font=("Arial", 12), command=self.convert, relief="flat")
        self.cnvrt_button.grid(row=11, column=2, sticky="SW")

        change_dir_button = tkinter.Button(self, text='Change download folder', bd=0, background='#d3d3d3', foreground='black', highlightcolor="#1DB954", font=(
            "Arial", 12), command=self.directrory)
        change_dir_button.grid(row=11, column=5, sticky="S")

        self.curr_dir_label = tkinter.Label(self, text='Download location: '+str(ospath.join(
            self.application_path, 'Downloads')), wraplength=500, font=("Arial Bold", 12), background='#323232', foreground='white')
        self.curr_dir_label.grid(row=12, column=0, columnspan=8, sticky="SEW")

        self.dl_logo = self.image_import('dl_logo.png', 27, 27)
        self.download_but = tkinter.Button(self, text='Download songs', bd=0, background='#d3d3d3', foreground='black', highlightcolor="#1DB954", font=(
            "Arial", 20), command=self.start_downloader, image=self.dl_logo, compound='left', relief="flat", padx=10)
        self.download_but.grid(row=13, column=1, columnspan=6)

    def image_import(self, filename, height, width):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = ospath.abspath(".")
        try:
            image_path = ospath.join(base_path, filename)
            img = Image.open(image_path)
        except:
            image_path = ospath.join(self.application_path, filename)
            img = Image.open(image_path)
        img = img.resize((height, width), Image.LANCZOS)
        pic = ImageTk.PhotoImage(img)
        return pic

    def directrory(self):
        self.location = filedialog.askdirectory()
        if self.location:
            self.curr_dir_label.config(
                text='Download location:'+str(self.location))
        else:
            pass

    def convert(self):
        if self.cnvrt_bool:
            self.cnvrt_button.config(text='OFF')
            self.cnvrt_bool = False
        else:
            self.cnvrt_button.config(text='ON')
            self.cnvrt_bool = True

    def start_downloader(self, event=None):
        try:
            if self.url.get() not in ('', None):
                self.download_but.config(state='disabled', text='Downloading')
                name = self.sp.playlist(self.url.get())["name"]
                spotify_list = self.sp.playlist_tracks(self.url.get())
                tracks = spotify_list['items']
                self.url.delete(0, len(self.url.get()))
                if spotify_list['next'] is not None:
                    tracks.extend(self.sp.next(spotify_list)['items'])
                self.scrolled.config(state="normal")
                self.scrolled.insert(
                    'insert', '"{}" playlist has {} song(s)\n'.format(name, len(tracks)))
                self.scrolled.config(state="disabled")
                self.scrolled.see('end')
                try:
                    if len(self.twlead) != None:
                        for i in self.twlead:
                            i.join()
                        print('threads were already running')
                except:
                    pass
                self.threads = []
                self.twlead = []
                stopper = True
                for i in range(10):
                    t = Thread(target=self.task, daemon=False,
                               args=(tracks[i::10], stopper,i+1))
                    t.start()
                    self.twlead.append(t)
                    if not stopper:
                        self.threads.append(t)
                    stopper = False
        except SpotifyException as e:
            self.download_but.config(state="normal", text='Download Songs')
            messagebox.showwarning(
                e.http_status, f"Message: {' '.join(e.args[2].split()[1::])}\nHTTP Status: {e.http_status}\nCode: {e.code}")

    def task(self, tracks, stopper,threadno):
        try:
            download_path = self.location
        except:
            download_path = ospath.join(self.application_path, 'Downloads')
        for i in tracks:
            self.update()
            j = i['track']
            song = j['name']+' '+j['artists'][0]['name']+' audio'
            m4a_name = ''
            for i in j['artists'][0]['name']+'-'+j['name']:
                if i not in ['/','\\','?','%','*',':','|','"','<','>','.',',',';','=']:
                    m4a_name += i
                else:
                    m4a_name += ' '
            download_name = m4a_name+'.mp4'
            m4a_name += '.m4a'
            mp4path = ospath.join(download_path, download_name)
            m4apath = ospath.join(download_path, m4a_name)
            try:
                if ospath.exists(m4apath) or ospath.exists(mp4path):
                    self.scrolled.config(state="normal")
                    self.scrolled.insert(
                        'insert', 'Song Already Exists in Download Directory ({})\n'.format(j['name']))
                    self.scrolled.see('end')
                    self.scrolled.config(state="disabled")
                else:
                    results = YoutubeSearch(song, max_results=15).to_dict()
                    spsonglen=int((j['duration_ms'])/1000)
                    for i in results:
                        try:
                            time=datetime.strptime(i['duration'],'%M:%S')
                            vid_length=time.minute*60+time.second
                        except:
                            time=datetime.strptime(i['duration'],'%H:%M:%S')
                            vid_length=time.hour*3600+time.minute*60+time.second
                        if vid_length >= spsonglen+5 or vid_length <= spsonglen-5:
                            pass
                        else:
                            vid_url='http://youtu.be'+i['url_suffix'].replace('watch?v=','')
                            vid=YouTube(vid_url.replace('watch?v=',''))
                            break
                    yt = vid.streams.get_audio_only()

                    if not ospath.exists(m4apath) or ospath.exists(mp4path):
                        yt.download(download_path, download_name)
                        self.scrolled.config(state="normal")
                        self.scrolled.insert(
                            'insert', 'Thread {} sucessfully downloaded {}\n'.format(threadno,j['name']))
                        self.scrolled.see('end')
                        self.scrolled.config(state="disabled")

            except Exception as e:
                messagebox.showerror(
                    f"Couldn't Download {song}", f"{e}")
                print(e, 'Couldn\'t download', song)

            if self.cnvrt_bool and ospath.exists(mp4path):
                try:
                    # converting song
                    rename(mp4path, m4apath)
                    # adding metadata
                    tags = easymp4.EasyMP4(m4apath)
                    if not tags.tags:
                        tags.add_tags()
                    artists = ''
                    for i in j['artists']:
                        if i == j['artists'][-1]:
                            artists += i['name']
                        else:
                            artists += i['name']+','
                    tags['artist'] = artists
                    tags['album'] = j['album']['name']
                    tags['title'] = j['name']
                    tags['albumartist'] = j['album']['artists'][0]['name']
                    tags['date'] = j['album']['release_date'][0:4]
                    tags.save()
                    # adding cover art
                    coverart = mp4.MP4(m4apath)
                    iconname = ospath.join(download_path, str(m4a_name.replace('.m4a','.jpg')))
                    request.urlretrieve(
                        j['album']['images'][0]['url'], iconname)
                    with open(iconname, 'rb') as f:
                        coverart['covr'] = [mp4.MP4Cover(
                            f.read(), imageformat=mp4.MP4Cover.FORMAT_JPEG)]
                    coverart.save()
                    remove(iconname)
                    self.scrolled.config(state="normal")
                    self.scrolled.insert(
                        'insert', 'Thread {} Converted "{}"\n'.format(threadno,j['name']))
                    self.scrolled.see('end')
                    self.scrolled.config(state="disabled")
                except Exception as e:
                    self.scrolled.config(state="normal")
                    self.scrolled.insert(
                        'insert', "Couldn't Convert '{}'\n".format(j['name']))
                    self.scrolled.see('end')
                    self.scrolled.config(state="disabled")
                    print('Couldnt convert song', e)
            elif not self.cnvrt_bool and ospath.exists(mp4path):
                self.scrolled.config(state="normal")
                self.scrolled.insert(
                    'insert', 'Skipping "{}" Conversion\n'.format(j['name']))
                self.scrolled.see('end')
                self.scrolled.config(state="disabled")

            if self.stop == True:
                break
        if stopper:
            for i in self.threads:
                i.join()
            self.download_but.config(state='normal', text='Download songs')
            self.scrolled.config(state="normal")
            self.scrolled.insert(
                'insert', 'Songs Have Finished Downloading\n\n')
            self.scrolled.see('end')
            self.scrolled.config(state="disabled")
            messagebox.showinfo("Playlist Downloaded",
                                "Songs Have Finished Downloading")

    def stoptrue(self):
        self.stop = True
        if hasattr(self, "twlead"):
            for i in self.twlead:
                i.join()
        self.destroy()


if __name__ == '__main__':
    App = GUI()
    App.mainloop()
