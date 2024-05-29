"""

Here, we try to make a tone series as in Hyde & Peretz (2004 Psych Sci)
but it has five notes of which only one is displaced. That means, when we displace
one note, two intervals change: the one before the note becomes longer,
the one after the note becomes shorter.
This is what Ehrle & Samson (2005) did too.

Additionally, we can change the pitch of the target tone as well (or both).

Now from this class we get two subclasses:
* EhrleSamson, which manipulates just the delay
* PitchTask, which manipulates just the pitch
* ... and possibly more later on


"""

from subprocess import call # used to call the external player
from task import Task
import math
import numpy as np
import wave
import struct
import os
import platform
import sys
# import pygame




def sine_wave(frequency, framerate, amplitude, length):
    """ Generate a sine wave through a lookup table (this is quite fast)
    Courtesy of http://zacharydenton.com/generate-audio-with-python/
    """
    return [amplitude*np.sin(2.0*np.pi*i*frequency/framerate) for i in range(length)]



# Platform-specific imports
if platform.system() in ["Linux","Windows"]:
    import pygame







class FiveToneSeries( Task ):


    # The name of this task
    NAME = "Five Tone Series Task"

 
    """

    Configuration parameters of MLP

    """


    # Properties of the audio
    SAMPLEWIDTH    = 2
    STRUCTYPE      = "h"

    # The maximum amplitude if we are using 2-byte signed samples
    MAX_AMPLITUDE  = 32767.0/3.

    SAMPLEFREQ     = 44100
    NCHANNELS      = 1

    # Generate the C6 tone
    C6FREQ         = 1047 # Hz
    DURATION       = int(.1*  SAMPLEFREQ)   # in samples
    FADE_LENGTH    = int(.025*SAMPLEFREQ) # in n. of samples
    SILENCE_LENGTH = int(.25* SAMPLEFREQ)  # in samples (since the tone is 100ms long, we make the silence 250ms so the ITI is 350ms)



    # Early or late - whether the one different tone is early or late
    EARLY_OR_LATE = None






    def __init__(self,early_or_late="late"): # by default we do the late-version

        # Calculate the target p value that we track
        self.calculateTarget()

        # Generate the base tone
        self.c6tone = self.generate_faded_tone(self.C6FREQ)

        # Generating silence
        self.silence = [ 0 for _ in range(self.SILENCE_LENGTH) ]

        # Put them in line, these are the first three tones (without the final silence)
        self.preface = (self.c6tone+self.silence)*2+self.c6tone

        if platform.system() in ["Linux","Windows"]:
            # Initialise pygame for playing audio
            pygame.init()


        self.EARLY_OR_LATE = early_or_late
            






    def rideau(self):
        # Executed when we close
        # if platform.system()=="Linux":
        # Initialise pygame for playing audio
        #    pygame.quit()
        pass






    def generate_faded_tone(self,frequency):
        """ Generate a tone that has a certain frequency """

        # Generating a sine tone of 100ms long, at the particular frequency
        tone = sine_wave(frequency,self.SAMPLEFREQ,self.MAX_AMPLITUDE,self.DURATION)

        # Now we generate a "fade-in" and "fade-out", just linear to keep it simple
        for i in range(self.FADE_LENGTH):
            tone[i] =  tone[i]*i/self.FADE_LENGTH
        for i in range(self.FADE_LENGTH):
            tone[-i] = tone[-i]*i/self.FADE_LENGTH

        return tone





    def generate_hyde_peretz( self, delay, freq_dev ):
        """ Generate the Hyde-Peretz (2004 Psych Sci) four-tone sequence,
        where the fourth is displaced, possibly, by an amount of delay (in msec), and
        shifted in pitch by an amount of freq_dev cents
        Delay needs to be bigger than zero. Freq_dev too """

        # Make sure both are cast as floats (not decimals)
        delay    = float(delay)
        freq_dev = float(freq_dev)

        if delay<0: 
            print "Warning! Cannot generate the Hyde&Peretz for delay<0 (delay=%f)"%delay
            delay = 0.

        if freq_dev<0: 
            print "Warning! Cannot generate the Hyde&Peretz for freq_dev<0 (freq_dev=%f)"%freq_dev
            freq_dev = 0.


        # The extra silence
        extrasilentframes = int(self.SAMPLEFREQ*delay/1000.)
        devsilence   = [ 0 for _ in range(extrasilentframes) ] # the silence that becomes longer
        shortsilence = [ 0 for _ in range(self.SILENCE_LENGTH-extrasilentframes) ] # the silence that becomes shorter

        newfreq = 2**(float(freq_dev)/1200)*self.C6FREQ
        # print "freq_dev=",freq_dev,"newfreq=",newfreq
        targettone   = self.generate_faded_tone(newfreq)

        # And then perhaps some alteration
        if self.EARLY_OR_LATE=="late":
            values = self.preface+self.silence+devsilence+targettone+shortsilence+self.c6tone+self.silence
        if self.EARLY_OR_LATE=="early":
            values = self.preface+shortsilence+targettone+devsilence+self.silence+self.c6tone+self.silence
        return values



    def make_hyde_peretz_wavfile( self, delay, freq_dev, filename ):
        """ Generate the Hyde-Peretz stimulus at deviation dev,
        and write it to the given filename. """

        # First, generate the tone sequence
        values = self.generate_hyde_peretz(delay,freq_dev)

        # Writing a simple wave file
        output = wave.open(filename, 'w')
        output.setparams((self.NCHANNELS, self.SAMPLEWIDTH, self.SAMPLEFREQ, 0, 'NONE', 'not compressed'))
        value_str = struct.pack('%d%s'%(len(values),self.STRUCTYPE),*values)
        output.writeframes(value_str)
        output.close()

        # That's all folks!




