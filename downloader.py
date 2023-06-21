# fmt: off
from datetime import datetime
from os import getcwd
from os import path as ospath
from os import remove, rename, rmdir
from platform import system
from sys import exit
from threading import Thread
from tkinter import messagebox
from urllib import request
from zipfile import ZipFile
from requests import get

from convandtag import m4atagger,mp3convtagger,flacconvtagger,wavconvtagger,remove_sus_characters
from mysql.connector import connect
from pytube import YouTube
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
from ytmusicapi import YTMusic

# fmt: on

__version__ = "v1.7"
__supported_filetypes__ = (".m4a", ".mp3", ".wav", ".flac")


def checkversion():
    response = (
        get(
            "https://api.github.com/repos/rickyrorton/spotify-downloader/releases/latest"
        )
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
        '''elif __name__ != "__main__":
            exit()'''


t = Thread(target=checkversion())
t.start()
t.join()


def checkffmpeg():
    from pydub.utils import which

    if not (which("ffmpeg")):
        ch = messagebox.askokcancel(
            "FFMPEG NOT FOUND",
            f"Ffmpeg was not found, kindly download ffmpeg to use formats like mp3,flac and wav,press OK to download ffmpeg",
        )
        if ch:
            if system() == "Windows":
                response = (
                    get(
                        "https://api.github.com/repos/GyanD/codexffmpeg/releases/latest"
                    )
                ).json()
            assets = (get(response["assets_url"])).json()
            for i in assets:
                if "essentials" in i["name"] and "zip" in i["name"]:
                    request.urlretrieve(
                        i["browser_download_url"], ospath.join(getcwd(), "ffmpeg.zip")
                    )
                    break
            with ZipFile(ospath.join(getcwd(), "ffmpeg.zip")) as zip:
                files = zip.namelist()
                bin_folder = files[1]
                ffmpeg_folder = files[0]
                targets = []
                for i in files:
                    if (
                        i.endswith("bin/ffmpeg.exe")
                        or i.endswith("bin/ffplay.exe")
                        or i.endswith("bin/ffprobe.exe")
                    ):
                        targets.append(i)
                        zip.extract(i, getcwd())
                for i in targets:
                    rename(
                        ospath.join(getcwd(), i),
                        ospath.join(getcwd(), i.replace(bin_folder, "")),
                    )
            remove(ospath.join(getcwd(), "ffmpeg.zip"))
            rmdir(ospath.join(getcwd(), bin_folder))
            rmdir(ospath.join(getcwd(), ffmpeg_folder))


try:
    checkffmpeg()
except Exception as e:
    print("error", e)
    pass

ytm = YTMusic()

client_credentials_manager = SpotifyClientCredentials(
    client_id="",
    client_secret="",
)
sp = Spotify(client_credentials_manager=client_credentials_manager)


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
                    ospath.join(path,name),
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
                    ospath.join(path,name),
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

def searchytm(song, query):
    vid_id = ytm.search(query)
    try:
        for (
            i
        ) in (
            vid_id
        ):  # to go thru list of returned results and check for result with matching artist
            spduration = int(song["duration_ms"] / 1000)
            if i["duration_seconds"] in range(
                spduration - 5, spduration + 5
            ):  # atleast one artist should be common to both and name should match
                vid_url = "https://youtu.be/" + i["videoId"]
                vid = YouTube(vid_url)
                return vid
        return None
    except Exception as e:
        return None

def get_ytVid(song):
    isrc_code = str(song["external_ids"]["isrc"].replace("-", ""))
    vid = searchytm(song, isrc_code)

    if vid == None:  # if isrc search doesnt give correct link
        query = song["artists"][0]["name"] + " " + song["name"]
        vid = searchytm(song, query)
        if vid == None:
            query = song["name"]
            vid = searchytm(song, query)
    return vid

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
            webmpath = ospath.join(path, download_name + ".webm")
            icon_url = ""
            imax = 0
            for i in song["album"]["images"]:
                if imax < i["height"]:
                    imax = i["height"]
                    icon_url = i["url"]
            try:
                match filetype:
                    case ".m4a":
                        filetype = ".m4a"
                        yt = (
                            vid.streams.filter(mime_type="audio/webm")
                            .order_by("abr")
                            .desc()
                            .first()
                        )
                        yt.download(path, download_name + ".webm")
                        m4apath = ospath.join(path, download_name + ".m4a")
                        m4atagger(
                            webmpath, m4apath, song, path, bitrate, icon_url, True
                        )
                        add_text(
                            scrltxt,
                            f"Finished downloading and converting {song['name']}\n",
                        )

                    case ".mp3":
                        yt = (
                            vid.streams.filter(mime_type="audio/webm")
                            .order_by("abr")
                            .desc()
                            .first()
                        )
                        yt.download(path, download_name + ".webm")
                        mp3path = ospath.join(path, download_name + ".mp3")
                        mp3convtagger(webmpath, mp3path, song, path, bitrate, icon_url)
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
                        wavconvtagger(webmpath, wavpath, song, path, bitrate, icon_url)
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
                        flacconvtagger(
                            webmpath, flacpath, song, path, bitrate, icon_url
                        )
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
                if e.startswith(
                    "[WinError 2] The system cannot find the file specified"
                ):
                    messagebox.showerror(
                        "Error",
                        f"Oops, FFMPEG not found",
                    )

                else:
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
        except (
            KeyError
        ):  # Keyerror happens when albums are being download so this try except loop is necessary do not remove
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

if __name__ == "__main__":
    # Checking for song (debugging?)
    vid = get_ytVid(sp.track(input("Enter Spotify Song Link: ")))
    print(f"Youtube Link: https://youtu.be/{vid.video_id}")
