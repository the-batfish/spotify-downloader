from os import path as ospath
from os import remove,rename
from urllib import request
from mutagen.mp4 import MP4,MP4Cover
from mutagen.id3 import ID3,TIT2,APIC,TALB,TPE1,TPE2,TYER,TRCK
from mutagen.wave import WAVE
from pytube import YouTube
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
from threading import Thread
from datetime import datetime
from pydub import AudioSegment
from tkinter import messagebox
from mysql.connector import connect
from ytmusicapi import YTMusic

ytm=YTMusic()

def checkdb(splink):
    db=connect(host='',user='',passwd='',database='')
    cur=db.cursor(buffered=True)
    cur.execute('Select ytlink from songs where splink like"{}%"'.format(splink))
    data=cur.fetchone()
    cur.close()
    db.close()
    return data

def songnotfound(splink):
    db=connect(host='',user='',passwd='',database='')
    cur=db.cursor(buffered=True)
    cur.execute('insert into notfound values("{}")'.format(splink))
    db.commit()
    cur.close()
    db.close()

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

def logger(text):
    with open('log.txt','a') as f:
        f.write(text)

def accusearch(results,songlen):
    for i in results:
        try:
            time = datetime.strptime(i['duration'], '%M:%S')
            vid_length = time.minute*60+time.second
        except:
            time = datetime.strptime(i['duration'], '%H:%M:%S')
            vid_length = time.hour*3600+time.minute*60+time.second
        if vid_length >= songlen+5 or vid_length <= songlen-5:
            pass
        else:
            vid_url = 'http://youtu.be'+ i['url_suffix'].replace('watch?v=', '')
            break
    try:
        return YouTube(vid_url)
    except:
        pass

def m4atagger(mp4,m4a,song,path):
    try:
        rename(mp4,m4a)
        iconname=ospath.join(path,remove_sus_characters(song['artists'][0]['name']+'-'+song['name'])+'.jpg')
        request.urlretrieve(song['album']['images'][0]['url'],iconname)
        tags=MP4(m4a)
        if not tags.tags:
            tags.add_tags()
        tags[u'\xa9nam']=song['name']
        tags[u'\xa9alb']=song['album']['name']
        tags[u'\xa9ART']=', '.join([i['name'] for i in song['artists']])
        tags[u'aART']=', '.join([i['name'] for i in song['album']['artists']])
        tags[u'\xa9day']=song['album']['release_date'][0:4]
        tags[u'trkn']=((int(song["track_number"]),int(song['album']['total_tracks'])),)
        with open(iconname,'rb') as f:
            tags['covr'] = [MP4Cover(f.read(),imageformat=MP4Cover.FORMAT_JPEG)]
        tags.save()
        remove(iconname)
    except Exception as e:
        print(e)

def mp3convtagger(mp4,mp3,song,path,bitrate):
    try:
        iconname=ospath.join(path,remove_sus_characters(song['artists'][0]['name']+'-'+song['name'])+'.jpg')
        request.urlretrieve(song['album']['images'][0]['url'],iconname)
        convert=AudioSegment.from_file(mp4)
        convert.export(mp3,format='mp3',bitrate=bitrate)
        tags=ID3(mp3)
        tags.add(TIT2(encoding=3, text=[song['name']]))
        tags.add(TALB(encoding=3, text=[song['album']['name']]))
        tags.add(TPE1(encoding=3, text=[i['name'] for i in song['artists']]))
        tags.add(TPE2(encoding=3, text=[i['name'] for i in song['album']['artists']]))
        tags.add(TYER(encoding=3, text=[song['album']['release_date'][0:4]]))
        tags.add(TRCK(encoding=3, text=[song['track_number']]))
        with open(iconname, "rb") as f:
            tags.add(APIC(encoding=3,mime=u'image/jpeg',type=3, desc=u'Cover',data=f.read()))
        tags.save(v2_version=3)
        remove(mp4)
        remove(iconname)
    except Exception as e:
        print(e)

def wavconvtagger(webm,wav,song,path):
    try:
        convert=AudioSegment.from_file(webm)
        convert.export(wav,format='wav')
        remove(webm)
    except Exception as e:
        print(e)

def flacconvtagger(webm,flac,song,path):
    try:
        iconname=ospath.join(path,remove_sus_characters(song['artists'][0]['name']+'-'+song['name'])+'.jpg')
        request.urlretrieve(song['album']['images'][0]['url'],iconname)
        convert=AudioSegment.from_file(webm)
        convert.export(flac,format='flac')
        remove(webm)
        remove(iconname)
    except Exception as e:
        print(e)

def start(dlbut,scrltxt,progress,link:str,path:str,threadno:int,filetype:str,bitrate:str):
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
            t=Thread(target=download_song,args=(link,scrltxt,path,filetype,dlbut,progress,bitrate),daemon=False)
            t.start()
            threads.append(t)

    elif link.startswith('https://open.spotify.com/playlist/'):
        dlbut['state']='disabled'
        playlist=sp.playlist_tracks(link)
        name=sp.playlist(link)["name"]
        tracks=playlist['items']
        while playlist['next']:
            playlist=sp.next(playlist)
            tracks.extend(playlist['items'])
        progress['maximum']=len(tracks)
        add_text(scrltxt,'Downloading playlist \"{}\" with {} songs\n'.format(name,len(tracks)))
        lead=True
        for i in range(threadno):
            t=Thread(target=download_playlist,args=(tracks[i::threadno],scrltxt,path,filetype,lead,dlbut,progress,bitrate,False),daemon=False)
            t.start()
            if not lead:
                threads.append(t)
            else:
                leader.append(t)          
            lead=False

    elif link.startswith('https://open.spotify.com/album/'):
        dlbut['state']='disabled'
        playlist=sp.album(link)
        name=playlist['name']
        tracks=playlist['tracks']['items']
        progress['maximum']=len(tracks)
        for i in tracks:
            i['album']={'name':name,'artists':playlist['artists'],'release_date':playlist['release_date'],'images':playlist['images'],'total_tracks':playlist['total_tracks']}
        add_text(scrltxt,'Downloading album \"{}\" with {} songs\n'.format(name,len(tracks)))
        lead=True
        for i in range(threadno):
            t=Thread(target=download_playlist,args=(tracks[i::threadno],scrltxt,path,filetype,lead,dlbut,progress,bitrate,True),daemon=False)
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
    download_name=remove_sus_characters(song['artists'][0]['name']+'-'+song['name'])
    if not (ospath.exists(ospath.join(path,download_name+'.m4a')) or ospath.exists(ospath.join(path,download_name+'.mp3')) or ospath.exists(ospath.join(path,download_name+'.wav')) or ospath.exists(ospath.join(path,download_name+'.flac'))):
        try:
            data=checkdb(song['external_urls']['spotify'])
        except:
            data=None
            pass
        
        try:
            if data==None:
                try:
                    isrc_code=song['external_ids']['isrc'].replace('-','')
                    vid_id=ytm.search(isrc_code)
                    for i in vid_id:
                        spartists=[j['name'] for j in song['artists']]
                        ytartists=[x['name'] for x in i['artists']]
                        if any(char in spartists for char in ytartists) or song['name']==i['title'] :
                            vid_url = 'http://youtu.be/'+ i['videoId']
                            print('ISRC-',song['name'],i['title'])
                            break
                    vid=YouTube(vid_url)
                except:
                    results = YoutubeSearch(song['artists'][0]['name']+' '+song['name'], max_results=10).to_dict()
                    spsonglen = int(song['duration_ms']/1000)
                    vid=accusearch(results=results,songlen=spsonglen)
            else:
                vid=YouTube(data[0])
        except:
            vid=None

        if vid != None:
            download_name=remove_sus_characters(song['artists'][0]['name']+'-'+song['name'])
            mp4path=ospath.join(path,download_name+'.mp4')
            webmpath=ospath.join(path,download_name+'.webm')
            if filetype=='.m4a':
                try:
                    yt=vid.streams.get_audio_only()
                    yt.download(path,download_name+'.mp4')
                    m4apath=ospath.join(path,download_name+'.m4a')  
                    m4atagger(mp4path,m4apath,song,path)
                    add_text(scrltxt,'Finished downloading and converting {}\n'.format(song['name']))
                except Exception as e:
                    messagebox.showerror('Error','Oops program couldnt download {} because of {}'.format(song['name'],e))
                    print(e)
            if filetype=='.mp3':
                try:
                    yt=vid.streams.get_audio_only()
                    yt.download(path,download_name+'.mp4')
                    mp3path=ospath.join(path,download_name+'.mp3')
                    mp3convtagger(mp4path,mp3path,song,path)
                    add_text(scrltxt,'Finished downloading and converting {}\n'.format(song['name']))
                except Exception as e:
                    messagebox.showerror('Error','Oops program couldnt download {} because of {}'.format(song['name'],e))

            if filetype=='.wav':
                try:
                    yt=vid.streams.filter(mime_type='audio/webm').order_by('abr').desc().first()
                    yt.download(path,download_name+'.webm')
                    wavpath=ospath.join(path,download_name+'.wav')
                    wavconvtagger(webmpath,wavpath,song,path)
                except Exception as e:
                    messagebox.showerror('Error','Oops program couldnt download {} because of {}'.format(song['name'],e))

            if filetype=='.flac':
                try:
                    yt=vid.streams.filter(mime_type='audio/webm').order_by('abr').desc().first()
                    yt.download(path,download_name+'.webm')
                    flacpath=ospath.join(path,download_name+'.flac')
                    flacconvtagger(webmpath,flacpath,song,path)
                except Exception as e:
                    messagebox.showerror('Error','Oops program couldnt download {} because of {}'.format(song['name'],e))

            progress['value']=1
            button['state']='normal'
            messagebox.showinfo("Song has finished downloading","The song has finished downloading")
            progress['value']=0
        
        else:
            button['state']='normal'
            messagebox.showinfo("Song couldn't be downloaded","The program was not able to find the matching song on youtube \nContact the developers and provide them links to the song on spotify and youtube")        
            try:
                songnotfound(link)
            except:
                pass
    else:
        add_text(scrltxt,'Skipping download as {} already exists\n'.format(song['name']))
        progress['value']+=1

def download_playlist(tracks,scrltxt,path,filetype,leader,button,progress,album:bool):
    for i in tracks:
        if not album:
            song=i['track']
        else:
            song=i    
        download_name=remove_sus_characters(song['artists'][0]['name']+'-'+song['name'])
        if not (ospath.exists(ospath.join(path,download_name+'.m4a')) or ospath.exists(ospath.join(path,download_name+'.mp3')) or ospath.exists(ospath.join(path,download_name+'.wav')) or ospath.exists(ospath.join(path,download_name+'.flac'))):
            try:
                data=checkdb(song['external_urls']['spotify'])
            except:
                data=None
                pass
            
            try:
                if data==None:
                    try:
                        isrc_code=song['external_ids']['isrc'].replace('-','')
                        vid_id=ytm.search(isrc_code)
                        for i in vid_id:
                            spartists=[j['name'] for j in song['artists']]
                            ytartists=[x['name'] for x in i['artists']]
                            if any(char in spartists for char in ytartists) or song['name']==i['title'] :
                                vid_url = 'http://youtu.be/'+ i['videoId']
                                print('ISRC-',song['name'],i['title'])
                                break
                        vid=YouTube(vid_url)
                    except Exception as e:
                        results = YoutubeSearch(song['artists'][0]['name']+' '+song['name'], max_results=10).to_dict()
                        spsonglen = int(song['duration_ms']/1000)
                        vid=accusearch(results=results,songlen=spsonglen)
                else:
                    vid=YouTube(data[0])
            except:
                vid=None

            if vid != None:
                mp4path=ospath.join(path,download_name+'.mp4')
                webmpath=ospath.join(path,download_name+'.webm')
                if filetype=='.m4a':
                    try:
                        yt=vid.streams.get_audio_only()
                        yt.download(path,download_name+'.mp4')
                        m4apath=ospath.join(path,download_name+'.m4a')
                        m4atagger(mp4path,m4apath,song,path)
                        add_text(scrltxt,'Finished downloading and converting {}\n'.format(song['name']))
                    except Exception as e:
                        messagebox.showerror('Error','Oops program couldnt download {} because of {}'.format(song['name'],e))

                if filetype=='.mp3':
                    try:
                        yt=vid.streams.get_audio_only()
                        yt.download(path,download_name+'.mp4')
                        mp3path=ospath.join(path,download_name+'.mp3')
                        mp3convtagger(mp4path,mp3path,song,path)
                        add_text(scrltxt,'Finished downloading and converting {}\n'.format(song['name']))
                    except Exception as e:
                        messagebox.showerror('Error','Oops program couldnt download {} because of {}'.format(song['name'],e))

                if filetype=='.wav':
                    try:
                        yt=vid.streams.filter(mime_type='audio/webm').order_by('abr').desc().first()
                        yt.download(path,download_name+'.webm')
                        wavpath=ospath.join(path,download_name+'.wav')
                        wavconvtagger(webmpath,wavpath,song,path)
                    except Exception as e:
                        messagebox.showerror('Error','Oops program couldnt download {} because of {}'.format(song['name'],e))
        
                if filetype=='.flac':
                    try:
                        yt=vid.streams.filter(mime_type='audio/webm').order_by('abr').desc().first()
                        yt.download(path,download_name+'.webm')
                        flacpath=ospath.join(path,download_name+'.flac')
                        flacconvtagger(webmpath,flacpath,song,path)
                    except Exception as e:
                        messagebox.showerror('Error','Oops program couldnt download {} because of {}'.format(song['name'],e))

                progress['value']+=1
            else:
                add_text(scrltxt,'Couldn\'t find {} on yt report problem to devs\n'.format(song['name']))
                try:
                    logger('{}-{}\n'.format(song['name'],song['external_urls']['spotify']))
                    songnotfound(song['external_urls']['spotify'])
                except:
                    logger('{}\n'.format(song['name']))
                progress['value']+=1
        else:
            add_text(scrltxt,'Skipping download as {} already exists\n'.format(song['name']))
            progress['value']+=1
    if leader:
        global threads
        for i in threads:
            i.join()
        button['state']='normal'
        messagebox.showinfo("Songs have finished downloading","All the songs have finished downloading")
        progress['value']=0
