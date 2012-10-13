import numpy as np
import random


from ehrlesamson    import * 
from fileoutput     import *



def runtest(task):
    # Run one block of the MLP with the given task.
    # Here, task contains all the necessary configuration
    # parameters.
    print "MLP Test run"
    participant = raw_input("Participant name: ")

    # Initialise file output
    fileoutput = FileOutput( participant, task )

    # Wait for a keypress to start
    raw_input("Press <ENTER> to start the experiment.")

    # The initial stimulus "guess"
    stims = [ ("max",task.INITIAL_STIM),
              ("min",task.MINHYP),
              ("mid",np.mean([ task.INITIAL_STIM, task.MINHYP ])), ]

    # The main loop for this block
    for i in range(NTRIALS):

        # Choose a stimulus randomly
        (trialtype,stim) = random.choice(stims)

        # Get the response for this stimulus
        answer = task.evaluate(stim)

        # Give feedback
        if (trialtype=="min") == (answer==0):
            print "That is correct."
        else:
            print "That is wrong."
            

        # Add this trial response to the log
        fileoutput.log( (participant,i,trialtype,stim,answer) )


    likelihoodest=(0,0,0)

    # That's all folks!
    fileoutput.closefiles(likelihoodest)
    task.rideau() # Do some final things

    return




task = EhrleSamson()
#task = HydePeretz()



NTRIALS = 10

runtest(task)
