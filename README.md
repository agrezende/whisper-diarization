# Speaker Diarization with Whisper and Pyannote

This Python program takes an audio file and a Whisper JSON file as input from [Whisper-WebUI](https://gitlab.com/aadnk/whisper-webui), and performs speaker diarization on the audio file using the 
[pyannote/speaker-diarization](https://huggingface.co/pyannote/speaker-diarization) model. The speakers are added to the resulting Whisper JSON file in each segment, and the most likely speaker is added to the text in the SRT file.

## Installation

This project requires Python 3.8 or newer. You may also want to consider using a tool like Anaconda or Miniconda to manage the Python environment.

* Clone the repository:

    ```bash
    git clone https://gitlab.com/aadnk/whisper-diarization.git
    cd whisper-diarization
    ````

* Create a Python environment (optional):

    ```bash
    conda create -n whisper-diarization python=3.8
    conda activate whisper-diarization
    ```
* Install [GPU version of PyTorch (optional):](https://pytorch.org/get-started/locally/)

* Accept the user conditions on HuggingFace:

    *  visit hf.co/pyannote/speaker-diarization and accept user conditions
    *  visit hf.co/pyannote/segmentation and accept user conditions
    *  visit hf.co/settings/tokens to create an access token, which you can then supply to the program

* Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Program

Before running the program, you can set your HuggingFace API Token either via the HK_ACCESS_TOKEN environment variable or as a command line argument:

```bash
export HK_ACCESS_TOKEN=your-token-here  # Linux or macOS
set HK_ACCESS_TOKEN=your-token-here  # Windows
```
To run the program, use the following command:

```
usage: app.py [-h] [--output_json_file OUTPUT_JSON_FILE] [--output_srt_file OUTPUT_SRT_FILE] [--auth_token AUTH_TOKEN] [--max_line_width MAX_LINE_WIDTH] [--num_speakers NUM_SPEAKERS] [--min_speakers MIN_SPEAKERS] [--max_speakers MAX_SPEAKERS] audio_file whisper_file

Add speakers to a SRT file or Whisper JSON file using pyannote/speaker-diarization.

positional arguments:
  audio_file            Input audio file
  whisper_file          Input Whisper JSON/SRT file

options:
  -h, --help            show this help message and exit
  --output_json_file OUTPUT_JSON_FILE
                        Output JSON file (optional)
  --output_srt_file OUTPUT_SRT_FILE
                        Output SRT file (optional)
  --auth_token AUTH_TOKEN
                        HuggingFace API Token (optional)
  --max_line_width MAX_LINE_WIDTH
                        Maximum line width for SRT file (default: 40)
  --num_speakers NUM_SPEAKERS
                        Number of speakers
  --min_speakers MIN_SPEAKERS
                        Minimum number of speakers
  --max_speakers MAX_SPEAKERS
                        Maximum number of speakers
```
The `--output_file` and `--auth_token` arguments are optional. If not specified, the output file will be named after the input Whisper JSON file with _output added to the filename, and the auth token will be read from the HK_ACCESS_TOKEN environment variable.

For instance, if you have a file `audio.mp3` and a corresponding `audio.json` that was the result of running Whisper on the audio file (using [Whisper-WebUI](https://gitlab.com/aadnk/whisper-webui)), you can run the program as follows:

```bash
python app.py audio.mp3 audio.json
```
This will produce a file `audio_output.json` with the speaker labels added to the JSON file, and a file `audio_output.srt` with the speaker labels added to the segment text.

Each segment in the JSON file with have the fields `longest_speaker` and `speakers`, 
while the speaker will be prefixed in the SRT file.

## Example

Example input Whisper JSON:
```json
{
    "text": "...",
    "segments": [
        {
            "text": "だけどもあまり15%超えない方がいいですよ、知らない単語は。",
            "start": 0.0,
            "end": 4.0,
            "words": []
        },
        {
            "text": "20カ国語を話すことができる スティーブさんにインタビューしたことがありました",
            "start": 10.608,
            "end": 16.288,
            "words": []
        },
        // ...
    ],
    "language": "ja",
}
```
Program output:
```
$ python app.py audio.mp3 audio.json
Diarization result:
  start=0.5s stop=3.8s speaker_SPEAKER_00
  start=3.8s stop=41.4s speaker_SPEAKER_01
  start=42.9s stop=48.2s speaker_SPEAKER_01
...
```
Output SRT:
```srt
1
00:00:00,000 --> 00:00:04,000
(SPEAKER_00)
だけどもあまり15%超えない方がいいですよ、知らない単語は。

2
00:00:10,608 --> 00:00:16,288
(SPEAKER_01) 20カ国語を話すことができる
スティーブさんにインタビューしたことがありました
```
Output JSON:
```json
{
    "text": "...",
    "segments": [
        {
            "text": "だけどもあまり15%超えない方がいいですよ、知らない単語は。",
            "start": 0.0,
            "end": 4.0,
            "words": [],
            "longest_speaker": "SPEAKER_00",
            "speakers": [
                {
                    "start": 3.7546875,
                    "end": 41.4028125,
                    "speaker": "SPEAKER_01"
                },
                {
                    "start": 0.4978125,
                    "end": 3.7546875,
                    "speaker": "SPEAKER_00"
                }
            ]
        },
        {
            "text": "20カ国語を話すことができる スティーブさんにインタビューしたことがありました",
            "start": 10.608,
            "end": 16.288,
            "words": [],
            "longest_speaker": "SPEAKER_01",
            "speakers": [
                {
                    "start": 3.7546875,
                    "end": 41.4028125,
                    "speaker": "SPEAKER_01"
                }
            ]
        },
        // ...
    ],
    "language": "ja",
}
```

## Troubleshooting

If you encounter any issues while installing the dependencies or running the program, please open an issue in this repository or contact the author.

## License

This project is licensed under the terms of the Apache 2.0 license.