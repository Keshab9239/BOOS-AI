import subprocess
import json
import time
import os
import urllib.parse
import datetime
import re

from google import genai

GEMINI_MODEL = "gemini-3.8-flash"

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

NAME = "BOOS"
SIR = "Sir"
DATA_FILE = os.path.expanduser("~/BOOS/boos_data.json")

def speak(text):
    print("\nBOOS:", text)
    subprocess.run(
        ["termux-tts-speak", "-l", "hi", text],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def run_cmd(command, timeout=15):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout.strip()
    except Exception:
        return ""

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"notes": [], "reminders": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def battery():
    raw = run_cmd(["termux-battery-status"])
    try:
        b = json.loads(raw)
        return b
    except Exception:
        return {}

def battery_info():
    b = battery()
    if not b:
        speak("Sir, battery ki information nahi mil rahi.")
        return

    speak(
        f"Sir, battery {b.get('percentage', 'unknown')} percent hai. "
        f"Status {b.get('status', 'unknown')} hai. "
        f"Temperature {b.get('temperature', 'unknown')} degree hai."
    )

def notifications():
    raw = run_cmd(["termux-notification-list"])
    try:
        items = json.loads(raw)
        if not items:
            speak("Sir, abhi koi notification nahi hai.")
            return

        speak(f"Sir, {len(items)} notifications mili hain.")
        count = 0
        for item in reversed(items):
            title = item.get("title", "")
            content = item.get("content", "")
            package = item.get("packageName", "")
            if title or content:
                speak(f"{title}. {content}")
                count += 1
            if count >= 5:
                break
        if count == 0:
            speak("Sir, notifications hain lekin unka message dikh nahi raha.")
    except Exception:
        speak("Sir, notification padhne mein dikkat aa rahi hai.")

def torch(state):
    result = run_cmd(["termux-torch", state])
    if state == "on":
        speak("Sir, torch on kar diya.")
    else:
        speak("Sir, torch off kar diya.")

def wifi_info():
    raw = run_cmd(["termux-wifi-connectioninfo"])
    try:
        w = json.loads(raw)
        ssid = w.get("ssid", "unknown")
        speak(f"Sir, Wi-Fi network {ssid} hai.")
    except Exception:
        speak("Sir, Wi-Fi ki information nahi mil rahi.")

def volume_info():
    raw = run_cmd(["termux-volume"])
    if raw:
        speak("Sir, volume ki information screen par dikhayi gayi hai.")
        print(raw)
    else:
        speak("Sir, volume information nahi mil rahi.")

def google_search(query):
    url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
    subprocess.Popen(["am", "start", "-a", "android.intent.action.VIEW", "-d", url])
    speak("Sir, Google par search khol diya.")

def youtube_search(query):
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
    subprocess.Popen(["am", "start", "-a", "android.intent.action.VIEW", "-d", url])
    speak("Sir, YouTube search khol diya.")

def open_app(app):
    apps = {
        "youtube": "com.google.android.youtube",
        "whatsapp": "com.whatsapp",
        "instagram": "com.instagram.android",
        "google": "com.google.android.googlequicksearchbox",
        "chrome": "com.android.chrome",
        "camera": "com.sec.android.app.camera",
        "settings": "com.android.settings"
    }
    package = apps.get(app)
    if not package:
        speak("Sir, is app ka naam abhi meri list mein nahi hai.")
        return
    result = run_cmd(["monkey", "-p", package, "-c",
                      "android.intent.category.LAUNCHER", "1"])
    speak(f"Sir, {app} kholne ki koshish kar raha hoon.")

def show_time():
    now = datetime.datetime.now()
    speak("Sir, abhi " + now.strftime("%I:%M %p") + " baj rahe hain.")

def show_date():
    now = datetime.datetime.now()
    speak("Sir, aaj " + now.strftime("%d %B %Y") + " hai.")

def add_note(text):
    data = load_data()
    data["notes"].append({
        "text": text,
        "time": datetime.datetime.now().isoformat()
    })
    save_data(data)
    speak("Sir, aapka note save kar diya.")

def read_notes():
    data = load_data()
    notes = data.get("notes", [])
    if not notes:
        speak("Sir, abhi koi note save nahi hai.")
        return
    speak(f"Sir, aapke {len(notes)} notes hain.")
    for note in notes[-5:]:
        speak(note["text"])

def add_reminder(text):
    data = load_data()
    data["reminders"].append({
        "text": text,
        "created": datetime.datetime.now().isoformat()
    })
    save_data(data)
    speak("Sir, reminder note kar liya. Abhi ye alarm notification nahi bhejega.")

def location_info():
    raw = run_cmd(["termux-location", "-p", "network"], timeout=25)
    if raw:
        try:
            loc = json.loads(raw)
            speak("Sir, location ki information mil gayi hai.")
            print(json.dumps(loc, indent=2))
        except Exception:
            speak("Sir, location information nahi padh pa raha.")
    else:
        speak("Sir, location nahi mil rahi. Permission check kijiye.")

def help_menu():
    speak(
        "Sir, aap mujhse battery, notification, torch on, torch off, "
        "Wi-Fi, volume, time, date, Google search, YouTube search, "
        "app kholo, note likho, notes sunao, reminder likho, "
        "location aur band hone ke liye keh sakte hain."
    )

AI_DATA_FILE = os.path.expanduser("~/BOOS/guru_memory.json")

MEMORY_FILE = os.path.expanduser("~/BOOS/guru_long_memory.json")

def load_memories():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_memory(item):
    memories = load_memories()

    if item and item not in memories:
        memories.append(item)

    with open(MEMORY_FILE, "w") as f:
        json.dump(memories[-100:], f, ensure_ascii=False, indent=2)

def show_memories():
    memories = load_memories()

    if memories:
        speak("Sir, mujhe ye baatein yaad hain:")
        for item in memories:
            speak(item)
    else:
        speak("Sir, abhi meri permanent memory khaali hai.")

def ai_chat(text):
    try:
        if not os.environ.get("GEMINI_API_KEY"):
            speak("Sir, Gemini API key available nahi hai.")
            return

        try:
            with open(AI_DATA_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            history = []

        prompt = (
            "Tum GURU ho, ek intelligent, friendly aur helpful AI assistant. "
            "User se Hindi aur Hinglish mein natural conversation karo. "
            "Pichhli baaton ka context samjho. Zarurat padne par khud bhi "
            "relevant questions poochho. User ko dost ki tarah samjho. "
            "Jawab simple aur natural rakho.\n\n"
        )

        for item in history[-10:]:
            prompt += f"User: {item['user']}\nGURU: {item['guru']}\n"

        prompt += f"User: {text}\nGURU:"

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        answer = response.text or "Sir, mujhe jawab nahi mil paaya."

        history.append({
            "user": text,
            "guru": answer
        })

        with open(AI_DATA_FILE, "w") as f:
            json.dump(history[-10:], f, ensure_ascii=False, indent=2)

        speak(answer)

    except Exception as e:
        print("AI Error:", str(e))
        speak("Sir, abhi AI se connection nahi ho pa raha.")

def handle(text):
    q = text.lower().strip()
    print("Aapne kaha:", text)

    if q.startswith("yaad rakhna"):
        item = text[len("yaad rakhna"):].strip()
        if item:
            save_memory(item)
            speak("Ji Sir, ye baat maine yaad rakh li.")
        else:
            speak("Sir, kya yaad rakhna hai?")
        return True

    if "meri memory" in q or "mujhe kya yaad hai" in q:
        show_memories()
        return True

    if not q:
        return True

    if any(x in q for x in ["band ho jao", "exit", "close", "so jao", "stop"]):
        speak("Ji Sir. BOOS ab band ho raha hai. Phir bulaiyega.")
        return False

    if "battery" in q or "बैटरी" in q or "charge" in q:
        battery_info()

    elif "notification" in q or "नोटिफिकेशन" in q:
        notifications()

    elif "torch on" in q or "flashlight on" in q or "टॉर्च चालू" in q:
        torch("on")

    elif "torch off" in q or "flashlight off" in q or "टॉर्च बंद" in q:
        torch("off")

    elif "wifi" in q or "वाईफाई" in q:
        wifi_info()

    elif "volume" in q or "आवाज" in q:
        volume_info()

    elif "time" in q or "समय" in q or "kitne baje" in q:
        show_time()

    elif "date" in q or "tarikh" in q or "तारीख" in q:
        show_date()

    elif "youtube" in q and ("search" in q or "ढूंढ" in q):
        query = re.sub(r".*youtube\s*(search)?", "", text, flags=re.I).strip()
        youtube_search(query or "YouTube")

    elif "google" in q and ("search" in q or "ढूंढ" in q):
        query = re.sub(r".*google\s*(search)?", "", text, flags=re.I).strip()
        google_search(query or "Google")

    elif "whatsapp kholo" in q or "open whatsapp" in q:
        open_app("whatsapp")

    elif "instagram kholo" in q or "open instagram" in q:
        open_app("instagram")

    elif "youtube kholo" in q or "open youtube" in q:
        open_app("youtube")

    elif "google kholo" in q or "open google" in q:
        open_app("google")

    elif "camera kholo" in q or "open camera" in q:
        open_app("camera")

    elif "settings kholo" in q or "open settings" in q:
        open_app("settings")

    elif q.startswith("note likho") or q.startswith("नोट लिखो"):
        note = re.sub(r"^(note likho|नोट लिखो)", "", text, flags=re.I).strip()
        if note:
            add_note(note)
        else:
            speak("Sir, note mein kya likhna hai?")

    elif "notes sunao" in q or "mere notes" in q:
        read_notes()

    elif q.startswith("reminder likho") or q.startswith("रिमाइंडर लिखो"):
        reminder = re.sub(r"^(reminder likho|रिमाइंडर लिखो)", "", text, flags=re.I).strip()
        if reminder:
            add_reminder(reminder)
        else:
            speak("Sir, reminder mein kya likhna hai?")

    elif "location" in q or "meri jagah" in q:
        location_info()

    elif "help" in q or "kya kar sakte" in q:
        help_menu()

    else:
      ai_chat(text)

    return True

def main():
    speak("Ji Sir! Main aapki seva mein hazir hoon. Main aapki kya madad kar sakta hoon?")
    speak("Aap apni command boliye. Pandrah second mein command na mili toh BOOS band ho jayega.")

    while True:
        print("\nBOOS sun raha hai...")

        try:
            result = subprocess.run(
                ["termux-speech-to-text"],
                capture_output=True,
                text=True,
                timeout=15
            )
            text = result.stdout.strip()
        except subprocess.TimeoutExpired:
            speak("Sir, aapki taraf se koi command nahi aayi. BOOS band ho raha hai.")
            break
        except KeyboardInterrupt:
            speak("Ji Sir, BOOS band ho raha hai.")
            break
        except Exception:
            speak("Sir, voice input mein dikkat aa rahi hai.")
            break

        if not text:
            speak("Sir, awaaz sunai nahi di. BOOS band ho raha hai.")
            break

        if not handle(text):
            break

        speak("Ji Sir, aur koi kaam?")

if __name__ == "__main__":
    main()
