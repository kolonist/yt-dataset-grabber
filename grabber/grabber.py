import os

from typing import NoReturn, Iterable, Any

from yaml import load as load_yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from json import load as load_json
from yt_dlp import YoutubeDL

import ffmpeg
import csv


def grab_dataset(params:dict[str,str], definition:Iterable[dict[str,Any]]) -> list[dict[str:str]]:
    rootdir = params["dataset_path"]

    dataset = []

    id = params["first_id"]

    for dictor in definition:
        for session in dictor["sessions"]:
            filename = download(rootdir, session["url"])

            dest_dir = os.path.join(
                rootdir,
                f"id{id:05d}",
                session["year"],
            )
            if not os.path.isdir(dest_dir):
                os.makedirs(dest_dir)

            convert(filename, session["timestamps"], dest_dir)

            # save info to dataset file
            file_num = 1 if len(session["timestamps"]) == 1 else 2

            for timestamp in session["timestamps"]:
                dataset.append({
                    "id": f"id{id:05d}",

                    "name"     : dictor["name"],
                    "sex"      : dictor["sex"],
                    "birthdate": dictor["birthdate"],
                    "lang"     : dictor["lang"],

                    "year" : session["year"],
                    "url"  : session["url"],

                    "file": f"{file_num:05d}.wav",

                    "start": parse_time(timestamp["start"]),
                    "end"  : parse_time(timestamp["end"]),
                })

                file_num += 1

            if file_num > 2:
                dataset.append({
                    "id": f"id{id:05d}",

                    "name"     : dictor["name"],
                    "sex"      : dictor["sex"],
                    "birthdate": dictor["birthdate"],
                    "lang"     : dictor["lang"],

                    "year" : session["year"],
                    "url"  : session["url"],

                    "file": f"00001.wav",

                    "start": "",
                    "end"  : "",
                })

        id += 1

    return dataset

def download(rootdir, id:str) -> str:
    src = f"https://www.youtube.com/watch?v={id}"

    rootdir = os.path.join(rootdir, "src")
    if not os.path.isdir(rootdir):
        os.makedirs(rootdir)

    saved_filename = [""]
    def hook(d):
        if d["status"] == "finished":
            saved_filename[0] = d["filename"]

    options = {
        "format": "m4a/bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
        }],
        "paths": {
            "home": rootdir
        },
        "outtmpl": {
            "default": f"{id}.%(ext)s"
        },
        "progress_hooks": [ hook ],
    }
    with YoutubeDL(options) as ydl:
        ydl.download(src)

    return saved_filename[0]

def convert(filename:str, timestamps:Iterable[dict[str,str]], dest_dir:str) -> NoReturn:
    file_id = 1 if len(timestamps) == 1 else 2

    files = []
    for timestamp in timestamps:
        start = parse_time(timestamp["start"])
        end = parse_time(timestamp["end"])

        dest_file = os.path.join(
            dest_dir,
            f"{file_id:05d}.wav"
        )

        print(f"{start} -> {end}")
        ffmpeg \
            .input(filename) \
            .audio \
            .output(
                dest_file,
                format="wav",
                acodec="pcm_s16le",
                ar=16000,
                ac=1,
                ss=start,
                to=end,
            ) \
            .overwrite_output() \
            .run(capture_stdout=False, quiet=True)

        file_id += 1
        files.append(dest_file)

    # concatenate files
    if len(files) > 1:
        streams = [ ffmpeg.input(file) for file in files ]

        concated_file = os.path.join(dest_dir, "00001.wav")
        ffmpeg \
            .concat(*streams, v=0, a=1) \
            .output(concated_file) \
            .overwrite_output() \
            .run(capture_stdout=False, quiet=True)

def parse_time(time:str) -> str:
    parts = [ f"{int(part):02d}" for part in time.split(":") ]

    while len(parts) < 3:
        parts = [ "00", *parts ]

    return ":".join(parts)


if __name__ == "__main__":
    # load parameters
    with open("params.yaml", "r") as f:
        params = load_yaml(f, Loader=Loader)

    # define paths
    rootdir = params["dataset_path"]
    definition_file_path = os.path.join(rootdir, params["definition_file"])

    # load dataset definition JSON
    with open(definition_file_path, "r") as f:
        definition = load_json(f)

    dataset = grab_dataset(params, definition)

    # save csv
    dataset_file = os.path.join(rootdir, "dataset.csv")

    fieldnames = list(dataset[0].keys())

    with open(dataset_file, "w", encoding="UTF8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataset)
