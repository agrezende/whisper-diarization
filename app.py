import argparse
import json
import os
from typing import List
import torch
from pyannote.audio import Pipeline

from intervaltree import IntervalTree
from util import write_srt

class DiarizationEntry:
    def __init__(self, start, end, speaker):
        self.start = start
        self.end = end
        self.speaker = speaker

    def __repr__(self):
        return f"<DiarizationEntry start={self.start} end={self.end} speaker={self.speaker}>"

class Diarization:
    def __init__(self, auth_token):
        if auth_token is None:
            raise ValueError("auth_token is required - use the HK_ACCESS_TOKEN or access_token parameter")
        
        self.auth_token = auth_token
        self.initialized = False
        self.pipeline = None

    def initialize(self):
        if self.initialized:
            return
        self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token=self.auth_token)

        # Load GPU mode if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cuda":
            self.pipeline = self.pipeline.to(torch.device(0))

    def run(self, audio_file):
        self.initialize()
        diarization = self.pipeline(audio_file)

        # Yield result
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            yield DiarizationEntry(turn.start, turn.end, speaker)
    
    def mark_speakers(self, diarization_result: List[DiarizationEntry], whisper_result: dict):
        result = whisper_result.copy()

        # Create an interval tree from the diarization results
        tree = IntervalTree()
        for entry in diarization_result:
            tree[entry.start:entry.end] = entry.speaker

        # Iterate through each segment in the Whisper JSON
        for segment in result["segments"]:
            segment_start = segment["start"]
            segment_end = segment["end"]

            # Find overlapping speakers using the interval tree
            overlapping_speakers = tree[segment_start:segment_end]

            # If no speakers overlap with this segment, skip it
            if not overlapping_speakers:
                continue

            # If multiple speakers overlap with this segment, choose the one with the longest duration
            longest_speaker = None
            longest_duration = 0
            
            for speaker_interval in overlapping_speakers:
                overlap_start = max(speaker_interval.begin, segment_start)
                overlap_end = min(speaker_interval.end, segment_end)
                overlap_duration = overlap_end - overlap_start

                if overlap_duration > longest_duration:
                    longest_speaker = speaker_interval.data
                    longest_duration = overlap_duration

            # Annotate the segment with the longest overlapping speaker ID
            segment["text"] = f"({longest_speaker}) {segment['text']}"

        return result

def _write_file(input_file: str, output_path: str, output_extension: str, file_writer: lambda f: None):
    if input_file is None:
        raise ValueError("input_file is required")
    if file_writer is None:
        raise ValueError("file_writer is required")

     # Write file
    if output_path is None:
        effective_path = os.path.splitext(input_file)[0] + "_output" + output_extension
    else:
        effective_path = output_path

    with open(effective_path, 'w+', encoding="utf-8") as f:
        file_writer(f)

    print(f"Output saved to {effective_path}")

def main():
    parser = argparse.ArgumentParser(description='Add speakers to a SRT file using Whisper and pyannote/speaker-diarization.')
    parser.add_argument('audio_file', type=str, help='Input audio file')
    parser.add_argument('whisper_file', type=str, help='Input Whisper JSON file')
    parser.add_argument('--output_json_file', type=str, default=None, help='Output JSON file (optional)')
    parser.add_argument('--output_srt_file', type=str, default=None, help='Output SRT file (optional)')
    parser.add_argument('--auth_token', type=str, default=None, help='HuggingFace API Token (optional)')
    parser.add_argument("--max_line_width", type=int, default=40, help="Maximum line width for SRT file (default: 40)")

    args = parser.parse_args()

    if args.auth_token is None:
        auth_token = os.environ.get("HK_ACCESS_TOKEN")
        if auth_token is None:
            raise ValueError("No HuggingFace API Token provided - please use the --auth_token argument or set the HK_ACCESS_TOKEN environment variable")
    else:
        auth_token = args.auth_token

    print("\nReading whisper JSON from " + args.whisper_file)

    # Read whisper JSON file
    with open(args.whisper_file, "r", encoding="utf-8") as f:
        whisper_result = json.load(f)

    diarization = Diarization(auth_token)
    diarization_result = list(diarization.run(args.audio_file))

    # Print result
    print("Diarization result:")
    for entry in diarization_result:
        print(f"  start={entry.start:.1f}s stop={entry.end:.1f}s speaker_{entry.speaker}")

    # Format of Whisper JSON file:
    #  {
    # "text": " And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.",
    # "segments": [
    #    {
    #        "text": " And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.",
    #        "start": 0.0,
    #        "end": 10.36,
    #        "words": [
    #            {
    #                "start": 0.0,
    #                "end": 0.56,
    #                "word": " And",
    #                "probability": 0.61767578125
    #            },
    #            {
    #                "start": 0.56,
    #                "end": 0.88,
    #                "word": " so",
    #                "probability": 0.9033203125
    #            },
    # etc.  

    marked_whisper_result = diarization.mark_speakers(diarization_result, whisper_result)

    # Write output JSON to file
    _write_file(args.whisper_file, args.output_json_file, ".json", 
                lambda f: json.dump(marked_whisper_result, f, indent=4, ensure_ascii=False))

    # Write SRT
    _write_file(args.whisper_file, args.output_srt_file, ".srt", 
                lambda f: write_srt(marked_whisper_result["segments"], f, maxLineWidth=args.max_line_width))

if __name__ == "__main__":
    main()