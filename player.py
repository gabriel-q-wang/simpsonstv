import os
import random
import time
import RPi.GPIO as GPIO
from subprocess import PIPE, Popen, STDOUT

directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'videos/encoded')

videos = []

GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def skipCurrentVideo(counter):
    # Button assigned to GPIO 23
    input = GPIO.input(23)
    # Button needs to be pressed twice to skip the video.
    if input == GPIO.LOW: # For active-low button
        counter += 1
    if input == GPIO.HIGH:
        counter += 1
    if counter >= 2:
        return True
    return False


def getVideos():
    global videos
    videos = []
    for file in os.listdir(directory):
        if file.lower().endswith('.mp4'):
            videos.append(os.path.join(directory, file))


def playVideos():
    global videos
    if len(videos) == 0:
        getVideos()
        time.sleep(5)
        return
    random.shuffle(videos)
    counter = 0
    for video in videos:
        playProcess = Popen(['omxplayer', '--no-osd', '--aspect-mode', 'fill', video])
        while playProcess.poll() is None:
        # Check your condition here
            if skipCurrentVideo(counter):
                counter = 0
                playProcess.terminate()  # Or process.kill() for a more forceful termination
                break
            time.sleep(1) # Wait for a second before re-checking

while (True):
    playVideos()
