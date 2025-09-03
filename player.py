import os
import random
import time
import RPi.GPIO as GPIO
import subprocess

directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'videos/encoded')

videos = []

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.HIGH) # Set high
time.sleep(1)
GPIO.output(23, GPIO.LOW)  # Set low
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def skipCurrentVideo(previous_state):
    # Button assigned to GPIO 23
    time.sleep(0.5) # Debounce delay
    input = GPIO.input(23)
    if previous_state != input:
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
    previous_state = GPIO.input(23)
    playProcess = None
    for index, video in enumerate(videos):
        if playProcess is None:
            playProcess = subprocess.Popen(['omxplayer', '--no-osd', '--aspect-mode', 'fill', video], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        next_video = video[0]
        if index + 1 < len(videos):
            next_video = videos[index+1]
        while playProcess is not None:
            if skipCurrentVideo(previous_state):
                nextPlayProcess = subprocess.Popen(['omxplayer', '--no-osd', '--aspect-mode', 'fill', next_video], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(0.2)
                try:
                    playProcess.stdin.write(b'q')
                    playProcess.stdin.flush()
                except BrokenPipeError:
                    # This can happen if the process has already exited
                    pass
                previous_state = GPIO.input(23)
                playProcess.wait()
                # If the process is still running, force-terminate it
                if playProcess.poll() is None:
                    playProcess.terminate()
                    if playProcess.poll() is None:
                        playProcess.kill()
                playProcess = nextPlayProcess
                break
            time.sleep(1) # Wait for a second before re-checking

while (True):
    playVideos()
