from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
from pytube import YouTube
from pydub import AudioSegment
from multiprocessing import Pool,cpu_count,freeze_support
from os import remove
from os import path as ospath
import sys
from eyed3 import load as mdload
from tkinter import Tk,Label,Button,Entry,CENTER,NORMAL,DISABLED
from urllib import request
from eyed3.id3 import ID3_V2_3
from time import time

client_credentials_manager = SpotifyClientCredentials(client_id='', client_secret='')
sp = Spotify(client_credentials_manager=client_credentials_manager)

def task(list,thread):
    if getattr(sys, 'frozen', False):
            application_path = ospath.dirname(sys.executable)
    elif __file__:
        application_path = ospath.dirname(__file__)
    download_path=ospath.join(application_path,'Downloads')
    referencedict={}
    for i in list:
        j=i['track']
        song=j['name']+' '+j['artists'][0]['name'] +' audio'
        try:    
            results = YoutubeSearch(song, max_results=1).to_dict()
            vid_url='http://youtu.be'+results[0]['url_suffix'].replace('watch?v=','')
            yt=YouTube(vid_url.replace('watch?v=','')).streams.get_audio_only()
            yt.download(download_path)
            referencedict[yt.default_filename]={
                'mp3name':str(j['artists'][0]['name']+'-'+j['name']+'.mp3').replace('"',''),
                'iconname':str(j['artists'][0]['name']+'-'+j['name']+'.jpg').replace('"',''),
                'iconurl':j['album']['images'][0]['url'],
                'artist':j['artists'][0]['name'],
                'album':j['album']['name'],
                'albumartist':j['album']['artists'][0]['name'],
                'title':j['name'],
                'date':j['album']['release_date'][0:4]
                }
            print('Thread {} sucessfully downloaded a song'.format(thread))
        except:
            yt=YouTube(vid_url).streams.get_audio_only()
            print('Couldn\'t download',song,'result:',yt)

    for i in referencedict:
        try:
            #converting song
            export_song = AudioSegment.from_file(ospath.join(download_path,i))
            export_song.export(ospath.join(download_path,referencedict[i]['mp3name']),format='mp3',bitrate='128k')
            #adding metadata
            audiofile=mdload(ospath.join(download_path,referencedict[i]['mp3name']))
            if not audiofile.tag:
                audiofile.initTag()
            request.urlretrieve(referencedict[i]['iconurl'],ospath.join(download_path,referencedict[i]['iconname']))
            tag=audiofile.tag
            tag.artist = referencedict[i]['artist']
            tag.album = referencedict[i]['album']
            tag.title = referencedict[i]['title']
            tag.album_artist = referencedict[i]['albumartist']
            tag.recording_date=referencedict[i]['date']
            tag.images.set(3, open(ospath.join(download_path,referencedict[i]['iconname']),'rb').read(), 'image/jpeg')
            tag.save(version=ID3_V2_3)
            #deleting stuff
            remove(ospath.join(download_path,i))
            remove(ospath.join(download_path,referencedict[i]['iconname']))
            print('Converted a song')
        except Exception as e:
            print('Couldnt convert song',e)
    referencedict.clear()

if __name__ == '__main__':
    freeze_support()
    def start(event = None):
        def dl():
            spotify_list=sp.playlist_tracks(url.get())
            tracks=spotify_list['items']
            url.delete(0,len(url.get()))
            window.update()
            if spotify_list['next'] is not None:
                tracks.extend(sp.next(spotify_list)['items'])
            procs=[]
            for i in range(cpu_count()-1):
                p=Pool(1)
                poollist=tracks[i::cpu_count()-1]
                r=p.apply_async(task,[poollist,str(i+1)])
                procs.append(r)
            for r in procs:
                r.wait()
            p.close()
            p.join()
            download_but.config(state='normal',text='Download songs')
        download_but.config(state='disabled',text='Downloading')
        window.update()
        window.after(5,dl)                                                                                                                                                                                                                                                                                                                                                                                                        
    window=Tk()
    window.geometry('500x300')
    window.resizable(False,False)
    window.title('Spotify playlist downloader')

    lbl=Label(window,text='SPOTIFY PLAYLIST DOWNLOADER',font = ("Arial Bold",12))
    lbl.place(relx=0.5,rely=0.3,anchor=CENTER)

    url=Entry(window,width=75)
    url.place(relx=0.5,rely=0.5,anchor=CENTER)
    url.bind('<Return>', start)

    download_but=Button(window,text='Download songs',bg='black',fg='white',font = ("Arial",12),command=start)
    download_but.place(relx=0.5,rely=0.63,anchor=CENTER)

    window.mainloop()