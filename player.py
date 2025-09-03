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
    for video in videos:
        if playProcess is None:  
            playProcess = subprocess.Popen(['omxplayer', '--no-osd', '--aspect-mode', 'fill', video], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while playProcess is not None:
            if skipCurrentVideo(previous_state):
                try:
                    playProcess.stdin.write(b'q')
                    playProcess.stdin.flush()
                except BrokenPipeError:
                    # This can happen if the process has already exited
                    pass
                previous_state = GPIO.input(23)
                playProcess.wait()
                time.sleep(0.25)
                # If the process is still running, force-terminate it
                if playProcess.poll() is None:
                    playProcess.terminate()
                    time.sleep(0.25)  # Give it a moment to stop
                    if playProcess.poll() is None:
                        playProcess.kill()
                playProcess = None
                break
            time.sleep(1) # Wait for a second before re-checking

while (True):
    playVideos()
