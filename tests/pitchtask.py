"""

Here, we try to make a tone series as in Hyde & Peretz (2004 Psych Sci)
but it has five notes of which only the fourth has a higher pitch.

"""

from subprocess import call # used to call the external player
import os
import platform
import scipy.io.wavfile
import numpy as np
# Platform-specific imports
if platform.system() in ["Linux", "Windows"]:
    import pygame

def sine_wave(frequency, framerate, amplitude, length):
    """ Create a sine wave of the given frequency, at the particular framerate (frames/sec),
    with the given amplitude and specified length (the duration in frames).
    """
    t = np.linspace(0,length/framerate,length)
    signal = amplitude*np.sin(2*np.pi*frequency*t)
    return signal

class PitchTask:
    """ Pitch Change Detection Task """

    # The name of this task
    NAME = "Pitch Change Detection"

    # Properties of the audio
    SAMPLEWIDTH    = 2
    STRUCTYPE      = "h"

    # The maximum amplitude if we are using 2-byte signed samples
    MAX_AMPLITUDE  = .9 #32767.0

    SAMPLEFREQ     = 44100
    NCHANNELS      = 1

    # Generate the A4 tone
    A4FREQ         = 440 # Hz
    DURATION       = int(.1*  SAMPLEFREQ) # in samples
    FADE_LENGTH    = int(.025*SAMPLEFREQ) # in n. of samples
    SILENCE_LENGTH = int(.4* SAMPLEFREQ) # in samples (since the tone is 100ms long, we make the silence 400ms so the ITI is 500ms)




    def __init__(self):

        # Generating a sine tone of 100ms long, A4
        self.tone = sine_wave(self.A4FREQ,
                              self.SAMPLEFREQ,
                              self.MAX_AMPLITUDE,
                              self.DURATION)
        
        # Now we generate a "fade-in" and "fade-out", just linear to keep it simple
        for i in range(self.FADE_LENGTH):
            self.tone[i] =  self.tone[i]*i/self.FADE_LENGTH
        for i in range(self.FADE_LENGTH):
            self.tone[-i] = self.tone[-i]*i/self.FADE_LENGTH

        # Generating silence
        self.silence = [ 0 for _ in range(self.SILENCE_LENGTH) ]

        # Put them in line, these are the first three tones
        self.preface = np.concatenate([self.tone,self.silence]*3)

        if platform.system() in ["Linux", "Windows"]:
            # Initialise pygame for playing audio
            pygame.init()

    def generate_hyde_peretz( self, freq_dev ):
        """ Generate the Hyde-Peretz (2004 Psych Sci) four-tone sequence,
        where the fourth is shifted in pitc by an amount of dev (in cents).
        Dev needs to be bigger than zero. """

        freq_dev = max(freq_dev, 0.)

        # The new frequency
        newfreq = 2**(float(freq_dev)/1200)*self.A4FREQ
        # Generating a sine tone of 100ms long, A4
        dev_tone = sine_wave(newfreq,
                             self.SAMPLEFREQ,
                             self.MAX_AMPLITUDE,
                             self.DURATION)

        # Now we generate a "fade-in" and "fade-out", just linear to keep it simple
        for i in range(self.FADE_LENGTH):
            dev_tone[i] =  dev_tone[i]*i/self.FADE_LENGTH
        for i in range(self.FADE_LENGTH):
            dev_tone[-i] = dev_tone[-i]*i/self.FADE_LENGTH
  
        # And then perhaps some alteration
        values = np.concatenate([self.preface,dev_tone,self.silence,self.tone])

        return values



    def make_hyde_peretz_wav( self, freq_dev, filename ):
        """ Generate the Hyde-Peretz stimulus at deviation dev,
        and write it to the given filename. """

        # First, generate the tone sequence
        values = self.generate_hyde_peretz(freq_dev)

        # Writing a simple wave file
        scipy.io.wavfile.write(filename, self.SAMPLEFREQ, values)
        
        #output = wave.open(filename, 'w')
        #output.setparams((self.NCHANNELS, self.SAMPLEWIDTH, self.SAMPLEFREQ, 0, 'NONE', 'not compressed'))
        #value_str = struct.pack('%d%s'%(len(values),self.STRUCTYPE),*values)
        #output.writeframes(value_str)
        #output.close()

        # That's all folks!




    def playstim(self,stim):
        """Play the given stimulus"""

        # Make the wave file
        # Generate the temporary wave file for this stimulus
        fname = '.stim.wav'
        
        # Play it using an external player
        if platform.system() in ["Linux", "Windows"]:

            self.make_hyde_peretz_wav(stim,fname)
            
            pygame.mixer.music.load(fname)
            pygame.mixer.music.play()
            pygame.time.wait(2500)
            pygame.mixer.music.unload()

        elif os.name=="posix": # That means we are in Mac OS

            # Generate a wave file
            self.make_hyde_peretz_wav(stim,fname)

            # And play it using the external player
            call(["afplay", fname]) # use in MacOS



