import os
import random
import time
import RPi.GPIO as GPIO
from omxplayer.player import OMXPlayer


directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'videos/encoded')
videos = []


GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.HIGH) # Set high
time.sleep(1)
GPIO.output(23, GPIO.LOW)  # Set low
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)


DBUS_NAME_1 = 'org.mpris.MediaPlayer2.omxplayer1'
DBUS_NAME_2 = 'org.mpris.MediaPlayer2.omxplayer2'


# Initialize players to None
curr_player = None
next_player = None


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


def get_next_video(current_index):
    """Get the next video file path in the list."""
    global videos
    next_index = (current_index + 1) % len(videos)
    return videos[next_index], next_index


def setup_player(video_file, dbus_name):
    """Initialize an omxplayer instance with a custom D-Bus name."""
    player = OMXPlayer(video_file, dbus_name=dbus_name, args=['--blank', '--no-osd', '--aspect-mode', 'fill'])
    player.pause() # Start paused
    return player


def playVideos():
    global videos
    global curr_player, next_player
    if len(videos) == 0:
        getVideos()
        time.sleep(5)
        return
    random.shuffle(videos)
    previous_state = GPIO.input(23)
    # Binary to determine which dbus the current player is on. True = Dbus1
    curr_dbus = False
    for index, video in enumerate(videos):
        next_video, _ = get_next_video(index)
        if curr_player is None:
            curr_player = setup_player(video, DBUS_NAME_1)
            curr_dbus = True
            curr_player.play()
        next_dbus = DBUS_NAME_2 if curr_dbus else DBUS_NAME_1
        next_player = setup_player(next_video, next_dbus)
        while curr_player.is_playing():
            if skipCurrentVideo(previous_state):
                break
            time.sleep(3) # Wait 3 seconds before re-checking
        next_player.play()
        curr_player.quit()
        curr_player = None
        previous_state = GPIO.input(23)
        curr_dbus = not curr_dbus
        curr_player, next_player = next_player, None

while (True):
    playVideos()
