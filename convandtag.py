from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3, TALB, TIT2, TPE1, TPE2, TRCK, TYER
from mutagen.mp4 import MP4, MP4Cover
from mutagen.wave import WAVE
from pydub import AudioSegment
from os import path as ospath
from os import rename,remove
from urllib import request

def remove_sus_characters(name: str):
    converted = "".join(
        i
        for i in name
        if i
        not in ("/", "\\", "?", "%", "*", ":", "|", '"', "<", ">", ".", ",", ";", "=")
    )
    return converted

def m4atagger(input_file, m4a, song, path, bitrate, icon_url, conv):
    if not conv:
        rename(input_file, m4a)
    elif conv:
        convert = AudioSegment.from_file(input_file)
        convert.export(m4a, format="mp4", bitrate=bitrate)
        remove(input_file)
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


def mp3convtagger(webm, mp3, song, path, bitrate, icon_url):
    iconname = ospath.join(
        path,
        remove_sus_characters(song["artists"][0]["name"] + "-" + song["name"]) + ".jpg",
    )
    request.urlretrieve(icon_url, iconname)
    convert = AudioSegment.from_file(webm)
    convert.export(mp3, format="mp3", bitrate=bitrate)
    tags = ID3(mp3)
    tags.add(TIT2(encoding=3, text=[song["name"]]))
    tags.add(TALB(encoding=3, text=[song["album"]["name"]]))
    tags.add(TPE1(encoding=3, text=", ".join([i["name"] for i in song["artists"]])))
    tags.add(
        TPE2(encoding=3, text=", ".join([i["name"] for i in song["album"]["artists"]]))
    )
    tags.add(TYER(encoding=3, text=[song["album"]["release_date"][0:4]]))
    tags.add(TRCK(encoding=3, text=[song["track_number"]]))
    with open(iconname, "rb") as f:
        tags.add(
            APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=f.read())
        )
    tags.save(v2_version=3)
    remove(webm)
    remove(iconname)


def wavconvtagger(webm, wav, song, path, bitrate, icon_url):
    iconname = ospath.join(
        path,
        remove_sus_characters(song["artists"][0]["name"] + "-" + song["name"]) + ".jpg",
    )
    request.urlretrieve(icon_url, iconname)
    convert = AudioSegment.from_file(webm)
    convert.export(wav, format="wav", bitrate=bitrate)
    tags = WAVE(wav)
    tags.add_tags()
    tags = tags.tags
    tags.add(TIT2(encoding=3, text=[song["name"]]))
    tags.add(TALB(encoding=3, text=[song["album"]["name"]]))
    tags.add(TPE1(encoding=3, text=", ".join([i["name"] for i in song["artists"]])))
    tags.add(
        TPE2(encoding=3, text=", ".join([i["name"] for i in song["album"]["artists"]]))
    )
    tags.add(TYER(encoding=3, text=[song["album"]["release_date"][0:4]]))
    tags.add(TRCK(encoding=3, text=[song["track_number"]]))
    with open(iconname, "rb") as f:
        tags.add(
            APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=f.read())
        )
    tags.save(wav, v2_version=3)
    remove(webm)
    remove(iconname)


def flacconvtagger(webm, flac, song, path, bitrate, icon_url):
    iconname = ospath.join(
        path,
        remove_sus_characters(song["artists"][0]["name"] + "-" + song["name"]) + ".jpg",
    )
    request.urlretrieve(icon_url, iconname)
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
