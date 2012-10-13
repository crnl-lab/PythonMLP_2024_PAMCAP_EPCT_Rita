

"""


This is a wrapper script that Tom can execute 
in the clinic. It will allow him to choose the
task and give the patient name and everything.



"""

import random
import sys
from ehrlesamson    import * 
from agencytask     import *
from mlp            import MLP


tasks = [("anisochrony",  "Hoertest"),
         ("delay-active", "Verzoeger-aktiv"),
         ("delay-passive","Verzoeger-passiv") ]





def runtest(task,trials):
    # Run one block of the MLP with the given task.
    # Here, task contains all the necessary configuration
    # parameters.
    print "MLP Test run"
    #participant = raw_input("Participant name: ")

    # Initialise file output
    #fileoutput = FileOutput( participant, task )

    # The initial stimulus "guess"
    stims = [ ("max",task.INITIAL_STIM),
              ("min",task.MINHYP) ]

    # Randomise the trials
    random.shuffle(trials)

    # The main loop for this block
    for i in range(len(trials)):

        # See what trialtype we are
        trialtype = trials[i]

        # Select the corresponding stimulus
        stim = dict(stims)[trialtype]

        # Wait for a keypress to start
        raw_input("Press <ENTER> for the stimulus.")

        # Get the response for this stimulus
        answer = task.evaluate(stim)

        # Give feedback
        if (trialtype=="min") == (answer==0):
            print "That is correct."
        else:
            print "That is wrong."
            

        # Add this trial response to the log
        # fileoutput.log( (participant,i,trialtype,stim,answer) )


    likelihoodest=(0,0,0)

    # That's all folks!
    # fileoutput.closefiles(likelihoodest)
    task.rideau() # Do some final things

    return





print "###############################################"
print
print
print "Musical stroke rehabilitation project, Hannover"
print
print 
print "###############################################"
participant=""
while not len(participant)>0:
    participant = raw_input("Please enter the patient number: ")





while True:

    print
    print
    print "Aufgaben: "
    for i in range(len(tasks)):
        print i,tasks[i][1]
    print

    answ = None
    while not answ in [str(i) for i in range(len(tasks)) ]:
        answ = raw_input("Which task do you want to do? ")
    selectedtask = tasks[int(answ)][0]

    if selectedtask=="anisochrony":
        task=EhrleSamson()
    if selectedtask in ["delay-active","delay-passive"]:
        task=AgencyTask()




    answ = None
    answers = ["try","train","1","2","3"]
    while not answ in answers:
        answ = raw_input("Which block [%s]? "%(" ".join(answers)))
    block = answ



    if block=="try":
        # A short try-out block that contains only 4 trials,
        # two at the smallest stimulus, two at the biggest one.
        # We also give feedback.
        runtest(task,["min","max","min","max"])




    if block=="train":
        # A short try-out block that contains 10 trials, but
        # follows the MLP procedure (i.e. dynamic selection
        # of the stimuli). We don't give feedback.

        # Make sure that we have only 10 trials in total
        task.NTRIALS_A        = 4
        task.N_CATCH_TRIALS_A = 1
        task.NTRIALS_B        = 4
        task.N_CATCH_TRIALS_B = 1

        # Then start the MLP
        mlp = MLP()
        mlp.run( task, 
                 participant="Patient%s-%s-Block%s"%(participant,
                                                     selectedtask,
                                                     block))



    if block in ["1","2","3"]:
        # The "real" experimental blocks

        # Then start the MLP
        mlp = MLP()
        mlp.run( task,
                 participant="Patient%s-%s-Block%s"%(participant,
                                                     selectedtask,
                                                     block))

