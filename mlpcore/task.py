import numpy as np



# Ok, some quantities we can already calculate on the basis of what we have now
# For example, the target P can be computed, given that we assume no attentional
# lapses (Green 1993 JASA, eq. 6)
def optimalp( a ):
    # Return the sweetpoint p for a given false alarm rate
    return (2*a+1+np.sqrt(1+8*a))/(3+np.sqrt(1+8*a))



class Task:

    """
    This is an object that generates the stimuli on a particular
    trial, presents them to a participant, and asks for a response.
    It then gives it back to the MLP object.
    It also includes the configuration parameters (i.e. n. of hypotheses,
    slope, FA rates, etc.)
    """

    # The name of this task
    NAME = "Null task"
    

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







    def __init__(self):

        self.calculateTarget()
        self.init() # Do some task-specific inits





    def calculateTarget(self):
        # Determine the tracking target

        # We calculate the optimal tracking p values for the different false alarm rates
        self.P_YES = [ optimalp(fa) for fa in self.FALSE_ALARM_RATES ]

        # And we take the mean of these and use that as the tracking value
        self.TARGET_P = np.mean(self.P_YES) # this is the tracking p-value, i.e. the performance for which we find the stimulus value based on our current maximum likelihood estimate







    def evaluate(self, stim):
        """ Get the participant's response for the given stimulus level. """
        resp=None
        while not resp in ["0","1"]:
            resp = raw_input("Is there a meaning to life? Stimulus level: %f [ 0=no 1=yes ] "%stim )
            if   resp=="1": answer=True
            elif resp=="0": answer=False
            else: print "Answer not understood! Enter your answer again."
        return answer
        



    def init(self):
        pass # You can customise this when you create your own tasks



    def rideau(self):
        """ Where we have the chance to do some things to do at the end. """
        pass



# >>>> We should do this in the corresponding task object
# Also check that stim is in a valid range
# if stim<0: stim=0.0
