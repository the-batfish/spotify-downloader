import sys
from os import path as ospath
from os import remove,rename
from tkinter import CENTER, Button, Entry, Label, Tk,scrolledtext,INSERT,LEFT
from urllib import request
from mutagen import easymp4,mp4
from pytube import YouTube
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
from threading import Thread
from multiprocessing import cpu_count
from PIL import Image,ImageTk
from tkinter.filedialog import askdirectory
<<<<<<< Updated upstream
=======
from datetime import datetime
from time import time as ttime
>>>>>>> Stashed changes

client_credentials_manager = SpotifyClientCredentials(client_id='', client_secret='')
sp = Spotify(client_credentials_manager=client_credentials_manager)

stop=False

if getattr(sys, 'frozen', False):
        application_path = ospath.dirname(sys.executable)
elif __file__:
    application_path = ospath.dirname(__file__)  

def task(tracks,stopper):
    global application_path
    global window
    global stop

    global location
    try:
        download_path=location
    except:
        download_path=ospath.join(application_path,'Downloads')

    for i in tracks:
        j=i['track']
        song=j['name']+' '+j['artists'][0]['name'] +' audio'
        try:
            m4a_name=''
            for i in j['artists'][0]['name']+'-'+j['name']:
                if i in ['/','\\','?','%','*',':','|','"','<','>','.',',',';','=']:
                    m4a_name+=' '
                else:
                    m4a_name+=i
            download_name=m4a_name+'.mp4'
            m4a_name+='.m4a'
            mp4path=ospath.join(download_path,download_name)
            m4apath=ospath.join(download_path,m4a_name)
            if not ospath.exists(m4apath) or ospath.exists(mp4path):  
                results = YoutubeSearch(song, max_results=15).to_dict()
                spsonglen=int((j['duration_ms'])/1000)
                for i in results:
                    try:
                        time=datetime.strptime(i['duration'],'%M:%S')
                        vid_length=time.minute*60+time.second
                    except:
                        time=datetime.strptime(i['duration'],'%H:%M:%S')
                        vid_length=time.hour*3600+time.minute*60+time.second
                    if vid_length >= spsonglen+10 or vid_length <= spsonglen-10 :
                        pass
                    else:
                        vid_url='http://youtu.be'+i['url_suffix'].replace('watch?v=','')
                        vid=YouTube(vid_url.replace('watch?v=',''))
                    
                yt=vid.streams.get_audio_only()
                yt.download(download_path,download_name)
                scrolled.insert(INSERT,'Thread sucessfully downloaded {}\n'.format(j['name']))
                scrolled.see('end')
    
        except Exception as e:
            yt=YouTube(vid_url).streams.get_audio_only()
            print(e,'Couldn\'t download',song,'result:',yt)

        global convertcheck
        if convertcheck and ospath.exists(mp4path):
            try:
                #converting song
                rename(mp4path,m4apath)
                #adding metadat
                tags=easymp4.EasyMP4(m4apath)
                if not tags.tags:
                    tags.add_tags()
                artists=''
                for i in j['artists']:
                    if i==j['artists'][-1]:
                        artists+=i['name']
                    else:
                        artists+=i['name']+','
                tags['artist'] = artists
                tags['album'] = j['album']['name']
                tags['title'] = j['name']
                tags['albumartist'] = j['album']['artists'][0]['name']
                tags['date']=j['album']['release_date'][0:4]
                tags.save()
                #adding cover art
                coverart=mp4.MP4(m4apath)
                iconname=ospath.join(download_path,str(j['artists'][0]['name']+'-'+j['name']+'.jpg').replace('"',''))
                request.urlretrieve(j['album']['images'][0]['url'],iconname)
                with open(iconname,'rb') as f:
                    coverart['covr'] = [mp4.MP4Cover(f.read(),imageformat=mp4.MP4Cover.FORMAT_JPEG)]
                coverart.save()
                remove(iconname)            
                scrolled.insert(INSERT,'Converted {}\n'.format(j['name']))
                scrolled.see('end')
            except Exception as e:
                print('Couldnt convert song',e)
        if stop==True:
            break
    if stopper:
        global start_time
        global no_of_tracks
        end=ttime()
        for i in threads:
            i.join()
        download_but.config(state='normal',text='Download songs')
<<<<<<< Updated upstream
        scrolled.insert(INSERT,'Songs have finished downloading\n')
=======
        scrolled.insert(INSERT,'{} tracks have downloaded in {} seconds\n'.format(no_of_tracks,int(end-start_time)))
>>>>>>> Stashed changes
        scrolled.see('end')

def start_downloader(event=None):
    if url.get() not in ('',None):
<<<<<<< Updated upstream
=======
        global start_time
        start_time=ttime()
>>>>>>> Stashed changes
        download_but.config(state='disabled',text='Downloading')
        spotify_list=sp.playlist_tracks(url.get())
        tracks=spotify_list['items']
        url.delete(0,len(url.get()))
        if spotify_list['next'] is not None:
            tracks.extend(sp.next(spotify_list)['items'])
<<<<<<< Updated upstream
        scrolled.insert(INSERT,'Your playlist has {} songs\n'.format(len(tracks)))
=======
        global no_of_tracks
        no_of_tracks=len(tracks)
        scrolled.insert(INSERT,'Your playlist has {} songs\n'.format(no_of_tracks))
>>>>>>> Stashed changes
        scrolled.see('end')
        global threads
        global twlead
        try:
            if len(twlead)!=None:
                for i in twlead:
                    i.join()
                print('threads were already running')    
        except:
            pass
        threads=[]
        twlead=[]
        stopper=True
        for i in range(cpu_count()):
            t=Thread(target=task,daemon=False,args=(tracks[i::cpu_count()],stopper))
            t.start()
            twlead.append(t)
            if not stopper:
                threads.append(t)
            stopper=False
        
def stoptrue():
    global stop
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

    lbl4=Label(window,text='Download location: '+str(ospath.join(application_path,'Downloads')),font = ("Arial Bold",9),bg = '#3d3d3d', fg = 'white')
    lbl4.place(relx=0.5,rely=0.85,anchor=CENTER)

    global scrolled
    scrolled=scrolledtext.ScrolledText(window,width = 55, height = 15, font = ("Arial",10))
    scrolled.place(relx=0.5,rely=0.48,anchor=CENTER)
    
    dl_logo=image_import('dl_logo.png',40,40)
    download_but=Button(window,text='Download songs',bg='grey',fg='white',font = ("Arial",14),command=start_downloader,image=dl_logo,compound=LEFT)
    download_but.place(relx=0.5,rely=0.93,anchor=CENTER)
    
    convertlbl=Label(window,text='Convert songs:',font = ("Arial Bold",9),bg = '#3d3d3d', fg = 'white')
    convertlbl.place(relx=0.15,rely=0.78,anchor=CENTER)
    global convertcheck
    convertcheck=True

    def convert():
        global convertcheck
        if convertcheck:
            convertbut.config(text='OFF')
            convertcheck=False
        else:
            convertbut.config(text='ON')
            convertcheck=True
       
    convertbut=Button(window,text='ON',bg='grey',fg='white',font = ("Arial",12),command=convert)
    convertbut.place(relx=0.29,rely=0.78,anchor=CENTER)

    def directrory():
        global location
        location=askdirectory()
        if location:
            lbl4.config(text='Download location:'+str(location))
        else:
            pass

    file=Button(window,text='Change download folder',bg='grey',fg='white',font = ("Arial",12),command=directrory)
    file.place(relx=0.7,rely=0.78,anchor=CENTER)
    window.mainloop()