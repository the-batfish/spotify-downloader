from datetime import datetime
from os import path as ospath, remove, rename
from sys import exit
from threading import Thread
from tkinter import messagebox, Toplevel
from urllib import request

from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3, TALB, TIT2, TPE1, TPE2, TRCK, TYER
from mutagen.mp4 import MP4, MP4Cover
from mutagen.wave import WAVE
from mysql.connector import connect
from pydub import AudioSegment
from pytube import YouTube
from requests import get
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
from ytmusicapi import YTMusic

__version__ = "v1.67"
__supported_filetypes__ = (".m4a", ".mp3", ".wav", ".flac")

response = (
    get("https://api.github.com/repos/rickyrorton/spotify-downloader/releases/latest")
).json()
data = response["tag_name"]
if data.lower() != __version__.lower():
    ch = messagebox.askokcancel(
        "UPDATE APP",
        f"Press OK to update your app to the latest version {data} from the github repository",
    )
    if ch:
        from webbrowser import open_new_tab

        open_new_tab("https://github.com/rickyrorton/spotify-downloader/releases")
        exit()

ytm = YTMusic()


def checkdb(splink):
    db = connect(
        host="",
        user="",
        passwd="",
        database="",
    )
    cur = db.cursor(buffered=True)
    cur.execute(f'Select ytlink from songs where splink like"{splink}%"')
    data = cur.fetchone()
    cur.close()
    db.close()
    return data


def songnotfound(splink):
    db = connect(
        host="",
        user="",
        passwd="",
        database="",
    )
    cur = db.cursor(buffered=True)
    cur.execute(f'insert into notfound values("{splink}")')
    db.commit()
    cur.close()
    db.close()


client_credentials_manager = SpotifyClientCredentials(
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


def add_text(scrltxt_obj, text: str):
    scrltxt_obj.config(state="normal")
    scrltxt_obj.insert("insert", text)
    scrltxt_obj.see("end")
    scrltxt_obj.config(state="disabled")


def logger(text):
    with open("log.txt", "a") as f:
        f.write(text)


def accusearch(results, songlen):
    for i in results:
        try:
            time = datetime.strptime(i["duration"], "%M:%S")
            vid_length = time.minute * 60 + time.second
        except:
            time = datetime.strptime(i["duration"], "%H:%M:%S")
            vid_length = time.hour * 3600 + time.minute * 60 + time.second
        if vid_length >= songlen + 5 or vid_length <= songlen - 5:
            pass
        else:
            vid_url = "https://youtu.be" + i["url_suffix"].replace("watch?v=", "")
            break
    try:
        return YouTube(vid_url)
    except:
        return None


def m4atagger(mp4, m4a, song, path):
    rename(mp4, m4a)
    iconname = ospath.join(
        path,
        remove_sus_characters(song["artists"][0]["name"] + "-" + song["name"]) + ".jpg",
    )
    request.urlretrieve(song["album"]["images"][0]["url"], iconname)
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


def mp3convtagger(mp4, mp3, song, path, bitrate):
    iconname = ospath.join(
        path,
        remove_sus_characters(song["artists"][0]["name"] + "-" + song["name"]) + ".jpg",
    )
    request.urlretrieve(song["album"]["images"][0]["url"], iconname)
    convert = AudioSegment.from_file(mp4)
    convert.export(mp3, format="mp3", bitrate=bitrate)
    tags = ID3(mp3)
    tags.add(TIT2(encoding=3, text=[song["name"]]))
    tags.add(TALB(encoding=3, text=[song["album"]["name"]]))
    tags.add(TPE1(encoding=3, text=[i["name"] for i in song["artists"]]))
    tags.add(TPE2(encoding=3, text=[i["name"] for i in song["album"]["artists"]]))
    tags.add(TYER(encoding=3, text=[song["album"]["release_date"][0:4]]))
    tags.add(TRCK(encoding=3, text=[song["track_number"]]))
    with open(iconname, "rb") as f:
        tags.add(
            APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=f.read())
        )
    tags.save(v2_version=3)
    remove(mp4)
    remove(iconname)


def wavconvtagger(webm, wav, song, path, bitrate):
    iconname = ospath.join(
        path,
        remove_sus_characters(song["artists"][0]["name"] + "-" + song["name"]) + ".jpg",
    )
    request.urlretrieve(song["album"]["images"][0]["url"], iconname)
    convert = AudioSegment.from_file(webm)
    convert.export(wav, format="wav", bitrate=bitrate)
    tags = WAVE(wav)
    tags.add_tags()
    tags = tags.tags
    tags.add(TIT2(encoding=3, text=[song["name"]]))
    tags.add(TALB(encoding=3, text=[song["album"]["name"]]))
    tags.add(TPE1(encoding=3, text=[i["name"] for i in song["artists"]]))
    tags.add(TPE2(encoding=3, text=[i["name"] for i in song["album"]["artists"]]))
    tags.add(TYER(encoding=3, text=[song["album"]["release_date"][0:4]]))
    tags.add(TRCK(encoding=3, text=[song["track_number"]]))
    with open(iconname, "rb") as f:
        tags.add(
            APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=f.read())
        )
    tags.save(wav, v2_version=3)
    remove(webm)
    remove(iconname)


def flacconvtagger(webm, flac, song, path, bitrate):
    iconname = ospath.join(
        path,
        remove_sus_characters(song["artists"][0]["name"] + "-" + song["name"]) + ".jpg",
    )
    request.urlretrieve(song["album"]["images"][0]["url"], iconname)
    convert = AudioSegment.from_file(webm)
    convert.export(flac, format="flac", bitrate=bitrate)
    tags = FLAC(flac)
    tags["TITLE"] = song["name"]
    tags["ARTIST"] = ", ".join([i["name"] for i in song["artists"]])
    tags["ALBUMARTIST"] = ", ".join([i["name"] for i in song["album"]["artists"]])
    tags["ALBUM"] = song["album"]["name"]
    tags["DATE"] = song["album"]["release_date"][0:4]
    tags["TRACKNUMBER"] = str(song["track_number"])
    image = Picture()
    image.type = 3
    image.desc = "front cover"
    with open(iconname, "rb") as f:
        image.data = f.read()
    tags.add_picture(image)
    tags.save()
    remove(webm)
    remove(iconname)


def start(
    dlbut,
    scrltxt,
    progress,
    link: str,
    path: str,
    threadno: int,
    filetype: str,
    bitrate: str,
):
    global threads
    global leader
    scrltxt.config(state="normal")
    scrltxt.delete(1.0, "end")
    scrltxt.config(state="disabled")
    try:
        for t in threads:
            t.join()
        for t in leader:
            t.join()
    except:
        pass
    threads = []
    leader = []

    if link.startswith("https://open.spotify.com/track"):
        dlbut["state"] = "disabled"
        progress["maximum"] = 1
        for i in range(1):
            t = Thread(
                target=download_song,
                args=(
                    link,
                    scrltxt,
                    path,
                    filetype,
                    dlbut,
                    progress,
                    bitrate,
                    "Single",
                ),
                daemon=False,
            )
            t.start()
            threads.append(t)

    elif link.startswith("https://open.spotify.com/playlist/"):
        dlbut["state"] = "disabled"
        playlist = sp.playlist_tracks(link)
        name = sp.playlist(link)["name"]
        tracks = playlist["items"]
        while playlist["next"]:
            playlist = sp.next(playlist)
            tracks.extend(playlist["items"])
        progress["maximum"] = len(tracks)
        add_text(scrltxt, f'Downloading playlist "{name}" with {len(tracks)} songs\n')
        lead = True
        for i in range(threadno):
            t = Thread(
                target=download_playlist,
                args=(
                    tracks[i::threadno],
                    scrltxt,
                    path,
                    filetype,
                    lead,
                    dlbut,
                    progress,
                    bitrate,
                ),
                daemon=False,
            )
            t.start()
            if not lead:
                threads.append(t)
            else:
                leader.append(t)
            lead = False

    elif link.startswith("https://open.spotify.com/album/"):
        dlbut["state"] = "disabled"
        playlist = sp.album(link)
        name = playlist["name"]
        tracks = playlist["tracks"]["items"]
        progress["maximum"] = len(tracks)
        for i in tracks:
            tracks[tracks.index(i)] = sp.track(i["external_urls"]["spotify"])
        add_text(scrltxt, f'Downloading album "{name}" with {len(tracks)} songs\n')
        lead = True
        for i in range(threadno):
            t = Thread(
                target=download_playlist,
                args=(
                    tracks[i::threadno],
                    scrltxt,
                    path,
                    filetype,
                    lead,
                    dlbut,
                    progress,
                    bitrate,
                ),
                daemon=False,
            )
            t.start()
            if not lead:
                threads.append(t)
            else:
                leader.append(t)
            lead = False

    elif link == None:
        messagebox.showerror(
            "No link given",
            "You have not given a link, try again but this time dont forget to give a link",
        )
    else:
        messagebox.showerror(
            "Invalid link",
            "You have given an invalid link,try again this time but with a correct link",
        )


def get_ytVid(song):
    try:
        data = checkdb(song["external_urls"]["spotify"])
    except:
        data = None

    try:
        if data == None:
            try:
                isrc_code = song["external_ids"]["isrc"].replace("-", "")
                vid_id = ytm.search(isrc_code)
                if len(vid_id) == 0:
                    vid_id = ytm.search(
                        song["artists"][0]["name"] + " " + song["name"],
                        filter="songs",
                    )
                for i in vid_id:
                    spartists = [j["name"].lower() for j in song["artists"]]
                    ytartists = [x["name"].lower() for x in i["artists"]]
                    spname = "".join(
                        i
                        for i in song["name"].lower()
                        if i not in ["-", "(", ")", " ", "/", "\\", ","]
                    )
                    ytname = "".join(
                        i
                        for i in i["title"].lower()
                        if i not in ["-", "(", ")", " ", "/", "\\", ","]
                    )
                    if any(char in spartists for char in ytartists) and (
                        spname in ytname or ytname in spname
                    ):
                        vid_url = "https://youtu.be/" + i["videoId"]
                        vid = YouTube(vid_url)
                        break
                    else:
                        vid = None
            except:
                vid = None

            if vid == None:
                results = YoutubeSearch(
                    song["artists"][0]["name"] + " " + song["name"],
                    max_results=10,
                ).to_dict()
                spsonglen = int(song["duration_ms"] / 1000)
                vid = accusearch(results=results, songlen=spsonglen)
        else:
            vid = YouTube(data[0])
        return vid
    except:
        return None


def download_song(link, scrltxt, path, filetype, button, progress, bitrate, mode):
    song = sp.track(link) if mode == "Single" else link
    download_name = remove_sus_characters(
        song["artists"][0]["name"] + "-" + song["name"]
    )

    if not (
        any(
            ospath.exists(ospath.join(path, download_name + i))
            for i in __supported_filetypes__
        )
    ):
        add_text(
            scrltxt,
            f'Starting download of song - {song["name"]}\n',
        )
        vid = get_ytVid(song)
        if vid:
            mp4path = ospath.join(path, download_name + ".mp4")
            webmpath = ospath.join(path, download_name + ".webm")
            try:
                match filetype:
                    case ".m4a":
                        yt = vid.streams.get_audio_only()
                        yt.download(path, download_name + ".mp4")
                        m4apath = ospath.join(path, download_name + ".m4a")
                        m4atagger(mp4path, m4apath, song, path)
                        add_text(
                            scrltxt,
                            f"Finished downloading and converting {song['name']}\n",
                        )

                    case ".mp3":
                        yt = vid.streams.get_audio_only()
                        yt.download(path, download_name + ".mp4")
                        mp3path = ospath.join(path, download_name + ".mp3")
                        mp3convtagger(mp4path, mp3path, song, path, bitrate)
                        add_text(
                            scrltxt,
                            f"Finished downloading and converting {song['name']}\n",
                        )

                    case ".wav":
                        yt = (
                            vid.streams.filter(mime_type="audio/webm")
                            .order_by("abr")
                            .desc()
                            .first()
                        )
                        yt.download(path, download_name + ".webm")
                        wavpath = ospath.join(path, download_name + ".wav")
                        wavconvtagger(webmpath, wavpath, song, path, bitrate)
                        add_text(
                            scrltxt,
                            f"Finished downloading and converting {song['name']}\n",
                        )

                    case ".flac":
                        yt = (
                            vid.streams.filter(mime_type="audio/webm")
                            .order_by("abr")
                            .desc()
                            .first()
                        )
                        yt.download(path, download_name + ".webm")
                        flacpath = ospath.join(path, download_name + ".flac")
                        flacconvtagger(webmpath, flacpath, song, path, bitrate)
                        add_text(
                            scrltxt,
                            f"Finished downloading and converting {song['name']}\n",
                        )

                progress["value"] += 1

                if mode == "Single":
                    button["state"] = "normal"
                    messagebox.showinfo(
                        "Song has finished downloading",
                        "The song has finished downloading",
                    )
                    progress["value"] = 0

            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Oops program couldnt download {song['name']} because of {e}",
                )
        else:
            add_text(
                scrltxt,
                f"Couldn't find {song['name']} on youtube report problem to devs\n",
            )
            progress["value"] += 1
            if mode == "Single":
                messagebox.showinfo(
                    "Song couldn't be downloaded",
                    "The program was not able to find the matching song on youtube \nContact the developers and provide them links to the song on spotify and youtube",
                )
            try:
                logger(f"{song['name']}-{song['external_urls']['spotify']}")
                songnotfound(link)
            except:
                try:
                    logger(f"{song['name']}\n")
                except:
                    pass
    elif mode == "Single":
        button["state"] = "normal"
        messagebox.showinfo(
            "Skipping download",
            f"Skipping download as song - {song['name']} already exists",
        )
    else:
        add_text(
            scrltxt, f"Skipping download as song - {song['name']} already exists\n"
        )
        progress["value"] += 1


def download_playlist(
    tracks, scrltxt, path, filetype, leader, button, progress, bitrate
):
    for i in tracks:
        try:
            song = i["track"]
        except KeyError:  # Keyerror happens when albums are being download so this try except loop is necessary do not remove
            song = i
        download_song(
            song, scrltxt, path, filetype, button, progress, bitrate, "Multiple"
        )

    if leader:
        global threads
        for i in threads:
            i.join()
        button["state"] = "normal"
        progress["value"] = progress["maximum"]
        messagebox.showinfo(
            "Songs have finished downloading", "All the songs have finished downloading"
        )
        progress["value"] = 0


def downloadyt(link, filetype, res, location):
    pass


if __name__ == "__main__":
    # Checking for song (debugging?)
    vid = get_ytVid(sp.track(input("Enter Spotify Song Link: ")))
    print(f"Youtube Link: https://youtu.be/{vid.video_id}")
