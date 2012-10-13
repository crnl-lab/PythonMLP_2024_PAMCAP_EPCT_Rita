"""

Implementing the MLP threshold detection procedure,
as described in Green (1993 JASA) and Gu and Green (1994 JASA).
Furthermore, we'll be adding catch trials to counteract 
bias in estimating false alarm rate (e.g. Leek et al (2000 JASA)).

"""
#
import numpy as np
import matplotlib.pyplot as plt
import random
from subprocess import call
import toneseries
import datetime

from configmlp import *

from matplotlib import cm


def gettoyresponse(stim):
    """ Here we just pretend to be doing the procedure: we will enter
    the response manually."""

    # Get the response for this stimulus level
    resp = raw_input("Stimulus level %.2f ==> [ 0 or 1 ] "%stim )
    if resp=="1": answer=True
    else:         answer=False

    return answer



def gettonesresponse(stim):
    """ We sonify the tone response for this stimulus,
    and then ask for the answer. """

    # Make the wave file
    toneseries.make_hyde_peretz_wav(stim,'stim.wav')

    # Play it using an external player
    call(["afplay", "stim.wav"]) # use in MacOS
    # call(["aplay","stim.wav"]) # use in linux

    resp=None
    while not resp in ["0","1"]:
        resp = raw_input("Was there a change? [ 0=no 1=yes ] " )
        if resp=="1":   answer=True
        elif resp=="0": answer=False
        else: print "Answer not understood! Enter your answer again."

    return answer
    

# Define which response function we use
getresponse = gettonesresponse









# Get basic data (e.g. participant name etc.)
participant = raw_input("Participant name: ")
fname = "data/%s--%s.txt"%(participant,
                           datetime.datetime.now().strftime("%d-%m.%Hh%Mm%S")
                           )
metafile = open(fname+".metadata.txt",'w')
metafile.write("participant          : %s\n"%participant)
metafile.write("slope                : %f\n"%SLOPE)
metafile.write("min-hyp              : %f\n"%MINHYP)
metafile.write("max-hyp              : %f\n"%MAXHYP)
metafile.write("n.hypotheses         : %i\n"%NHYPOTHESES)
metafile.write("false-alarm-rates    : %s\n"%( ",".join([ "%.2f"%f for f in FALSE_ALARM_RATES ]) ))
metafile.write("target p             : %f\n"%TARGET_P)
metafile.write("n.trials.A           : %i\n"%NTRIALS_A)
metafile.write("n.catch trials.A     : %i\n"%N_CATCH_TRIALS_A)
metafile.write("n.trials.B           : %i\n"%NTRIALS_B)
metafile.write("n.catch trials.B     : %i\n"%N_CATCH_TRIALS_B)
metafile.write("initial stim         : %f\n"%INITIAL_STIM)

outfile = open(fname,'w')
outfile.write("PARTICIPANT TRIAL TYPE STIMULUS RESPONSE\n")








# Initialise a list that includes the "catch" trials,
# so we plan in advance that we have the right number of catch trials.
trialsA = [ "mlp" for _ in range(NTRIALS_A-1) ] + [ "catch" for _ in range(N_CATCH_TRIALS_A) ]
trialsB = [ "mlp" for _ in range(NTRIALS_B)   ] + [ "catch" for _ in range(N_CATCH_TRIALS_B) ]
random.shuffle(trialsA)
random.shuffle(trialsB)
trials = ["mlp"] + trialsA + trialsB # this is done so that the first trial is never a catch

# The threshold hypotheses
THRESHOLD_HYPOTHESES = np.linspace(MINHYP,MAXHYP,NHYPOTHESES)

# Initialise our hypotheses
hypotheses = [ (a,m,1.)  # false alarm rate, threshold, and probability (initially just one)
               for a in FALSE_ALARM_RATES
               for m in THRESHOLD_HYPOTHESES ]

# The initial stimulus "guess"
stim = INITIAL_STIM

for i in range(len(trials)):

    # Decide what type of trial this is (catch or mlp)
    trialtype = trials[i]
    if trialtype=="catch": 
        stim = MINHYP # use the lowest hypothesized stimulus level

    # Also check that stim is in a valid range
    if stim<0: stim=0.0

    # Get the response for this stimulus
    answer = getresponse(stim)

    outfile.write('%s %i %s %f %i\n'%(participant,i,trialtype,stim,answer))
    
    # Run an update of the hypotheses
    hypotheses = updatehypotheses( hypotheses, 
                                   stim,
                                   answer )

    
    # Now check for the maximum likelihood one
    maxp = max([ p for (_,_,p) in hypotheses ])

    # And then find the hypotheses that have this maximum
    maxlikelihyps = [ (a,m,p) for (a,m,p) in hypotheses 
                      if p==maxp ]

    # If there are several (due to being practically equal), just choose a random one
    # among them
    likelihoodestimate = random.choice( maxlikelihyps )

    # Now we calculate the stimulus level corresponding to the "sweet point",
    # the target p-value that we track, for the maximum likelihood estimate
    stim = getsweetpoint( likelihoodestimate,
                          TARGET_P )
                          



# Make a little summary
(a,m,p)=likelihoodestimate
print "In %i trials, using %i hypotheses"%(len(trials),len(hypotheses))
print "the maximum likelihood estimate was at m=%.2f with false alarm estimate %.2f"%(m,a)

metafile.write('\n\n')
metafile.write('Maximum likelihood estimate: %.2f\n'%m)
metafile.write('False alarm rate estimate: %.2f\n\n'%a)

metafile.close()
outfile.close()
