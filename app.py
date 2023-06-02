import os
import torch
from pyannote.audio import Pipeline

auth_token = os.getenv("HK_ACCESS_TOKEN")

if auth_token is None:
    raise ValueError("Please set the HK_ACCESS_TOKEN environment variable.")

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                    use_auth_token=auth_token)

# Load GPU mode if available
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    pipeline = pipeline.to(torch.device(0))

# apply the pipeline to an audio file
diarization = pipeline("F:\\Video\\YouTube\\Japanese\\Haru\\output.flac")

# dump the diarization output to disk using RTTM format
#with open("audio.rttm", "w") as rttm:
#    diarization.write_rttm(rttm)

# 5. print the result
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")