import re

def format_timestamp(seconds: float, always_include_hours: bool = True, fractionalSeperator: str = ','):
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

input = "F:\\Video\\YouTube\\Japanese\\Haru\\speakers.txt"

# Example line start=3.8s stop=41.4s speaker_SPEAKER_01

# Convert to SRT
# 1
# 00:00:03,800 --> 00:00:41,400
# speaker_SPEAKER_01

line_regex = r"start=(?P<start>\d+(?:\.\d+)?)s\s+stop=(?P<stop>\d+(?:\.\d+)?)s\s+(?P<text>.*)"
result = []

with open(input, "r") as f:
    for line in f:
        line = line.strip()
        
        match = re.match(line_regex, line)

        if match is None:
            continue

        start = match.group("start")
        stop = match.group("stop")
        text = match.group("text")
        
        result.append({
            "start": float(start),
            "stop": float(stop),
            "text": text
        })

with open("F:\\Video\\YouTube\\Japanese\\Haru\\speakers.srt", "w") as f:
    for i, item in enumerate(result):
        f.write(f"{i+1}\n")
        f.write(f"{format_timestamp(item['start'])} --> {format_timestamp(item['stop'])}\n")
        f.write(f"{item['text']}\n")
        f.write("\n")

