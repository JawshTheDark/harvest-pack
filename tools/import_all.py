"""Imports every sheet in sheets/ (batch1.png ... batch5.png, or .webp/.jpg) using the icon order
in tools/sheets.json, then writes a numbered overview of each sheet to sheets/_check_<name>.png so
you can see which icon is which. Run from the harvest-pack folder."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHEETS = os.path.join(ROOT, "sheets")

mapping = json.load(open(os.path.join(HERE, "sheets.json")))
done = 0
for key, names in mapping.items():
    path = next((os.path.join(SHEETS, key + e) for e in (".png", ".webp", ".jpg", ".jpeg") if os.path.exists(os.path.join(SHEETS, key + e))), None)
    if not path:
        print("%s: no sheet yet" % key)
        continue
    print("== %s" % key)
    subprocess.run([sys.executable, os.path.join(HERE, "gemini_import.py"), path, "--names", names, "--debug", os.path.join(SHEETS, "_check_%s.png" % key)], check=True)
    done += 1
print("%d sheets imported; %d icons in art/" % (done, len([f for f in os.listdir(os.path.join(ROOT, "art")) if f.endswith(".png")])))
