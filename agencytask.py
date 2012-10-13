"""

This is the module that does nothing more than showing stimuli
of various intensities when requested by MLP.

"""

import time
from task import *

import fluidsynth # you'll need pyfluidsynth (http://code.google.com/p/pyfluidsynth/)

import termios, fcntl, sys, os # Used to detect keypress


class AgencyTask (Task):

    # The name of this task
    NAME = "Agency/Delay detection"


    """
    Our agency/delay detection task as used in the stroke rehabilitation
    study (Tom Kafczyk, Floris van Vugt, Eckart Altenmueller, 2012)
    """
    

    # The slope of our psychometric curves
    SLOPE = .1

    # The minimum and maximum of the hypothesised thresholds
    MINHYP = 0
    MAXHYP = 1000

    # The number of hypotheses
    NHYPOTHESES = 500

    # Our false alarm rates (these will be crossed with the threshold hypotheses)
    FALSE_ALARM_RATES = [0.,.1,.2,.3,.4]

    # The initial stimulus level
    INITIAL_STIM = 1200

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



    # The sounds emitted for each of the keys
    sounds  = None
    channel = None # the mixer channel we use to play the sounds

    # Whether we use fluidsynth
    fs = None # the fluidsynth object
    
    SOUNDFONTFILE = "soundfonts/drums woodblock (8kb).sf2"




    def init(self):
        # Some initialisation stuff
        self.fs = fluidsynth.Synth()
        self.fs.start(driver="alsa")
        
        self.sfid = self.fs.sfload(self.SOUNDFONTFILE) 
        self.fs.program_select(0, self.sfid, 0, 0) # select the sound font, armed and loaded!
        



    def rideau(self):
        # What to do when we close the program
        self.fs.delete() # release the fluidsynth process





        



    # The parameters of the note that we play
    RESPONSE_NOTE     = 66
    RESPONSE_VELOCITY = 127 # maximal sound!
    NOTE_DURATION     = .1  # duration of the notes in sec


    WAIT_AFTER = .5 # how long to wait after, so that you don't get immediately back to the question

    def play_tone( self, t ):
        """ Play the tone after a delay of t ms, t>0 """
        t0          =time.time()
        target_t_on =t0+t/1000.
        target_t_off=target_t_on+self.NOTE_DURATION
        t           =t0

        # Wait until it is time to play the tone
        while t<target_t_on:
            t=time.time()

        # And then play the tone
        self.fs.noteon(0, self.RESPONSE_NOTE, self.RESPONSE_VELOCITY) 

        # Then wait as long as the tone lasts
        while t<target_t_off:
            t=time.time()

        # Switch the tone off again
        self.fs.noteoff(0, self.RESPONSE_NOTE )


        while t<target_t_off+self.WAIT_AFTER:
            t=time.time()

        return







    def evaluate(self,stim):
        """ Give the stimulus at the given level (decided by MLP)
        and collect the answer."""

        if stim<0:
            print "Warning: cannot generate delay smaller than zero (%.5f), hence setting to zero"%stim
            stim=0.

        print "Press the key"
        self.awaitkey()
        #pr = raw_input("Keypress? ")
        self.play_tone(stim) # play the tone, after a delay of some msec

        # Get the response for this stimulus level
        resp = None
        while resp not in ["0","1"]:
            resp = raw_input("Wann kam der Ton? [ 0=gleichzeitig 1=verzoegert ] ")
        if resp=="1": answer=True
        else:         answer=False

        return answer






    def awaitkey( self, key="0" ):
        # Wait for the user to press a key

        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        bailout=False

        while not bailout:
            try:
                while not bailout:
                    c=0
                    try:
                        c = sys.stdin.read(1)
                        #print "Got character", c, repr(c), "waiting for",key
                        if c==key:
                            bailout = True
                    except IOError: pass
            finally:
                termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
                fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)






