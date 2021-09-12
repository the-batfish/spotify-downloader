import sys
from os import path as ospath
from os import remove
from tkinter import CENTER, Button, Entry, Label, StringVar, Tk,scrolledtext,INSERT,OptionMenu,LEFT
from urllib import request
from eyed3 import load as mdload
from eyed3.id3 import ID3_V2_3
from pydub import AudioSegment
from pytube import YouTube
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
from threading import Thread
from multiprocessing import cpu_count
from PIL import Image,ImageTk
from tkinter.filedialog import askdirectory

client_credentials_manager = SpotifyClientCredentials(client_id='', client_secret='')
sp = Spotify(client_credentials_manager=client_credentials_manager)
stop=False
if getattr(sys, 'frozen', False):
        application_path = ospath.dirname(sys.executable)
elif __file__:
    application_path = ospath.dirname(__file__)
def task(tracks):
    global application_path
    global window
    global stop
    download_but.config(state='disabled',text='Downloading')
    quality=variable.get()[-4::1]
    quality=quality.replace('-','')
    global location
    try:
        download_path=location
    except:
        download_path=ospath.join(application_path,'Downloads')
    for i in tracks:
        window.update()
        j=i['track']
        song=j['name']+' '+j['artists'][0]['name'] +' audio'
        try:    
            results = YoutubeSearch(song, max_results=1).to_dict()
            vid_url='http://youtu.be'+results[0]['url_suffix'].replace('watch?v=','')
            yt=YouTube(vid_url.replace('watch?v=','')).streams.get_audio_only()
            yt.download(download_path)

            scrolled.insert(INSERT,'Thread sucessfully downloaded {}\n'.format(j['name']))
    
        except Exception as e:
            yt=YouTube(vid_url).streams.get_audio_only()
            print(e,'Couldn\'t download',song,'result:',yt)

        try:
            #converting song
            webm = AudioSegment.from_file(ospath.join(download_path,yt.default_filename))
            duration_s=j['duration_ms']/1000
            if webm.duration_seconds > duration_s:
                export_song=webm[:duration_s*1000]
            else:
                export_song=webm
            export_song.export(ospath.join(download_path,str(j['artists'][0]['name']+'-'+j['name']+'.mp3').replace('"','')),format='mp3',bitrate=quality)
            #adding metadata
            audiofile=mdload(ospath.join(download_path,str(j['artists'][0]['name']+'-'+j['name']+'.mp3').replace('"','')))
            if not audiofile.tag:
                audiofile.initTag()
            request.urlretrieve(j['album']['images'][0]['url'],ospath.join(download_path,str(j['artists'][0]['name']+'-'+j['name']+'.jpg').replace('"','')))
            tag=audiofile.tag
            tag.artist = j['artists'][0]['name']
            tag.album = j['album']['name']
            tag.title = j['name']
            tag.album_artist = j['album']['artists'][0]['name']
            tag.recording_date=j['album']['release_date'][0:4]
            tag.images.set(3, open(ospath.join(download_path,str(j['artists'][0]['name']+'-'+j['name']+'.jpg').replace('"','')),'rb').read(), 'image/jpeg')
            tag.save(version=ID3_V2_3)
            #deleting stuff
            remove(ospath.join(download_path,yt.default_filename))
            remove(ospath.join(download_path,str(j['artists'][0]['name']+'-'+j['name']+'.jpg').replace('"','')))
            
            scrolled.insert(INSERT,'Converted {}\n'.format(j['name']))
        except Exception as e:
            print('Couldnt convert song',e)
        if stop==True:
            break  
    download_but.config(state='normal',text='Download songs')

def start_downloader(event=None):
    if url.get() not in ('',None):
        spotify_list=sp.playlist_tracks(url.get())
        tracks=spotify_list['items']
        url.delete(0,len(url.get()))
        if spotify_list['next'] is not None:
            tracks.extend(sp.next(spotify_list)['items'])
        global threads
        try:
            if len(threads)!=None:
                for i in threads:
                    i.join()
                print('threads were already running')    
        except:
            pass
        threads=[]
        for i in range(cpu_count()):
            t=Thread(target=task,daemon=False,args=(tracks[i::cpu_count()],))
            t.start()
            threads.append(t)
        
def stoptrue():
    global stop
    global threads
    stop=True
    window.destroy()

if __name__=='__main__':                                                                                                                                                                                                                                                                                                            
    window=Tk()
    window.geometry('500x550')
    window.resizable(False,False)
    window.configure(bg = '#3d3d3d')
    window.title('Spotify playlist downloader')
    window.protocol('WM_DELETE_WINDOW',stoptrue)
    def image_import(filename,height,width):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = ospath.abspath(".")
        try:
            image_path=ospath.join(base_path,filename)
            img=Image.open(image_path)
        except:
            image_path=ospath.join(application_path,filename)
            img=Image.open(image_path)
        img=img.resize((height,width), Image.ANTIALIAS)
        pic=ImageTk.PhotoImage(img)
        return pic
    logo=image_import('logo.png',48,48)
    lbl=Label(window,text=' SPOTIFY PLAYLIST DOWNLOADER',font = ("Arial Bold",14),bg = '#3d3d3d', fg = 'white',image=logo,compound=LEFT)
    lbl.place(relx=0.5,rely=0.08,anchor=CENTER)

    lbl1=Label(window,text='Enter playlist link:',font = ("Arial Bold",9),bg = '#3d3d3d', fg = 'white')
    lbl1.place(relx=0.12,rely=0.17,anchor=CENTER)

    lbl2=Label(window,text='Output:',font = ("Arial Bold",12),bg = '#3d3d3d', fg = 'white')
    lbl2.place(relx=0.5,rely=0.23,anchor=CENTER)

    url=Entry(window,width=60)
    url.place(relx=0.59,rely=0.17,anchor=CENTER)
    url.bind('<Return>', start_downloader)
    
    audio_quality=['Low-96k','Medium-128k','High-192k','Ultra high-320k']
    variable=StringVar(window)
    variable.set(audio_quality[1])
    dropdown=OptionMenu(window,variable,*audio_quality)
    dropdown.place(relx=0.35,rely=0.78,anchor=CENTER)

    lbl3=Label(window,text='Audio Quality:',font = ("Arial Bold",9),bg = '#3d3d3d', fg = 'white')
    lbl3.place(relx=0.14,rely=0.78,anchor=CENTER)

    lbl4=Label(window,text='Download location: '+str(ospath.join(application_path,'Downloads')),font = ("Arial Bold",9),bg = '#3d3d3d', fg = 'white')
    lbl4.place(relx=0.5,rely=0.85,anchor=CENTER)

    global scrolled
    scrolled=scrolledtext.ScrolledText(window,width = 55, height = 15, font = ("Arial",10))
    scrolled.place(relx=0.5,rely=0.48,anchor=CENTER)

    download_but=Button(window,text='Download songs',bg='grey',fg='white',font = ("Arial",12),command=start_downloader)
    download_but.place(relx=0.5,rely=0.93,anchor=CENTER)
    
    def directrory():
        global location
        location=askdirectory()
        lbl4.config(text='Download location:'+str(location))

    file=Button(window,text='Change download folder',bg='grey',fg='white',font = ("Arial",12),command=directrory)
    file.place(relx=0.7,rely=0.78,anchor=CENTER)
    window.mainloop()