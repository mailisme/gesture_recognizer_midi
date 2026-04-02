import time

import mido
from mido import Message

print(mido.get_output_names())
msg = Message('note_on', note=60, velocity=100)
outport = mido.open_output('loopMIDI Port 10')
while True:
    outport.send(msg)
    time.sleep(0.5)