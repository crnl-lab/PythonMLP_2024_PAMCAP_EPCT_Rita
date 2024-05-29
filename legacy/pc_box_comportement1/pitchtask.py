"""

Here, we try to make a tone series as in Hyde & Peretz (2004 Psych Sci)
but it has five notes of which the fourth one is slightly higher in pitch (in cents).

"""

from fivetoneseries import *



class PitchTask( FiveToneSeries ):


    # The name of this task
    NAME = "Pitch Task"

 
    """

    Configuration parameters of MLP

    """

    # The slope of our psychometric curves
    SLOPE = 1.0 # this must be the beta parameter

    # The minimum and maximum of the hypothesised thresholds
    MINHYP = 0
    MAXHYP = 300

    # The number of hypotheses
    NHYPOTHESES = 300
    # NHYPOTHESES = 3

    # The way the hypotheses are spaced
    HYPOTHESIS_SPACING = "lin" # "lin" or "log"

    # Our false alarm rates (these will be crossed with the threshold hypotheses)
    FALSE_ALARM_RATES = [0.,.1,.2,.3,.4]

    # The initial stimulus level
    INITIAL_STIM = MAXHYP

    # The number of catch trials (at the lowest stimulus level, to reduce biases in false alarm estimate)
    NTRIALS_A        = 10
    N_CATCH_TRIALS_A = 2
    NTRIALS_B        = 20
    N_CATCH_TRIALS_B = 4


    # The tracking p value for the different false alarm rates
    P_YES = None
    
    # The tracking p value
    TARGET_P = None


    


    def playstim(self,stim):
        """Play the given stimulus"""

        # Make the wave file

        # Generate the wave file for this stimulus
        self.make_hyde_peretz_wavfile(0,    # no delay
                                      stim,
                                      'stim.wav')

        # Play it using an external player
        if platform.system() in ["Linux","Windows"]:

            sound = pygame.mixer.Sound("stim.wav")
            sound.play()

            #pygame.mixer.music.load("stim.wav")
            #pygame.mixer.music.play()
            pygame.time.wait(1750)
            #pygame.mixer.music.stop()
            #pygame.mixer.music.load('other.wav')

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


