from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube,Search
from ytmusicapi import YTMusic
from os import remove,getcwd
from os import path as ospath
from mutagen.mp4 import MP4, MP4Cover
from urllib import request
from pydub import AudioSegment

ytm=YTMusic()

client_credentials_manager = SpotifyClientCredentials( #Client credentials for spotify python api
    client_id="",
    client_secret="",
)
sp = Spotify(client_credentials_manager=client_credentials_manager)

def remove_sus_characters(name: str):
    converted = "".join(
        i
        for i in name
        if i
        not in ("/", "\\", "?", "%", "*", ":", "|", '"', "<", ">", ".", ",", ";", "=")
    )
    return converted

def searchytm(song,query):   
    vid_id=ytm.search(query)
    try:
        for i in vid_id:#to go thru list of returned results and check for result with matching artist
            spduration=int(song['duration_ms']/1000)
            if (i["duration_seconds"] in range(spduration-5,spduration+5)):#atleast one artist should be common to both and name should match
                vid_url = "https://youtu.be/" + i["videoId"]
                vid = YouTube(vid_url)
                return vid
    except Exception as e:
        return None        

def m4atagger(webm, m4a, song, path):
    convert = AudioSegment.from_file(webm)
    convert.export(m4a, format="mp4", bitrate='192k')
    remove(webm)
    icon_url= ''
    imax=0
    for i in song["album"]["images"]:
        if imax<i['height']:
            imax=i['height']
            icon_url=i['url']

    iconname = ospath.join(
        path,
        remove_sus_characters(song["artists"][0]["name"] + "-" + song["name"]) + ".jpg",
    )
    request.urlretrieve(icon_url, iconname)

    tags = MP4(m4a)
    if not tags.tags:
        tags.add_tags()
    tags["\xa9nam"] = song["name"]
    tags["\xa9alb"] = song["album"]["name"]
    tags["\xa9ART"] = ", ".join([i["name"] for i in song["artists"]])
    tags["aART"] = ", ".join([i["name"] for i in song["album"]["artists"]])
    tags["\xa9day"] = song["album"]["release_date"][0:4]
    tags["trkn"] = ((int(song["track_number"]), int(song["album"]["total_tracks"])),)

    with open(iconname, "rb") as f:
        tags["covr"] = [MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_JPEG)]
    tags.save()
    
    remove(iconname)

while True:
    link=input("Enter playlist link or type N to quit:")
    if link.lower()=='n':
        break
    else:
        playlist = sp.playlist_tracks(link)
        tracks = playlist["items"]
        while playlist["next"]:#loop to add remaining songs if playlist length>100
            playlist = sp.next(playlist)
            tracks.extend(playlist["items"])

        name = sp.playlist(link)["name"]
        print('Downloading playlist {} with {} songs'.format(name,len(tracks))) #show info to user

        for k in tracks:
            try:
                song = k["track"]
            except KeyError:  # Keyerror happens when albums are being download so this try except loop is necessary do not remove
                song = k

            isrc_code = str(song["external_ids"]["isrc"].replace("-", ""))
            vid=searchytm(song,isrc_code)
            
            if vid==None:#if isrc search doesnt give correct link
                query=song["artists"][0]["name"] + " " + song["name"]
                vid=searchytm(song,query)
                if vid==None:
                    query=song['name']
                    vid=searchytm(song,query)
            path=ospath.join(getcwd(),name)
            download_name = str(remove_sus_characters(song["artists"][0]["name"] + "-" + song["name"]))
            download_path=ospath.join(path,download_name)
            vid.streams.get_by_itag(251).download(path,download_name+'.webm')
            m4atagger(download_path+'.webm',download_path+'.m4a',song,path)