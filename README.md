# DIY-Portable-Electronic-MIDI-Drum-Pads-with-built-in-sounds
DIY portable velocity-sensitive electronic Drum-pad for finger drumming


# Project Description:

In this repository, I am sharing the code, schematic and general build and usage guidelines for a portable velocity-sensitive electronic Drum-pad for finger-drumming, which can play drum (or technically any audio) samples loaded by the user and also act as usb-midi input device.
The drum-pad is powered by Raspberry-Pi Pico and CircuitPython. Huge Thanks to Adafruit industries for CircuitPython and the libraries for USB-MIDI and WAV audio playback.
The motivation for this project was to make a small and portable drum-pad which would have in-built sounds and battery power for trying out ideas at any place, and MIDI capability for when I want to work with my DAW.
I am glad to inform that all of these criteria is satisfied by the current project, with some minor drawbacks here and there.


# Demo available on YouTube: https://youtu.be/JEltvYWzZDU


# NOTE/ Warning: Issues observed with the current design:
1. 	When I am using battery power, I can hear a high-pitched whine/ noise in the headphones (when nothing is playing). Which is most-likely some kind of switching noise from the RPI-Pico's power management IC. My hypothesis is that battery voltage is ~3.7V, and 1N4007 drop is ~0.7, so ~3.0V is arriving at the Vsys of the PICO and the power management IC is boosting the voltage to 3.3V, and thus introducing the switching noise in the process. This issue maybe reolved by using a Schottky diode instead of the 1n4007 which I am currently using. Even with the above mentioned issue (which is not present when using USB power), the drum-pad is usable as the whine is generally drowned by the drum sample playback, but many people may find it annoying and the noise can cause issues with PAs in live scenarios.
The solution for now is to stick to USB power, or try using a schottky diode in place of the 1N4007.

2. 	During my testing, although I could definitely hear the difference between a hard and soft strike on the drum-pads, the consistency (and the range) of the velocity sensitivity is not even close to the professional grade equipments. Please consider the same before investing time in this project. Possible solutions can be: improvement in the algorithm, better setting of the thresholds and one can also try removing the 10nF capacitors in parallel with the 1meg resistors and 3.3v zener diodes.  


# Build details:

The schematic for the project is attached in the project-file area, as: RPI_Pico_8xDrum_Pad_Schematic.png.
The brains of this project is the Raspberry-Pi Pico (RP2040 uC), and the drum-pads are 1-inch piezoelectric disks (which are generally used as buzzers).
Since, RPI-Pico has only 3 analog-inputs, I had to use CD4051 8:1 analog MUX/DeMUX to scan the 8-drum pads.
Also the PWM audio out from RPI-Pico is very weak and thus, the same is being amplified through LM386 IC.

For the battery-power, I am using 18650 Li-Ion battery with TP4056 battery charger-and-protection module.
The battery-power is Power-ORed with the USB-power, through a 1n4007 diode (schottky diode is recommended to reduce the voltage-drop), and this is possible because the RPI-Pico board already has a schottky diode between the Vbus and Vsys pins.
Thus, using the connections in the attached schematic, the device can charge the battery when usb power is available and also switch back to battery power when the usb is unplugged and both MIDI connection and power/ battery charging can be done through the same RPI-Pico's usb port.

For the drum-pads, I used 1-inch piezo disks, to which gnd and signal wires are soldered, then hot-glue is added to protect the connection and the disks are mounted on 4inch x 4inch electrical box using double-sided tapes.
On the top-side I glued some foam circles. The finished construction can be viewed on the YouTube demo.

The sensitivity and the thresholds for each drum-pad can be set in the following lines of code.py. The file can be easily modified in any text editor.

\# Pad Thresholds and Max-values
thrList = [15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000]
maxList = [50000, 50000, 40000, 55000, 35000, 45000, 40000, 45000]


The drum-pad map w.r.t the wiring can be assigned in the following lines:

\# The following is the address/ combination List for the CD4051 IC for selecting each drum-pad
\# Modify the following, as per the wiring
combiList = [[0,0,0], [0,0,1], [0,1,0], [1,0,0], [0,1,1], [1,0,1], [1,1,1], [1,1,0]]

\*In this repository, in the SAMPLES folder text-to-speech versions of the Sample names are present and can be used to verify the wiring and functionality.

The sample to drum-pad map can be assigned in the following lines:

wavDataList = [wavData6, wavData7, wavData8, wavData2, wavData3, wavData1, wavData4, wavData5]
noteValList = [41, 51, 49, 38, 40, 36, 42, 46]

\*By interchanging the order of the wavData6, wavData7, etc., the samples can be shuffled w.r.t to the drum-pads, and the same is true for the MIDi-notes sent, using the "noteValList".



# How to load the samples:
The best tool for processing the samples is Audacity (which is versatile, small and free). Many audacity tutorials are available on YouTube for the operations mentioned in the following lines:
	1. The desired samples need to be openened in Audacity and then merged to MONO, set the sample rate to 16KHz (max 22050Hz), and exported as signed 16-bit PCM WAV file.
	2. Make sure there are no meta-data such as Artist name, Album name, etc are present, otherwise the WAV files may not play. Click on the clear button on the dialogue box that appears to add the meta-data during the export process, to make sure no meta-data is present.
	3. Once the export is complete, connect the RPI-Pico (which should already be configured for CircuitPython) and in the RPI-Pico's CIRCUITPY drive, create a folder called SAMPLES and copy the samples in the same.
	4. Make sure to edit the names of the samples in the code.py file's "waveData1 = audiocore.WaveFile(..." lines.

In this repository, in the SAMPLES folder text-to-speech versions of the Sample names are present and can be used to verify the wiring and functionality.

Note: There is only approximately 900KB available for the samples, as the samples are currently being loaded directly on the RPI-Pico's program memory, thus make sure the sample lengths (/size) are small enough.
If an SD-Card module is added (as an upgrade), larger samples may be used. But for 8-drum pads and with sample-rate limit of 22KHz, I found 900KB to be plenty enough.
Also, if any other sample-rate than 16KHz is used (max 22KHz), please edit the same in the "sample_rate=16000," portion of the code.py file.


# Notes on the CircuitPython Version and Libraries:

Please use the same version of CircuitPython .uf2 file and the libs, e.g., 7.x.x or 6.x.x. If the version of .uf2 and the libraries are mixed, the code does not work.
The CircuitPython libraries required is present in the "lib.zip" file of this repository (which are of version 7.x.x, and needs to be unzipped before use). If any other version of .uf2 file is used, the equivalent libs need to be used. 

CircuitPython UF2 file Download: https://circuitpython.org/board/raspberry_pi_pico/
CircuitPython Library Download: https://circuitpython.org/libraries

Other CircuitPython Lib info./ references: 	

https://docs.circuitpython.org/en/latest/shared-bindings/pwmio/index.html
https://docs.circuitpython.org/en/latest/shared-bindings/audiopwmio/index.html
https://docs.circuitpython.org/en/latest/shared-bindings/displayio/index.html
https://docs.circuitpython.org/en/latest/shared-bindings/audiomixer/index.html
https://docs.circuitpython.org/en/latest/shared-bindings/sdcardio/index.html
https://docs.circuitpython.org/en/latest/shared-bindings/audiocore/index.html#audiocore.RawSample
