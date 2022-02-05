from os import path as ospath
from os import remove,rename
from urllib import request
from mutagen.mp4 import MP4,MP4Cover
from mutagen.id3 import ID3,TIT2,APIC,TALB,TPE1,TPE2,TYER
from pytube import YouTube
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
from threading import Thread
from datetime import datetime
from pydub import AudioSegment
from tkinter import messagebox

client_credentials_manager = SpotifyClientCredentials(client_id='', client_secret='')
sp = Spotify(client_credentials_manager=client_credentials_manager)

def remove_sus_characters(name:str):
    converted = "".join(i for i in name if i not in ("/", "\\", "?", "%", "*", ":", "|", '"', "<", ">", ".", ",", ";", "="))
    return converted

def add_text(scrltxt_obj,text:str):
    scrltxt_obj.config(state='normal')
    scrltxt_obj.insert('insert',text)
    scrltxt_obj.see('end')
    scrltxt_obj.config(state='disabled')

def accusearch(results,songlen):
    for i in results:
        try:
            time = datetime.strptime(i['duration'], '%M:%S')
            vid_length = time.minute*60+time.second
        except:
            time = datetime.strptime(i['duration'], '%H:%M:%S')
            vid_length = time.hour*3600+time.minute*60+time.second
        if vid_length >= songlen+3 or vid_length <= songlen-3:
            pass
        else:
            vid_url = 'http://youtu.be'+ i['url_suffix'].replace('watch?v=', '')
            break
    return YouTube(vid_url)

def m4atagger(file,song,path):
    iconname=ospath.join(path,remove_sus_characters(song['artists'][0]['name']+'-'+song['name'])+'.jpg')
    request.urlretrieve(song['album']['images'][0]['url'],iconname)
    tags=MP4(file)
    if not tags.tags:
        tags.add_tags()
    tags[u'\xa9nam']=song['name']
    tags[u'\xa9alb']=song['album']['name']
    tags[u'\xa9ART']=', '.join([i['name'] for i in song['artists']])
    tags[u'aART']=', '.join([i['name'] for i in song['album']['artists']])
    tags[u'\xa9day']=song['album']['release_date'][0:4]
    with open(iconname,'rb') as f:
        tags['covr'] = [MP4Cover(f.read(),imageformat=MP4Cover.FORMAT_JPEG)]
    tags.save()
    remove(iconname)

def mp3convtagger(mp4,mp3,song,path):
    iconname=ospath.join(path,remove_sus_characters(song['artists'][0]['name']+'-'+song['name'])+'.jpg')
    request.urlretrieve(song['album']['images'][0]['url'],iconname)
    convert=AudioSegment.from_file(mp4)
    convert.export(mp3,format='mp3')
    tags=ID3(mp3)
    tags.add(TIT2(encoding=3, text=[song['name']]))
    tags.add(TALB(encoding=3, text=[song['album']['name']]))
    tags.add(TPE1(encoding=3, text=[i['name'] for i in song['artists']]))
    tags.add(TPE2(encoding=3, text=[i['name'] for i in song['album']['artists']]))
    tags.add(TYER(encoding=3, text=[song['album']['release_date'][0:4]]))
    with open(iconname, "rb") as f:
        tags.add(APIC(encoding=3,mime=u'image/jpeg',type=3, desc=u'Cover',data=f.read()))
    tags.save(v2_version=3)
    remove(mp4)
    remove(iconname)

def start(dlbut,scrltxt,progress,link:str,path:str,threadno:int,filetype:str):
    global threads
    global leader
    scrltxt.config(state='normal')
    scrltxt.delete(1.0,'end')
    scrltxt.config(state='disabled')
    try:
        for t in threads: 
            t.join()
        for t in leader:
            t.join()
    except:
        pass
    threads=[]
    leader=[]
    if link.startswith('https://open.spotify.com/track'):
        dlbut['state']='disabled'
        progress['maximum']=1
        for i in range(1):
            t=Thread(target=download_song,args=(link,scrltxt,path,filetype,dlbut,progress),daemon=False)
            t.start()
            threads.append(t)
    elif link.startswith('https://open.spotify.com/playlist/'):
        dlbut['state']='disabled'
        playlist=sp.playlist_tracks(link)
        name=sp.playlist(link)["name"]
        tracks=playlist['items']
        while playlist['next']:
            playlist=sp.next(playlist)
            tracks.extend(playlist)
        progress['maximum']=len(tracks)
        scrltxt.insert('insert','Downloading playlist \"{}\" with {} songs\n'.format(name,len(tracks)))
        lead=True
        for i in range(threadno):
            t=Thread(target=download_playlist,args=(tracks[i::threadno],scrltxt,path,filetype,lead,dlbut,i+1,progress),daemon=False)
            t.start()
            if not lead:
                threads.append(t)
            else:
                leader.append(t)          
            lead=False
    elif link==None:
        messagebox.showerror('No link given','You have not given a valid link,try again but this time dont forget to give a link')
    else:
        messagebox.showerror('Invalid link','You have given an invalid link,try again this time but with a correct link')

def download_song(link,scrltxt,path,filetype,button,progress):
    song=sp.track(link)
    results = YoutubeSearch(song['name']+' '+song['artists'][0]['name']+' audio', max_results=15).to_dict()
    spsonglen = int((song['duration_ms'])/1000)
    download_name=remove_sus_characters(song['artists'][0]['name']+'-'+song['name'])
    vid=accusearch(results=results,songlen=spsonglen)
    mp4path=ospath.join(path,download_name+'.mp4')
    if filetype=='.m4a':
        if not ospath.exists(ospath.join(path,download_name+'.m4a')):
            try:
                yt=vid.streams.get_audio_only()
                yt.download(path,download_name+'.mp4')
                m4apath=ospath.join(path,download_name+'.m4a')
                rename(mp4path,m4apath)
                m4atagger(m4apath,song,path)
                add_text(scrltxt,'Finished downloading and converting {}\n'.format(song['name']))
            except Exception as e:
                messagebox.showerror('Error','Oops program couldnt download {} because of {}'.format(song['name'],e))
        else:
            add_text(scrltxt,'Skipping download as {} already exists in directory\n'.format(song['name']))

    if filetype=='.mp3':
        if not ospath.exists(ospath.join(path,download_name+'.mp3')):
            try:
                yt=vid.streams.get_audio_only()
                yt.download(path,download_name+'.mp4')
                mp3path=ospath.join(path,download_name+'.mp3')
                mp3convtagger(mp4path,mp3path,song,path)
                add_text(scrltxt,'Finished downloading and converting {}\n'.format(song['name']))
            except Exception as e:
                messagebox.showerror('Error','Oops program couldnt download {} because of {}'.format(song['name'],e))
        else:
            add_text(scrltxt,'Skipping download as {} already existed\n'.format(song['name']))
        
    progress['value']=1
    button['state']='normal'
    messagebox.showinfo("Song has finished downloading","The song has finished downloading")
    progress['value']=0

def download_playlist(tracks,scrltxt,path,filetype,leader,button,number,progress):
    for i in tracks:
        song=i['track']
        results = YoutubeSearch(song['name']+' '+song['artists'][0]['name']+' audio', max_results=15).to_dict()
        spsonglen = int((song['duration_ms'])/1000)
        download_name=remove_sus_characters(song['artists'][0]['name']+'-'+song['name'])
        vid=accusearch(results=results,songlen=spsonglen)
        mp4path=ospath.join(path,download_name+'.mp4')
        if filetype=='.m4a':
            if not ospath.exists(ospath.join(path,download_name+'.m4a')):
                try:
                    yt=vid.streams.get_audio_only()
                    yt.download(path,download_name+'.mp4')
                    m4apath=ospath.join(path,download_name+'.m4a')
                    rename(mp4path,m4apath)
                    m4atagger(m4apath,song,path)
                    add_text(scrltxt,'Finished downloading and converting {}\n'.format(song['name']))
                except Exception as e:
                    messagebox.showerror('Error','Oops program couldnt download {} because of {}'.format(song['name'],e))
            else:
                add_text(scrltxt,'Skipping download as {} already existed\n'.format(song['name']))

        if filetype=='.mp3':
            if not ospath.exists(ospath.join(path,download_name+'.mp3')):
                try:
                    yt=vid.streams.get_audio_only()
                    yt.download(path,download_name+'.mp4')
                    mp3path=ospath.join(path,download_name+'.mp3')
                    mp3convtagger(mp4path,mp3path,song,path)
                    add_text(scrltxt,'Finished downloading and converting {}\n'.format(song['name']))
                except Exception as e:
                    messagebox.showerror('Error','Oops program couldnt download {} because of {}'.format(song['name'],e))
            else:
                add_text(scrltxt,'Skipping download as {} already existed\n'.format(song['name']))

        '''if filetype=='.webm':
            if not ospath.exists(ospath.join(path,download_name+'.webm')):
                yt=vid.streams.filter(mime_type='audio/webm').order_by('abr').desc()[0]
                yt.dowload(path,download_name+'.webm')
                webmpath=ospath.join(path,download_name+'.webm')
                #webmtagger()'''
        
        progress['value']+=1
    if leader:
        global threads
        for i in threads:
            i.join()
        button['state']='normal'
        messagebox.showinfo("Songs have finished downloading","All the songs have finished downloading")
        progress['value']=0
