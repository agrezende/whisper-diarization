import textwrap
from typing import Iterator, TextIO

def write_srt(transcript: Iterator[dict], file: TextIO, maxLineWidth=None):
    """
    Write a transcript to a file in SRT format.
    Example usage:
        from pathlib import Path
        from whisper.utils import write_srt
        result = transcribe(model, audio_path, temperature=temperature, **args)
        # save SRT
        audio_basename = Path(audio_path).stem
        with open(Path(output_dir) / (audio_basename + ".srt"), "w", encoding="utf-8") as srt:
            write_srt(result["segments"], file=srt)
    """
    iterator  = __subtitle_preprocessor_iterator(transcript, maxLineWidth)

    for i, segment in enumerate(iterator, start=1):
        text = segment['text'].replace('-->', '->')

        # write srt lines
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True, fractionalSeperator=',')} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True, fractionalSeperator=',')}\n"
            f"{text}\n",
            file=file,
            flush=True,
        )

def __subtitle_preprocessor_iterator(transcript: Iterator[dict], maxLineWidth: int = None, highlight_words: bool = False): 
    for segment in transcript:
        text = segment['text']

        # Append longest speaker ID if available
        segment_longest_speaker = segment.get('longest_speaker', None)

        if segment_longest_speaker is not None:
            text = f"({segment_longest_speaker}) {text}"

        # Yield the segment as-is or processed
        if maxLineWidth is None or maxLineWidth < 0:
            yield segment
        else:
            yield {
                'start': segment['start'],
                'end': segment['end'],
                'text': process_text(text.strip(), maxLineWidth)
            }

def process_text(text: str, maxLineWidth=None):
    if (maxLineWidth is None or maxLineWidth < 0):
        return text

    lines = textwrap.wrap(text, width=maxLineWidth, tabsize=4)
    return '\n'.join(lines)

def format_timestamp(seconds: float, always_include_hours: bool = False, fractionalSeperator: str = '.'):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}{fractionalSeperator}{milliseconds:03d}"