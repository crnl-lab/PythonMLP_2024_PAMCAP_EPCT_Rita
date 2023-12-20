"""

Implementing the MLP threshold detection procedure,
as described in Green (1993 JASA) and Gu and Green (1994 JASA).
Furthermore, we'll be adding catch trials to counteract 
bias in estimating false alarm rate (e.g. Leek et al (2000 JASA)).

"""
#
import numpy as np
import random





## This is the implementation of the psychometric function
def pyes( x, a, m, k ):
    # Return the probability of a "yes" response,
    # given the logistic psychmetric function.
    # x is the stimulus intensity,
    # a is the false alarm rate
    # k is the slope parameter (fiddle with this so it gives the right transition range)
    # m is the mean of the distribution
    return a+((1-a)*(1/(1+np.exp(-k*(x-m)))))




# Ok, some quantities we can already calculate on the basis of what we have now
# For example, the target P can be computed, given that we assume no attentional
# lapses (Green 1993 JASA, eq. 6)
def optimalp( a ):
    # Return the sweetpoint p for a given false alarm rate
    return (2*a+1+np.sqrt(1+8*a))/(3+np.sqrt(1+8*a))






class MLP:
    """
    This is the object that is in charge of running the MLP algorithm.
    So it will decide the stimulus level on each trial, and keep track
    of our hypotheses.
    """




    def __init__(
            self,

            # The slope of our psychometric curves
            slope = .1,
            
            # The minimum and maximum of the hypothesised thresholds
            hyp_min = 0,
            hyp_max = 200,

            # The number of hypotheses
            hyp_n = 200,
            
            # Our false alarm rates (these will be crossed with the threshold hypotheses)
            fa = [0.,.1,.2,.3,.4],
            
            # The number of trials
            # The number of catch trials (at the lowest stimulus level, to reduce biases in false alarm estimate)
            #NTRIALS_A        = 10
            #N_CATCH_TRIALS_A = 2
            #NTRIALS_B        = 20
            #N_CATCH_TRIALS_B = 4
    ):
        

        self.slope = slope
        self.hyp_min = hyp_min
        self.hyp_max = hyp_max
        self.hyp_n   = hyp_n

        self.fa = fa


        # The threshold hypotheses
        THRESHOLD_HYPOTHESES = np.linspace(self.hyp_min,
                                           self.hyp_max,
                                           self.hyp_n)

        # Initialise our hypotheses
        self.hypotheses = [ (a,m,1.)  # false alarm rate, threshold, and probability (initially just one)
                            for a in self.fa
                            for m in THRESHOLD_HYPOTHESES ]






    def calculate_target(self):
        # Determine the tracking target

        # We calculate the optimal tracking p values for the different false alarm rates
        P_YES = [ optimalp(fa) for fa in self.fa ]
        
        # And we take the mean of these and use that as the tracking value
        TARGET_P = np.mean(self.P_YES) # this is the tracking p-value, i.e. the performance for which we find the stimulus value based on our current maximum likelihood estimate

        return TARGET_P


        

    def update( self, x, answer, task ):
        # Given a subject's answer (yes=True or no=False) to stimulus intensity x,
        # update the likelihood of the hypotheses.
        # That is, for each hypotheses, calculate the probability p of
        # that observation assuming that hypothesis.
        # Then, we multiply the likelihood of that hypothesis with p.
        # We return the new list of hypotheses.

        newhyp = []
        for (a,m,p) in self.hypotheses:

            # Calculate the likelihood of a "yes" response to this stimulus
            obsp = pyes( x, a, m, self.slope )

            # If this was a no-response, invert the probability
            if not answer:
                obsp = 1-obsp

            # And then add the hypothesis to the new list
            newhyp.append( (a,m,p*obsp) )

        self.hypotheses = newhyp






    def get_ml(self):
        """ Get the current maximum likelihood stimulus. """

        # Now check for the maximum likelihood one
        maxp = max([ p for (_,_,p) in self.hypotheses ])

        # And then find the hypotheses that have this maximum
        maxlikelihyps = [ (a,m,p) for (a,m,p) in self.hypotheses 
                          if p==maxp ]

        # If there are several (due to being practically equal), just choose a random one
        # among them
        return random.choice( maxlikelihyps )




    def get_sweetpoint(
            self,
            params, 
            p
            ):
        """
        For a particular psychometric curve, return the stimulus
        level corresponding to a particular target p value.
        So this is just inverting the psychometric function.
        The psychmetric curve is as before, it is defined by the false alarm rate (a)
        and the threshold location (m).
        The target_p is a probability from 0 to 1.
        """

        (a,m,_)=params
        
        if p<=a:
            print ("Error, calculating a sweet point below the false alarm rate!")
            return None

        y = ((1-a)/(p-a))-1
        return (np.log(y)/(-self.slope))+m





    def next_stimulus(self):
        """ Decide which stimulus level to present now.
        This means essentially: deciding what is the current
        maximum likelihood hypothesis, finding its corresponding
        psychometric curve, and finding the corresponding sweet point.
        """
        
        # Get the most probable psychmetric curve
        candidate = self.getmaximumlikelihood()
        
        # Now we calculate the stimulus level corresponding to the "sweet point",
        # the target p-value that we track, for the maximum likelihood estimate
        stim = self.getsweetpoint(
            candidate,
            self.calculate_target() )

        return stim




    






















