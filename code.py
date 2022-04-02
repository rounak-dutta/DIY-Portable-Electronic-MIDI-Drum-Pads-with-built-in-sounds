## Code for DIY-Portable-Electronic-MIDI-Drum-Pads-with-built-in-sounds ##
## by Rounak Dutta ##
## Huge Thanks to Adafruit industries for CircuitPython ##
## and the libraries for USB-MIDI and WAV audio playback. ##
import board
import digitalio
import analogio
import time
import touchio
import audiocore
import audiopwmio
import audiomixer
import usb_midi
import adafruit_midi
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn

# Initializing the USB MIDI channel
midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0], in_channel=0, midi_out=usb_midi.ports[1], out_channel=0
)

# RPI-Pico built-in LED as power-on indicator
led = digitalio.DigitalInOut(board.GP25)
led.direction = digitalio.Direction.OUTPUT
led.value = True

# Initializing CD4051, channel Select to scan the piezo-disks:
# GP18 - C (MSB) GP19 - B GP20 - A (LSB)
muxC = digitalio.DigitalInOut(board.GP18)
muxC.direction = digitalio.Direction.OUTPUT
muxB = digitalio.DigitalInOut(board.GP19)
muxB.direction = digitalio.Direction.OUTPUT
muxA = digitalio.DigitalInOut(board.GP20)
muxA.direction = digitalio.Direction.OUTPUT

# Analog Input Pin (from CD4051)
drPadIn = analogio.AnalogIn(board.GP26)


# Pad Combinations: Based on the current wiring
# (1)   (2)   (3)
#    (5)   (4)
# (6)   (8)   (7)
# The following is the address/ combination List for the CD4051 IC for selecting each drum-pad
# Modify the following, as per the wiring
combiList = [[0,0,0], [0,0,1], [0,1,0], [1,0,0], [0,1,1], [1,0,1], [1,1,1], [1,1,0]]
# After correction from the above combiList:
# (1)   (2)   (3)
#    (4)   (5)
# (6)   (7)   (8)


# Equivalent of Arduino's map() function.
def range_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# Equivalent of Arduino's map() function but with float output
def range_map_float(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Function to Scan the Piezo-Disks (Drum Pads)
scanDelay = 0.000010
def scanDrumPads():
    drumHits = []

    for i in range(0, 8):
        muxC.value = combiList[i][0]
        muxB.value = combiList[i][1]
        muxA.value = combiList[i][2]
        drumHits.append(drPadIn.value)
        time.sleep(scanDelay)
    return drumHits

# Reading and storing the Drum Samples from the Samples Folder
# The samples are currently mono in signed 16-bit WAV format with 16KHz sampling rate
# Max sampling rate possible is 22050
# Make sure any meta-data (e.g., artist name, album etc.) is not present in the samples
# Otherwise there will be an error during the wavfile read.
# Best to use Audacity for the sample creation
wavData1 = audiocore.WaveFile(open("/SAMPLES/001_Kick1.wav", "rb"))
wavData2 = audiocore.WaveFile(open("/SAMPLES/002_Snare1.wav", "rb"))
wavData3 = audiocore.WaveFile(open("/SAMPLES/003_Snare2.wav", "rb"))
wavData4 = audiocore.WaveFile(open("/SAMPLES/004_CHH1.wav", "rb"))
wavData5 = audiocore.WaveFile(open("/SAMPLES/005_OHH1.wav", "rb"))
wavData6 = audiocore.WaveFile(open("/SAMPLES/006_FTom1.wav", "rb"))
wavData7 = audiocore.WaveFile(open("/SAMPLES/007_Ride1.wav", "rb"))
wavData8 = audiocore.WaveFile(open("/SAMPLES/008_Crash1.wav", "rb"))

# Initializing the Mixer
mixer = audiomixer.Mixer(
    voice_count=8,
    sample_rate=16000,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)

# Using GP0 pin as the audio out, through RC LPF (Fc= ~10kHz, 1.5kOhm and 10nF (103)) [Optional]
# Followed by LM386 amplifier
dac = audiopwmio.PWMAudioOut(board.GP0)
dac.play(mixer)



# Settings for the Drum Pads
# Floor-Tom, Ride-Cymbal, Crash-Cymbal, Snare-1, Snare-2, Kick-Drum, Closed-HiHat, Open-HiHat
hitRecoverCountMax = [100, 100, 100, 100, 100, 75, 100, 100]
hitRecoverCount = [0, 0, 0, 0, 0, 0, 0, 0]
wavDataList = [wavData6, wavData7, wavData8, wavData2, wavData3, wavData1, wavData4, wavData5]

# Pad Thresholds and Max-values (range: 0 to 65536)
thrList = [15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000]
maxList = [50000, 50000, 40000, 55000, 35000, 45000, 40000, 45000]


# Midi-Info.:
velocityVal = 0
noteValList = [41, 51, 49, 38, 40, 36, 42, 46]
noteONFlagList = [0, 0, 0, 0, 0, 0, 0, 0]



# The main while-loop
while True:
    # Get the Drum-Pad's current RAW analog-data
    drumHits = scanDrumPads()

    # Processing the RAW analog data for each pad
    for i in range(0,8):
        # Check if the pad is recently hit, if not check for a hit and send note
        if (noteONFlagList[i] == 0):
            # If a pad is hit and value is over the threshold,
            # then play the audion and send midi data
            if drumHits[i] > thrList[i]:
                # Map the 16-bit velocity/ Analog value to 0-127 range
                velocityVal = range_map(drumHits[i], 0, maxList[i], 0, 127)
                # Cap the max-velocity to 120 and min to 20
                if (velocityVal > 120):
                    velocityVal = 127
                elif (velocityVal < 20):
                    velocityVal = 0

                # Map the velocity top 0-1 range for the mixer's volume level for the sample

                # For closed hi-hat, if open hi-hat is on, mute the open hi-hat
                # Currently: i=6 --> closed hi-hat, i=7 --> open hi-hat
                if (i == 6 and mixer.voice[7].playing):
                    mixer.voice[7].level = 0

                mixer.voice[i].level = range_map_float(velocityVal, 0, 127, 0, 1)
                # Play the sample
                mixer.voice[i].play(wavDataList[i])

                # Send the MIDI-note
                if (noteONFlagList[i] == 0):
                    midi.send(NoteOn(noteValList[i], velocityVal))
                    noteONFlagList[i] = 1

        # If a pad is recently hit, wait for some cycles for the pad to settle
        else:
            if (hitRecoverCount[i] >= hitRecoverCountMax[i]):
                    midi.send(NoteOff(noteValList[i], 64))
                    noteONFlagList[i] = 0
                    hitRecoverCount[i] = 0
            else:
                hitRecoverCount[i] += 1

    # Main-Loop-Delay: 10us
    time.sleep(0.000010)
