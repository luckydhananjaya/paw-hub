"""Capture the signed Android app in a clean emulator using only sample notes."""
import re, subprocess, time, xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path("screenshots")
OUT.mkdir(exist_ok=True)

def adb(*args, binary=False):
    return subprocess.check_output(["adb", *args], text=not binary)

def tree():
    adb("shell", "uiautomator", "dump", "/sdcard/paw-ui.xml")
    xml = adb("shell", "cat", "/sdcard/paw-ui.xml")
    (OUT / "last-ui.xml").write_text(xml)
    return ET.fromstring(xml[xml.index("<?xml"):])

def find(label):
    for _ in range(20):
        doc = tree()
        for node in doc.iter("node"):
            if label in (node.get("text", ""), node.get("content-desc", "")):
                bounds = list(map(int, re.findall(r"\d+", node.get("bounds", ""))))
                if len(bounds) == 4 and bounds[2] > bounds[0] and bounds[3] > bounds[1]:
                    return bounds
        time.sleep(1)
    raise RuntimeError("UI element not found: " + label)

def tap(label):
    x1,y1,x2,y2 = find(label)
    adb("shell", "input", "tap", str((x1+x2)//2), str((y1+y2)//2))
    time.sleep(2)

def screenshot(name):
    (OUT / name).write_bytes(adb("exec-out", "screencap", "-p", binary=True))

adb("shell", "wm", "size", "1080x1920")
adb("shell", "wm", "density", "420")
adb("shell", "am", "start", "-n", "com.luckydhananjaya.pawnote/.MainActivity")
find("Grocery shopping")
time.sleep(3)
screenshot("01-notes-home.png")
tap("Grocery shopping")
find("Toggle checklist / text")
adb("shell", "input", "keyevent", "111")
time.sleep(1)
screenshot("02-note-editor.png")
tap("Toggle checklist / text")
time.sleep(1)
screenshot("03-checklist.png")
(OUT / "provenance.txt").write_text("Signed APK from workflow 41371956146; version 1.0.0 (1001). Clean API 35 emulator, 1080x1920, sample notes only. Screenshots captured using adb screencap; no raster edits.\n")
print("Captured three real Android screenshots.")
