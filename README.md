# Speaker Diarization with Whisper and Pyannote

This Python program takes an audio file and a Whisper JSON file as input (from [Whisper-WebUI](https://gitlab.com/aadnk/whisper-webui)), performs speaker diarization on the audio file using the pyannote/audio library, and then adds speaker labels to the Whisper JSON file, both as a extra JSON field and as a prefix in the segment text.

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

```bash
python app.py /path/to/audio/file /path/to/whisper.json \
--output_json_file /path/to/output.json \
--output_srt_file /path/to/output.srt --auth_token your-token-here
```
The `--output_file` and `--auth_token` arguments are optional. If not specified, the output file will be named after the input Whisper JSON file with _output added to the filename, and the auth token will be read from the HK_ACCESS_TOKEN environment variable.

For instance, if you have a file `audio.mp3` and a corresponding `audio.json` that was the result of running Whisper on the audio file (using [Whisper-WebUI](https://gitlab.com/aadnk/whisper-webui)), you can run the program as follows:

```bash
python app.py audio.mp3 audio.json
```
This will produce a file `audio_output.json` with the speaker labels added to the JSON file, and a file `audio_output.srt` with the speaker labels added to the segment text.

## Troubleshooting

If you encounter any issues while installing the dependencies or running the program, please open an issue in this repository or contact the author.

## License

This project is licensed under the terms of the Apache 2.0 license.