"""

Here, we try to make a tone series as in Hyde & Peretz (2004 Psych Sci)
but it has five notes of which only one is displaced. That means, when we displace
one note, two intervals change: the one before the note becomes longer,
the one after the note becomes shorter.
This is what Ehrle & Samson (2005) did too.

"""

from subprocess import call # used to call the external player
from mlpcore.task import Task
import math
import numpy as np
import wave
import struct
import os
import platform
import sys


def sine_wave(frequency, framerate, amplitude, length):
    """ Generate a sine wave through a lookup table (this is quite fast)
    Courtesy of http://zacharydenton.com/generate-audio-with-python/
    """
    period = int(framerate / frequency)
    lookup_table = [float(amplitude) * math.sin(2.0*math.pi*float(frequency)*(float(i%period)/float(framerate))) for i in xrange(period)]
    return [lookup_table[i%period] for i in range(length)]




# Platform-specific imports
if platform.system()=="Linux":
    import pygame







class EhrleSamson( Task ):


    # The name of this task
    NAME = "Anisochrony Detection"

 
    """

    Configuration parameters of MLP

    """

    # The slope of our psychometric curves
    SLOPE = .1

    # The minimum and maximum of the hypothesised thresholds
    MINHYP = 0
    MAXHYP = 200

    # The number of hypotheses
    NHYPOTHESES = 200

    # Our false alarm rates (these will be crossed with the threshold hypotheses)
    FALSE_ALARM_RATES = [0.,.1,.2,.3,.4]

    # The initial stimulus level
    INITIAL_STIM = MAXHYP

    # The number of trials
    # The number of catch trials (at the lowest stimulus level, to reduce biases in false alarm estimate)
    NTRIALS_A        = 10
    N_CATCH_TRIALS_A = 2
    NTRIALS_B        = 20
    N_CATCH_TRIALS_B = 4


    # The tracking p value for the different false alarm rates
    P_YES = None
    
    # The tracking p value
    TARGET_P = None


    





    # Properties of the audio
    SAMPLEWIDTH    = 2
    STRUCTYPE      = "h"

    # The maximum amplitude if we are using 2-byte signed samples
    MAX_AMPLITUDE  = 32767.0

    SAMPLEFREQ     = 44100
    NCHANNELS      = 1

    # Generate the C6 tone
    C6FREQ         = 1047 # Hz
    DURATION       = int(.1*  SAMPLEFREQ)   # in samples
    FADE_LENGTH    = int(.025*SAMPLEFREQ) # in n. of samples
    SILENCE_LENGTH = int(.25* SAMPLEFREQ)  # in samples (since the tone is 100ms long, we make the silence 250ms so the ITI is 350ms)




    def __init__(self):

        self.calculateTarget()

        # Generating a sine tone of 100ms long, C6
        self.tone = sine_wave(self.C6FREQ,self.SAMPLEFREQ,self.MAX_AMPLITUDE,self.DURATION)

        # Now we generate a "fade-in" and "fade-out", just linear to keep it simple
        for i in range(self.FADE_LENGTH):
            self.tone[i] =  self.tone[i]*i/self.FADE_LENGTH
        for i in range(self.FADE_LENGTH):
            self.tone[-i] = self.tone[-i]*i/self.FADE_LENGTH

        # Generating silence
        self.silence = [ 0 for _ in range(self.SILENCE_LENGTH) ]

        # Put them in line, these are the first three tones
        self.preface = (self.tone+self.silence)*3

        if platform.system()=="Linux":
            # Initialise pygame for playing audio
            pygame.init()


    def rideau(self):
        # Executed when we close
        if platform.system()=="Linux":
            # Initialise pygame for playing audio
            pygame.quit()





    def generate_hyde_peretz( self, dev ):
        """ Generate the Hyde-Peretz (2004 Psych Sci) four-tone sequence,
        where the fourth is displaced, possibly, by an amount of dev (in msec).
        Dev needs to be bigger than zero. """

        if dev<0: 
            #print "Warning! Cannot generate the Hyde&Peretz for dev<0 (dev=%f)"%dev
            dev = 0.

        # The extra silence
        extrasilentframes = int(self.SAMPLEFREQ*dev/1000.)
        devsilence   = [ 0 for _ in range(extrasilentframes) ] # the silence that becomes longer
        shortsilence = [ 0 for _ in range(self.SILENCE_LENGTH-extrasilentframes) ] # the silence that becomes shorter

        # And then perhaps some alteration
        values = self.preface+devsilence+self.tone+shortsilence+self.tone

        return values



    def make_hyde_peretz_wav( self, dev, filename ):
        """ Generate the Hyde-Peretz stimulus at deviation dev,
        and write it to the given filename. """

        # First, generate the tone sequence
        values = self.generate_hyde_peretz(dev)

        # Writing a simple wave file
        output = wave.open(filename, 'w')
        output.setparams((self.NCHANNELS, self.SAMPLEWIDTH, self.SAMPLEFREQ, 0, 'NONE', 'not compressed'))
        value_str = struct.pack('%d%s'%(len(values),self.STRUCTYPE),*values)
        output.writeframes(value_str)
        output.close()

        # That's all folks!




    def playstim(self,stim):
        """Play the given stimulus"""

        # Make the wave file

        # Play it using an external player
        if platform.system()=="Linux":

            # Generate the wave file for this stimulus
            self.make_hyde_peretz_wav(stim,'stim.wav')
            
            pygame.mixer.music.load("stim.wav")
            pygame.mixer.music.play()
            pygame.time.wait(2000)

            """
            # Make the stimulus (this is just concatenating)
            vals = self.generate_hyde_peretz(stim)

            # open stream
            stream = self.p.open(format   = self.SAMPLEWIDTH,
                                 channels = self.NCHANNELS,
                                 rate     = self.SAMPLEFREQ,
                                 output   = True)

            stream.write(vals)
            stream.close()
            """



        elif os.name=="posix": # That means we are in Mac OS

            # Generate a wave file
            self.make_hyde_peretz_wav(stim,'stim.wav')

            # And play it using the external player
            call(["afplay", "stim.wav"]) # use in MacOS




    def evaluate(self,stim):
        """ We sonify the tone response for this stimulus,
        and then ask for the answer. """

        # Play the stimulus
        self.playstim(stim)

        # And then collect the response
        resp=None
        while not resp in ["0","1"]:
            resp = raw_input("Die Toene waren [ 0=regelmaessig 1=unregelmaessig ]? " )
            if resp=="1":   answer=True
            elif resp=="0": answer=False
            else: print "Answer not understood! Enter your answer again."

        return answer


