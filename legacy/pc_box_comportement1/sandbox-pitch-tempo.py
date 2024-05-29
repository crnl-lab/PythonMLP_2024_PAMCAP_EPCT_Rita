
import math
import numpy as np
import wave
import struct
import os
import platform
import sys



def sine_wave_lookuptable(frequency, framerate, amplitude, length):
    """ Generate a sine wave through a lookup table (this is quite fast)
    Courtesy of http://zacharydenton.com/generate-audio-with-python/
    """
    period = int(framerate / frequency)
    print frequency,framerate,period
    lookup_table = [float(amplitude) * math.sin(2.0*math.pi*float(frequency)*(float(i%period)/float(framerate))) for i in xrange(period)]
    return [lookup_table[i%period] for i in range(length)]




def sine_wave(frequency, framerate, amplitude, length):
    """ Generate a sine wave through a lookup table (this is quite fast)
    Courtesy of http://zacharydenton.com/generate-audio-with-python/
    """
    return [amplitude*np.sin(2.0*np.pi*i*frequency/framerate) for i in range(length)]




# Platform-specific imports
if platform.system()=="Linux":
    import pygame







class PitchExample():






    # Properties of the audio
    SAMPLEWIDTH    = 2
    STRUCTYPE      = "h"

    # The maximum amplitude if we are using 2-byte signed samples
    MAX_AMPLITUDE  = 32767.0/3.

    SAMPLEFREQ     = 44100
    NCHANNELS      = 1

    # Generate the C6 tone
    C6FREQ         = 1047.0 # Hz
    DURATION       = int(.1*  SAMPLEFREQ)   # in samples
    FADE_LENGTH    = int(.025*SAMPLEFREQ) # in n. of samples
    SILENCE_LENGTH = int(.25* SAMPLEFREQ)  # in samples (since the tone is 100ms long, we make the silence 250ms so the ITI is 350ms)




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






    def __init__(self):

        # self.calculateTarget()
        self.c6tone = self.generate_faded_tone(self.C6FREQ)

        # Generating silence
        self.silence = [ 0 for _ in range(self.SILENCE_LENGTH) ]

        # Put them in line, these are the first three tones
        self.preface = self.silence+(self.c6tone+self.silence)*3




    def generate_hyde_peretz( self, delay, freq_dev ):
        """ Generate the Hyde-Peretz (2004 Psych Sci) four-tone sequence,
        where the fourth is displaced, possibly, by an amount of delay (in msec), and
        shifted in pitch by an amount of freq_dev cents
        Delay needs to be bigger than zero. Freq_dev too """

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
        print "freq_dev=",freq_dev,"newfreq=",newfreq
        targettone   = self.generate_faded_tone(newfreq)

        # And then perhaps some alteration
        values = self.silence+self.preface+devsilence+targettone+shortsilence+self.c6tone+self.silence

        return values



    def make_hyde_peretz_wav( self, delay, freq_dev, filename ):
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






task = PitchExample()

#for delay in [0,20,50]:
for delay in [0,10,20,30,40,50,75]:

    for pitchshift in [0,8,10,15,20,30,50,100]:

        task.make_hyde_peretz_wav(delay,pitchshift,
                                  "stim_delay%imsec_pitch%icents.wav"%(delay,pitchshift))


#five_cents=task.generate_hyde_peretz(0,5)
#four_cents=task.generate_hyde_peretz(0,4)
#zero_cents=task.generate_hyde_peretz(0,0)

#import matplotlib.pyplot as plt
#plt.plot(five_cents,'-',color="red")
#plt.plot(zero_cents,'-',color="green")
#plt.plot(four_cents,'-',color="blue")
#plt.show()



