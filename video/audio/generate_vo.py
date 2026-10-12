"""
Generates voiceover audio blocks V1 to V10 using edge-tts.
Strictly no em dashes. Voice: en-US-ChristopherNeural.
"""

import asyncio
import os
import json
import subprocess
from email.utils import parsedate_to_datetime
from datetime import timezone as tz

import edge_tts
import edge_tts.constants
import edge_tts.communicate
import edge_tts.drm

# Patch edge-tts WSS_URL for reliable synthesis without 403
NEW_WSS = (
    "wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1"
    f"?Ocp-Apim-Subscription-Key={edge_tts.constants.TRUSTED_CLIENT_TOKEN}"
)
edge_tts.constants.WSS_URL = NEW_WSS
edge_tts.communicate.WSS_URL = NEW_WSS

def _parse_date(date: str):
    try:
        p = parsedate_to_datetime(date)
    except Exception:
        return None
    if p.tzinfo is None:
        p = p.replace(tzinfo=tz.utc)
    return p.timestamp()

edge_tts.drm.DRM.parse_rfc2616_date = staticmethod(_parse_date)

VO_BLOCKS = [
    {
        "id": "v1",
        "scene": "s1",
        "window": "0:02.5 to 0:12",
        "text": "It is two in the morning. An AI agent is clearing a founder's refund queue, one customer at a time. At ticket seventy three, the process dies. Who got paid? Who is about to get paid twice?"
    },
    {
        "id": "v2",
        "scene": "s2",
        "window": "0:12.4 to 0:20",
        "text": "Maya runs a small software business on Dodo Payments. Every refund means find the customer, find the payment, check the policy, work out the amount, refund, reply. One mistake with money is permanent."
    },
    {
        "id": "v3",
        "scene": "s3",
        "window": "0:20.4 to 0:42",
        "text": "So before building, we broke the tracing on purpose. We killed a traced worker mid run, twelve ways. With a hard kill at the default flush interval, the trace kept zero spans. Faster flushing saved most steps, but never the last one, and never the root. A trace is weakest the moment an agent dies."
    },
    {
        "id": "v4",
        "scene": "s4",
        "window": "0:42.4 to 0:56",
        "text": "Then we tested the processor. The same refund, sent twice, was paid twice, even with an idempotency key. Retrying after a crash is how you refund a customer twice."
    },
    {
        "id": "v5",
        "scene": "s5",
        "window": "0:56.4 to 1:20",
        "text": "Purser is built around that moment. Gemini reads each ticket, calls the tools, and proposes. It never sets an amount. A deterministic kernel computes it from the founder's policy and checks twelve invariants. Every refund is written to a hash chained log before money moves, with its fingerprint embedded in the refund itself."
    },
    {
        "id": "v6",
        "scene": "s6",
        "window": "1:20.4 to 1:44",
        "text": "Here we kill it for real, right after Dodo accepts the refund and before Purser records it. On restart, Purser reads its log, asks Dodo what actually happened, finds its own fingerprint, and records the refund that already exists. No second payment. Then it files a witness statement, so the trace is whole again."
    },
    {
        "id": "v7",
        "scene": "s7",
        "window": "1:44.4 to 2:04",
        "text": "In the morning, the founder reads one report. Every refund is reconciled against Dodo's ledger before the batch can close. Anything above the limit, or anything suspicious, waits for one click. The agent can never approve itself."
    },
    {
        "id": "v8",
        "scene": "s8",
        "window": "2:04.4 to 2:24",
        "text": "neatlogs is how we found this, and how Purser checks its own testimony: one trace per ticket, each batch a session, and a witness statement for whatever a crash erased. Entire links every policy rule to the coding session where it was written, so a refund traces back to the founder's intent."
    },
    {
        "id": "v9",
        "scene": "s9",
        "window": "2:24.4 to 2:33",
        "text": "cfo.ai turns the measured cost per ticket into pricing, margin and runway."
    },
    {
        "id": "v10",
        "scene": "s10",
        "window": "2:33.6 to 2:38",
        "text": "Purser. The trace is a witness. The ledger is the judge."
    }
]

VOICE = "en-US-ChristopherNeural"
RATE = "-4%"

async def generate_voiceover():
    os.makedirs("video/audio", exist_ok=True)
    manifest = []
    durations = []
    print(f"Generating 10 voiceover blocks with edge-tts ({VOICE})...")

    for block in VO_BLOCKS:
        out_mp3 = f"video/audio/{block['id']}.mp3"
        out_wav = f"video/audio/{block['id']}.wav"
        
        communicate = edge_tts.Communicate(block["text"], VOICE, rate=RATE)
        await communicate.save(out_mp3)
        
        # Convert to 48kHz mono 24-bit PCM wav
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", out_mp3, "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le", out_wav],
            check=True
        )
        
        # Measure duration with ffprobe
        raw_dur = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out_wav]
        ).decode().strip()
        dur = float(raw_dur)
        words = len(block["text"].split())
        wpm = round(words / dur * 60)
        
        print(f"  {block['id']}: {words} words, {dur:.2f}s ({wpm} wpm)")
        
        manifest.append({
            "id": block["id"],
            "scene": block["scene"],
            "mp3": out_mp3,
            "wav": out_wav,
            "window": block["window"],
            "text": block["text"],
            "duration": dur,
            "words": words,
            "wpm": wpm
        })
        durations.append({
            "id": block["id"],
            "words": words,
            "dur": round(dur, 3)
        })

    with open("video/audio/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    with open("video/audio/durations.json", "w", encoding="utf-8") as f:
        json.dump({"voice": VOICE, "rate": RATE, "blocks": durations}, f, indent=2)

    print("\nAssembling full voiceover timeline...")
    # Calculate scene start times matching prompt windows
    # S1 start 2.5s
    # Each block gets exact start time
    schedule = {
        "v1": 2.5,
        "v2": 12.4,
        "v3": 20.4,
        "v4": 42.4,
        "v5": 56.4,
        "v6": 80.4,
        "v7": 104.4,
        "v8": 124.4,
        "v9": 144.4,
        "v10": 153.6
    }
    
    timeline = []
    current_time = 0.0
    for block in manifest:
        bid = block["id"]
        sched_start = schedule.get(bid, current_time + 0.4)
        if sched_start < current_time + 0.3:
            sched_start = current_time + 0.4
        b_dur = block["duration"]
        b_end = sched_start + b_dur
        current_time = b_end
        timeline.append({
            "id": bid,
            "scene": block["scene"],
            "start": round(sched_start, 3),
            "end": round(b_end, 3),
            "dur": round(b_dur, 3),
            "text": block["text"]
        })

    with open("video/audio/timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)

    total_time = 170.0 # 2:50 film
    print(f"Total audio timeline length: {timeline[-1]['end']:.2f}s (video total: {total_time}s)")

    # Build voiceover_full.wav with ffmpeg adelay and amix
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for t in timeline:
        cmd += ["-i", f"video/audio/{t['id']}.wav"]
    fl = []
    for i, t in enumerate(timeline):
        ms = int(round(t["start"] * 1000))
        fl.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]")
    inputs_str = "".join(f"[a{i}]" for i in range(len(timeline)))
    fl.append(
        f"{inputs_str}amix=inputs={len(timeline)}:normalize=0:duration=longest,"
        f"apad=whole_dur={total_time},atrim=0:{total_time},"
        f"loudnorm=I=-16:TP=-1.5:LRA=11[out]"
    )
    cmd += [
        "-filter_complex", ";".join(fl),
        "-map", "[out]",
        "-ar", "48000",
        "-ac", "1",
        "-c:a", "pcm_s24le",
        "video/audio/voiceover_full.wav"
    ]
    subprocess.run(cmd, check=True)
    print("Successfully built video/audio/voiceover_full.wav")

if __name__ == "__main__":
    asyncio.run(generate_voiceover())
