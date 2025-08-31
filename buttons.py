import RPi.GPIO as GPIO
import time
import os

os.system('raspi-gpio set 19 ip')
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT)


def turnOnScreen():
    os.system('raspi-gpio set 19 op a5')
    GPIO.output(18, GPIO.HIGH)


def turnOffScreen():
    os.system('raspi-gpio set 19 ip')
    GPIO.output(18, GPIO.LOW)


turnOnScreen()
screen_on = True
