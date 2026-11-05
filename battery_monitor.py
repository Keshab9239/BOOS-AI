import subprocess
import json
import time
import os

STATE = os.path.expanduser("~/BOOS/battery_state.json")

def speak(message):
    subprocess.run(
        ["termux-tts-speak", "-l", "hi", message],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def battery():
    try:
        result = subprocess.run(
            ["termux-battery-status"],
            capture_output=True, text=True, timeout=15
        )
        return json.loads(result.stdout)
    except Exception:
        return {}

try:
    with open(STATE) as f:
        old = json.load(f)
except Exception:
    old = {}

while True:
    b = battery()

    if b:
        level = int(b.get("percentage", 0))
        plugged = b.get("plugged", "UNPLUGGED")

        if level < 20 and not old.get("low_alert", False):
            speak("Sir, aapke mobile ki battery low hai. Please charger laga lijiye.")
            old["low_alert"] = True

        if level >= 20:
            old["low_alert"] = False

        if plugged != old.get("plugged"):
            if plugged != "UNPLUGGED":
                speak("Sir, mobile charging shuru ho gayi hai.")
            elif old.get("plugged") != "UNKNOWN":
                speak("Sir, charger hata diya gaya hai.")
            old["plugged"] = plugged

        if level == 100 and not old.get("full_alert", False):
            speak("Sir, aapka mobile full charge ho gaya hai.")
            old["full_alert"] = True

        if level < 100:
            old["full_alert"] = False

        with open(STATE, "w") as f:
            json.dump(old, f)

    time.sleep(60)
