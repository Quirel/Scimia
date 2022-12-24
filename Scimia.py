"""
Scimia by Novecento

This script is meant to be run directly.
"""

import os
import sys
import time
import sys
from queue import Queue

import numpy as np
import sounddevice as sd
import soundfile as sf
from termcolor import colored

scimia_enabled = True
BAR_LENGTH = 60
ALRT_TIMEOUT = 10.0
alarmt_ts = time.time() - ALRT_TIMEOUT
current_ts = time.time()

os.system('color')
os.system('mode con: cols=65 lines=32')

# If this file is compiled, we will use the _MEIPASS path (the temporary path/folder used by PyInstaller),
# otherwise use the CWD (current working directory).
data, fs = sf.read(getattr(sys, "_MEIPASS", os.getcwd()) + '/sound.wav')

print(r"""               _           _                __      __         
    __________(_)___ ___  (_)___ _   ____ _/ /___  / /_  ____ _
   / ___/ ___/ / __ `__ \/ / __ `/  / __ `/ / __ \/ __ \/ __ `/
  (__  ) /__/ / / / / / / / /_/ /  / /_/ / / /_/ / / / / /_/ / 
 /____/\___/_/_/ /_/ /_/_/\__,_/   \__,_/_/ .___/_/ /_/\__,_/  
                                       /_/       by Novecento                                                                                                                           
""")

if len(sys.argv)>1:
    print('Volume threshold set to ' + sys.argv[1])
    val = sys.argv[1]
else:
    val = input(" Set microphone treshold: ")

print(" Scimia is alarmed... ")

max_audio_value = int(val)

# Create the queue that will hold the audio chunks
audio_queue = Queue()


# noinspection PyUnusedLocal
def callback(indata: np.ndarray, outdata: np.ndarray, frames: int,
             time_, status: sd.CallbackFlags) -> None:
    """
    This is called (from a separate thread) for each audio block.

    Taken from the sounddevice docs:
    https://python-sounddevice.readthedocs.io/en/0.3.14/examples.html#recording-with-arbitrary-duration

    According to the docs, our function must have this signature:
    def callback(indata: ndarray, outdata: ndarray, frames: int,
                             time: CData, status: CallbackFlags) -> None
    """
    # Add the data to the queue
    audio_queue.put(indata.copy())


with sd.Stream(callback=callback):
    try:
        while True:
            # Pull a chunk of audio from the queue
            # This call is blocking, so if the queue is empty, we will wait until chunk has been added
            loudness = np.linalg.norm(audio_queue.get()) * 10
            bar = int(loudness * (BAR_LENGTH / max_audio_value))

            # If we are quiet, then print the audio bar
            if loudness < max_audio_value:
                print(' [' + '|' * bar + ' ' * (BAR_LENGTH - bar) + ']', end='\r')
            else:
                # Add the color red if we have passed the audio threshold
                print(colored(' [' + '!' * BAR_LENGTH + ']', 'red'), end='\r')
                # Play a sound to the user to let them know that they are loud
                if scimia_enabled:
                    current_ts = time.time()
                    # play sound only if it played more than X second ago
                    if current_ts < alarmt_ts + ALRT_TIMEOUT:
                        print(f'Skip. current: {current_ts}, alarm {alarmt_ts}, diff: {current_ts-alarmt_ts}')
                        continue
                    print(f'Alarm. alarm_ts: {alarmt_ts}, alarm_ts+10: {alarmt_ts + 10.0}, current_ts: {current_ts}, curent-alarm: {current_ts-alarmt_ts}')
                    alarmt_ts = current_ts
                    sd.play(data, fs)
                    sd.wait()
    except KeyboardInterrupt:
        print("\n\n\nStopping...")
