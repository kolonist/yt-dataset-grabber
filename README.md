# yt-dataset-grabber

Tool to grab voice datasets from Youtube.

# Description

This tool can help you to create and spread your voice datasets based on Youtube
video clips.

You should just fill JSON file with basic information and URL of video and then
this tool downloads, converts and saves audio files into hierarhial directory
structure.

# Installation

1. Install `Python` v3.10 or higher
2. Install `ffmpeg` binaries
3. Install `pyyaml`, `ffmpeg-python` and `yt_dlp` python packages
4. Clone this repository to your local directory

# Usage

1. Create directory where your dataset will be stored
2. Fill `params.yaml` according to its format specified below
3. Create `definition_file` according to its format specified
   below and store it in you dataset directory
4. Run grabber: `python grabber.py`
5. It starts to sownload files and store then in dataset folder

After grabber finishes work you will have the following directories
structure in your dataset folder:

```
src/    # source audio files downloaded from Youtube
    2mvFlVq9PYk.m4a
    KJHKJ45Kjhk.m4a
    7q-9PYkvFlV.m4a
    ...

id0001/    # folder with speaker 1 samples
    2023/  # samples of session with year 2023
        00001.wav  # there is only one fragment in this session
    2024/
        00001.wav  # concatenation of all fragments of this session
        00002.wav  # fragments of the session with year 2024
        00003.wav  # fragments numeration started from 2
        ...
id00002/
    ...
...

dataset.csv    # information about every wav file in the dataset
```

After your dataset created you may want to create verification
protocol like _VoiceCeleb's_ one.

`python verification.py` can create 3 verification protools in your
dataset directory. Created protocols have target hypothesys with
1-year, 2-years and 3-years difference in one speaker sessions
(if there are such sessions) and impostor hypothesys in different
speakers.

Example of such verification protocol for 1-year difference below:

```
0 id00058/2014/00001.wav id00034/2021/00001.wav
1 id00043/2022/00001.wav id00043/2021/00001.wav
0 id00055/2022/00001.wav id00045/2020/00001.wav
1 id00037/2019/00001.wav id00037/2020/00001.wav
...
```

Produced wave files are mono, PCM, 16000 Hz sampling rate.

## `params.yaml`

File contains the following fields:

### `dataset_path: str`

Path where your dataset should be stored.

### `definition_file: str`

Filename of JSON with dataset description. This file should be stored
in `dataset_path`.

### `first_id: int`

Number of first voice ID in your dataset. Voice IDs numerated as
`id00042`, `id00043`, ..., `id02342`. \
`42` is the value of `first_id`, \
`2300` is the number of voices in dataset.

Can be helpful if you create only a part of large dataset to
merge it with another parts later.

### Example:

```yaml
dataset_path: ../dataset
definition_file: dataset_src.json
first_id: 1
```

## Dataset definition file

This is the file you shoud create manually before you start grabbing
your dataset.

It should be stored in dataset directory and its name should be
specified in the `dataset_path` field of `params.yaml`.

Dataset definition file is JSON document with the following structure:

```json
[
    // first speaker
    {
        "name": "Name of speaker (or chanel, or whatever you want)",
        "sex": "gender of speaker",
        "birthdate": "1999-12-31",
        "lang": "english",

        // list of sessions with this speaker - one session per year
        "sessions": [
            // first session
            {
                "year": "2023",  // year of video recording

                // ID of video - part of URL after `/watch?v=`
                // for example, if URL is
                // `https://www.youtube.com/watch?v=TV_HmS73t-I` then
                // `url` should be the following:
                "url": "TV_HmS73t-I",

                // time of fragment start and end according to Youtube
                // videoclip timeline
                // you could define several fragments of one video
                "timestamps": [
                    // first fragment
                    {
                        // format is hh:mm:ss
                        "start": "4", // 4 seconds
                        "end": "8:0"  // 8 minutes
                    },

                    // second fragment
                    {
                        "start": "15", // 15 seconds
                        "end": "16:2"  // 16 minutes 2 seconds
                    },
                ]
            },

            // second session
            {
                "year": "2022",
                "url": "iBg_SN0EBEM",
                "timestamps": [
                    {
                        // 4 hours 8 minutes 15 seconds
                        "start": "4:8:15",

                        // 16 hours 23 minutes 42 seconds
                        "end": "16:23:42"
                    }
                ]
            },
        ]
    },

    // second speaker
    {
        "name": "John Doe",
        "sex": "male",
        "birthdate": "2000-01-01",
        "lang": "english",
        "sessions": [
            {
                "year": "2023",
                "url": "idMtiqFnv5I",
                "timestamps": [
                    {
                        "start": "7:30",
                        "end": "9:30"
                    }
                ]
            },
            {
                "year": "2022",
                "url": "3_JrH-gtTBE",
                "timestamps": [
                    {
                        "start": "1:10",
                        "end": "2:10"
                    }
                ]
            },
            {
                "year": "2021",
                "url": "yRCXRWVVPso",
                "timestamps": [
                    {
                        "start": "1:0",
                        "end": "3:0"
                    }
                ]
            }
        ]
    }
]
```


@license MIT \
@version 0.0.1 \
@author Alexander Zubakov <developer@xinit.ru>
