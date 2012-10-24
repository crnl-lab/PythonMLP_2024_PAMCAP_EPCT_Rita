"""

Implementing the MLP threshold detection procedure,
as described in Green (1993 JASA) and Gu and Green (1994 JASA).
Furthermore, we'll be adding catch trials to counteract 
bias in estimating false alarm rate (e.g. Leek et al (2000 JASA)).

"""
#
import numpy as np
import random


from fileoutput import *




def pyes( x, a, m, k ):
    # Return the probability of a "yes" response,
    # given the logistic psychmetric function.
    # x is the stimulus intensity,
    # a is the false alarm rate
    # k is the slope parameter (fiddle with this so it gives the right transition range)
    # m is the mean of the distribution
    return a+((1-a)*(1/(1+np.exp(-k*(x-m)))))





class MLP:
    """
    This is the object that is in charge of running the MLP algorithm.
    So it will decide the stimulus level on each trial, and keep track
    of our hypotheses.
    """




    def __init__(self):
        # What is done when we create the object
        pass




    def init_hypotheses(self,task):
        """ Initialise a set of hypotheses that we will entertain during the block run."""

        # Initialise a list that includes the "catch" trials,
        # so we plan in advance that we have the right number of catch trials.
        trialsA = [ "mlp" for _ in range(task.NTRIALS_A-1) ] + [ "catch" for _ in range(task.N_CATCH_TRIALS_A) ]
        trialsB = [ "mlp" for _ in range(task.NTRIALS_B)   ] + [ "catch" for _ in range(task.N_CATCH_TRIALS_B) ]
        random.shuffle(trialsA)
        random.shuffle(trialsB)

        self.trials = ["mlp"] + trialsA + trialsB # this is done so that the first trial is never a catch

        # The threshold hypotheses
        THRESHOLD_HYPOTHESES = np.linspace(task.MINHYP,task.MAXHYP,task.NHYPOTHESES)

        # Initialise our hypotheses
        self.hypotheses = [ (a,m,1.)  # false alarm rate, threshold, and probability (initially just one)
                            for a in task.FALSE_ALARM_RATES
                            for m in THRESHOLD_HYPOTHESES ]

        # That's all folks
        return
        

        

    def updatehypotheses( self, x, answer, task ):
        # Given the answer (yes=True or no=False) to stimulus intensity x,
        # update the likelihood of the hypotheses.
        # That is, for each hypotheses, calculate the probability p of
        # that observation assuming that hypothesis.
        # Then, we multiply the likelihood of that hypothesis with p.
        # We return the new list of hypotheses.
        newhyp = []
        for (a,m,p) in self.hypotheses:

            # Calculate the likelihood of a "yes" response to this stimulus
            obsp = pyes( x, a, m, task.SLOPE )

            # If this was a no-response, invert the probability
            if not answer:
                obsp = 1-obsp

            # And then add the hypothesis to the new list
            newhyp.append( (a,m,p*obsp) )

        self.hypotheses = newhyp








    def getmaximumlikelihood(self):

        # Now check for the maximum likelihood one
        maxp = max([ p for (_,_,p) in self.hypotheses ])

        # And then find the hypotheses that have this maximum
        maxlikelihyps = [ (a,m,p) for (a,m,p) in self.hypotheses 
                          if p==maxp ]

        # If there are several (due to being practically equal), just choose a random one
        # among them
        return random.choice( maxlikelihyps )




    def getsweetpoint( self,
                       (a,m,_), 
                       p,
                       task ):
        """
        For a particular psychometric curve, return the stimulus
        level corresponding to a particular target p value.
        So this is just inverting the psychometric function.
        The psychmetric curve is as before, it is defined by the false alarm rate (a)
        and the threshold location (m).
        The target_p is a probability from 0 to 1.
        """

        if p<=a:
            print "Error, calculating a sweet point below the false alarm rate!"
            return None

        y = ((1-a)/(p-a))-1
        return (np.log(y)/(-task.SLOPE))+m









    def run(self, 

            # The task, which must be an object that inherits Task
            task,

            # If we give a participant name here, we won't ask it anymore
            participant="",

            # A function that we call to evaluate a particular stimulus.
            evaluate=None,

            # Whether to ask for a keypress before we start
            preKeypress=True,

            ):

        # If we don't give an alternative evaluate stimulus,
        # we just take the one provided by the task
        if evaluate==None:
            evaluate=task.evaluate

        # Run one block of the MLP with the given task.
        # Here, task contains all the necessary configuration
        # parameters.
        print "MLP "+task.NAME

        # Input the participant name if we don't know it already
        if participant=="":
            participant = raw_input("Participant name: ")
        else:
            print "Participant: ",participant
        self.participant=participant

        # Initialise file output
        self.fileoutput = FileOutput( self.participant, task )

        # Initialise the hypotheses
        self.init_hypotheses(task)

        # The initial stimulus "guess"
        stim = task.INITIAL_STIM

        print "Prepared %i trials"%len(self.trials)

        if preKeypress:
            # Wait for a keypress to start
            raw_input("Press <ENTER> to start the experiment.")

        # The main loop for this block
        for i in range(len(self.trials)):

            # Decide what type of trial this is (catch or mlp)
            trialtype = self.trials[i]
            if trialtype=="catch": stim = task.MINHYP # use the lowest hypothesized stimulus level

            # Get the response for this stimulus
            answer = evaluate(stim)

            # Add this trial response to the log
            self.fileoutput.log( (self.participant,i,trialtype,stim,answer) )

            # Run an update of the hypotheses
            hypotheses = self.updatehypotheses( stim, answer, task )

            # Get the most probable psychmetric curve
            likelihoodestimate = self.getmaximumlikelihood()

            # Now we calculate the stimulus level corresponding to the "sweet point",
            # the target p-value that we track, for the maximum likelihood estimate
            stim = self.getsweetpoint( likelihoodestimate,
                                       task.TARGET_P, task )


        (a,m,p)=likelihoodestimate
        print
        print "In %i trials, using %i hypotheses"%(len(self.trials),len(self.hypotheses))
        print "the maximum likelihood estimate was at m=%.2f with false alarm estimate %.2f"%(m,a)

        # That's all folks!
        self.fileoutput.closefiles(likelihoodestimate)
        task.rideau() # Do some final things

        return
























