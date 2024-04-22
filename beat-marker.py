#! /usr/bin/env python3

import os
import sys
import inspect
import pathlib

# GET RESOLVE

try:
    import DaVinciResolveScript as resolve

except ImportError:
    if sys.platform.startswith("darwin"):
        davinci_path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"

    elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
        import os
        davinci_path = os.getenv(
            'PROGRAMDATA') + "\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Modules\\"

    elif sys.platform.startswith("linux"):
        davinci_path = "/opt/resolve/Developer/Scripting/Modules/"

    else:
        davinci_path = ""

    try:
        from importlib.machinery import SourceFileLoader
        resolve = SourceFileLoader(
            "DaVinciResolveScript", davinci_path + "DaVinciResolveScript.py").load_module()

    except ImportError:
        sys.stdout.write("Could not recive scripting enviorment.")
        sys.exit()

resolve = resolve.scriptapp("Resolve")

if resolve == None:
    sys.stdout.write("Resolve is not opened.")
    sys.exit()

# CHECK IF TIMLINE IS OPEN

manager = resolve.GetProjectManager()
project = manager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

if timeline == None:
    sys.stdout.write("There is no timeline opened.")
    sys.exit()

# PHRASE ARGS

if len(sys.argv) == 1:
    import subprocess

    sourceFile = inspect.getfile(lambda: None)
    path = pathlib.Path(sourceFile)
    path = path.parent.absolute()

    print("Opening editor...")

    if sys.platform.startswith("darwin"):
        subprocess.Popen("open ./beat-marker_gui.app", cwd=path, shell=True)
    elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
        subprocess.Popen("beat-marker_gui.exe", cwd=path, shell=True)
    elif sys.platform.startswith("linux"):
        subprocess.Popen("./beat-marker_gui", cwd=path, shell=True)

    sys.exit()

if sys.argv[1] == "timeline":

    # PARSE TIMELINE ARGS

    if len(sys.argv) == 2:
        sys.stdout.write("Missing argument: timeline <bpm> [<offset>]")
        sys.exit()

    try:
        bpm = int(sys.argv[2])
    except:
        sys.stdout.write("Please specify a vaild bpm. (2nd arg)")
        sys.exit()

    try:
        offset = int(sys.argv[3])
    except:
        offset = 0

    # CALCULATE INTERVAL

    fps = project.GetSetting("timelineFrameRate")

    if bpm == 0:
        interval = 0
    else:
        interval = 60 * fps / bpm

    # CREATE TIMELINE MARKERS

    timeline.DeleteMarkersByColor("Sand")

    if interval == 0:
        sys.exit()

    start = offset
    end = timeline.GetEndFrame() - timeline.GetStartFrame()
    timestamp = start
    count = 1

    while timestamp < end:
        frame = round(timestamp + interval, ndigits=None)
        timeline.AddMarker(frame, "Sand", "Beat " + str(count), "", 1)
        timestamp += interval
        count += 1

elif sys.argv[1] == "clip":

    # PARSE CLIP ARGS

    if len(sys.argv) <= 3:
        sys.stdout.write(
            "Missing argument: timeline <audio-tack> <bpm> [<offset>]")
        sys.exit()

    try:
        track = int(sys.argv[2])

        if track > timeline.GetTrackCount("audio") or track < 1:
            raise Exception()

    except:
        sys.stdout.write("Please specify a vaild track. (2nd arg)")
        sys.exit()

    try:
        bpm = int(sys.argv[3])
    except:
        sys.stdout.write("Please specify a vaild bpm. (3rd arg)")
        sys.exit()

    try:
        offset = int(sys.argv[4])
    except:
        offset = 0

    # CALCULATE INTERVAL

    fps = round(project.GetSetting("timelineFrameRate"), ndigits=None)

    if bpm == 0:
        interval = 0
    else:
        interval = round(60 * fps / bpm)

    # CREATE MARKERS

    try:
        clip = timeline.GetItemListInTrack("audio", track)[0]
    except:
        sys.stdout.write("There is no audio clip on the track")
        sys.exit()

    clip.DeleteMarkersByColor("Sand")

    if interval == 0:
        sys.exit()

    start = offset
    end = clip.GetEnd() - clip.GetStart()
    count = 1

    for i in range(start, end, interval):
        clip.AddMarker(i, "Sand", "Beat " + str(count), "", 1)
        count += 1

else:
    sys.stdout.write("Please specify a vaild marker type. (1st arg)")
    sys.exit()
