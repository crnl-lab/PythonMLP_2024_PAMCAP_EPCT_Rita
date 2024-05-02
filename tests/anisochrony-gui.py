# -*- coding: utf-8 -*-


"""

Here we present the MLPy through a graphical user interface
(based on pygame).

"""

import pygame

import random
import sys
from ehrlesamson    import * 
import pythonmlp
import time
import pandas as pd


displaySize = (1024,600) # for widescreen
# The background of the screen
BGCOLOR = (127,127,127)
# Pygame configuration constants
displayFlags = 0
#displayFlags = pygame.FULLSCREEN



mainfont = None
mainFontSize = 16
screen = None

CONTINUE_KEY  = [ pygame.K_SPACE ]
RESPONSE_KEYS = [ pygame.K_r, pygame.K_i ]







# The (fixed) slope of our psychometric curves
SLOPE_HYP = .1

# The minimum and maximum of the hypothesised thresholds
MINHYP = 0
MAXHYP = 200

# The number of hypotheses
NHYPOTHESES = 200

# Our false alarm rates (these will be crossed with the threshold hypotheses)
FALSE_ALARM_RATES = [0.,.1,.2,.3,.4]

# The initial stimulus level
INITIAL_STIM = MAXHYP
MAX_STIM = MAXHYP




def init():
    # Get started
    pygame.init()

    # Initialise the fonts
    global mainfont
    mainfont = pygame.font.SysFont("Times",mainFontSize) 

    screen = pygame.display.set_mode(displaySize,displayFlags)
    screen.convert()
    pygame.display.set_caption('MLP Experiment')
    pygame.mouse.set_visible(False)
    screen.fill(BGCOLOR)

    # Initialise the random numbers
    random.seed()

    return screen




def ending():
    # To stop the program
    pygame.quit()



def waitforkey( keys ):
    # Just wait until the user presses one of these keys,
    # then return the key that was pressed and the reaction
    # time.
    t0 = time.time()
    bailout = False 
    key = None
    t=0
    pygame.event.clear() # Make sure there is no previous keypresses in the pipeline

    while not bailout:

        time.sleep(.01) # wait for 10ms

        # Flush the time 
        t = time.time()

        # Wait for the next event
        evs = pygame.event.get()

        for ev in evs:

            if ev.type == pygame.KEYDOWN:
                if ev.key in keys:
                    key = keys.index(ev.key)+1
                    bailout=True
                if ev.key == pygame.K_ESCAPE:
                    sys.exit(0)

            if ev.type == pygame.QUIT:
                sys.exit(0)


    return (t,key)





def textScreen( surf, font, text,
                bgColor = (127,127,127),
                fontcolor = (255,255,255),
                linespacing = 40 ):
    """ Display the given text on the screen surface """
    surf.fill( bgColor )

    # First convert each line into a separate surface
    lines = text.split("\n")
    textboxes = []
    for line in lines:
        textboxes.append( font.render(line,True,fontcolor) )

    # Then blit the surfaces onto the screen
    starty = (surf.get_height()-(len(lines)*linespacing))/2
    i=0
    for i in range(len(textboxes)):
        # Put the image of the text on the screen at 250 x250
        surf.blit( textboxes[i] , ((surf.get_width()-textboxes[i].get_size()[0])/2,
                                   starty+(i*linespacing)) )


    return starty+(len(lines)*linespacing)
        










def runtest(task,trials):
    # Run one block of the MLP with the given task.
    # Here, task contains all the necessary configuration
    # parameters.
    print ("MLP Test run")
    #participant = raw_input("Participant name: ")

    # Initialise file output
    #fileoutput = FileOutput( participant, task )

    # The initial stimulus "guess"
    stims = [ ("max",INITIAL_STIM),
              ("min",MINHYP) ]

    # Randomise the trials
    random.shuffle(trials)

    # The main loop for this block
    for i in range(len(trials)):

        # See what trialtype we are
        trialtype = trials[i]

        # Select the corresponding stimulus
        stim = dict(stims)[trialtype]

        if i==0:
            textScreen(screen,mainfont,u"Appuyez sur la barre d'espace pour écouter l'extrait")
            pygame.display.flip()
            waitforkey(CONTINUE_KEY)

        # Wait for a keypress to start
        #raw_input("Press <ENTER> for the stimulus.")

        textScreen(screen,mainfont,u"Écoutez...")
        pygame.display.flip()

        task.playstim(stim)

        textScreen(screen,mainfont,u"Est-ce que les sons étaient régulier (appuyer sur R) ou irrégulier (appuyer sur I)?")
        pygame.display.flip()
        (t,key)=waitforkey(RESPONSE_KEYS)
        # Get the response for this stimulus
        answer = (key==2) # answer is True when response is irregular (change heard)


        # Give feedback
        cont = u"Appuyez sur la barre d'espace pour écouter le prochain extrait"
        if (trialtype=="min") == (answer==0):
            textScreen(screen,mainfont,u"C'est correct.\n\n"+cont)
        else:
            textScreen(screen,mainfont,u"C'est faux.\n\n"+cont)
        pygame.display.flip()
        waitforkey(CONTINUE_KEY)
            

        # Add this trial response to the log
        # fileoutput.log( (participant,i,trialtype,stim,answer) )


    likelihoodest=(0,0,0)

    # That's all folks!
    # fileoutput.closefiles(likelihoodest)
    #task.rideau() # Do some final things

    return







def evaluateGUI(stim):
    """ This is a custom function to evaluate a stimulus level,
    and it is fed into the MLP procedure. We are given a stimulus
    level, present it to the participant, and register the answer.
    That's all, the MLP takes care of the rest."""


    textScreen(screen,mainfont,u"Écoutez...")
    pygame.display.flip()

    task.playstim(stim)

    textScreen(screen,mainfont,u"Est-ce que les sons étaient régulier (appuyer sur R) ou irrégulier (appuyer sur I)?")
    pygame.display.flip()
    (t,key)=waitforkey(RESPONSE_KEYS)
    # Get the response for this stimulus
    answer = (key==2) # answer is True when response is irregular (change heard)

    return answer





def runblock(block,participant):

    task = EhrleSamson()
    
    if block=="try":
        # A short try-out block that contains only 4 trials,
        # two at the smallest stimulus, two at the biggest one.
        # We also give feedback.
        runtest(task,["min","max","min","max"])
        return


        
    if block=="train":
        # A short try-out block that contains 10 trials, but
        # follows the MLP procedure (i.e. dynamic selection
        # of the stimuli). We don't give feedback.

        # Make sure that we have only 10 trials in total
        NTRIALS        = 8
        N_CATCH_TRIALS = 2
        


    if block in ["1","2","3"]:
        # The "real" experimental blocks

        NTRIALS        = 20
        N_CATCH_TRIALS = 4




    mlp = pythonmlp.MLP(
    
        # The slope of our psychometric curves
        slope = SLOPE_HYP, # this is a cheat, we give the real psychometric curve slope...
        
        # The minimum and maximum of the hypothesised thresholds
        hyp_min = MINHYP,
        hyp_max = MAXHYP,
        
        # The number of hypotheses
        hyp_n = NHYPOTHESES,
        
        # Our false alarm rates (these will be crossed with the threshold hypotheses)
        fa = FALSE_ALARM_RATES,
    )
    
        
    # Initialise a list that includes the "catch" trials,
    # so we plan in advance that we have the right number of catch trials.
    trials = [ "mlp" for _ in range(NTRIALS-1) ] + [ "catch" for _ in range(N_CATCH_TRIALS) ]
    random.shuffle(trials)
    
    # The trials we want to do
    todo = ["mlp"] + trials #+ trialsB # this is done so that the first trial is never a catch
    
    # Now let's run those trials
    
    stim = INITIAL_STIM # start at the maximum level
    
    trials = []
    for trial,info in enumerate(todo):
            
        stim = stim if stim>0 else 0 # set to 0 if lower
        stim = 0 if info=='catch' else stim
        
        textScreen(screen,mainfont,u"Écoutez...")
        pygame.display.flip()

        task.playstim(stim)

        textScreen(screen,mainfont,u"Est-ce que les sons étaient régulier (appuyer sur R) ou irrégulier (appuyer sur I)?")
        pygame.display.flip()
        (t,key)=waitforkey(RESPONSE_KEYS)
        # Get the response for this stimulus
        ans = (key==2) # answer is True when response is irregular (change heard)

        
        mlp.update(stim,ans)
        trials.append({
            "trial":trial+1,
            "kind":info,
            "stimulus":stim,
            "response":ans
            })
        stim = mlp.next_stimulus()

    from datetime import datetime
    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y%m%d-%H%M%S')
    fname = "{}-anisochrony-{}.csv".format(participant,formatted_time)
    trials = pd.DataFrame(trials)
    trials['task']='anisochrony'
    trials.to_csv(fname,index=False)




def instruct():
    """Give the instructions for this task"""

    task = EhrleSamson()

    keepGoing=True
    while keepGoing:
        mx = INITIAL_STIM
        mn = MINHYP

        instruct=u"Vous allez entendre cinq sons presenté dans un rhythme régulier.\nAppuyez sur espace pour écouter un exemple."
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY)

        textScreen(screen,mainfont,u"Écoutez...")
        pygame.display.flip()
        task.playstim(mn)


        instruct = u"C'étaient cinq sons dans un rhythme régulier.\nPar contre, parfois vous allez entendre que le quatrième son est un peu trop tard,\ndonc faisant la séquence irrégulier.\nAppuyez sur espace pour écouter un exemple."
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY)

        textScreen(screen,mainfont,u"Écoutez...")
        pygame.display.flip()
        task.playstim(mx)


        instruct = u"C'étaient cinq sons dont le quatrième est un peu tard.\n\nVous allez entendre plusieurs fois des suites de cinq sons.\nAprès chaque fois, je vais vous demander\ns'il vous ont semblé regulier (comme la première séquence que vous avez entendu)\nou pas régulier (comme la dernière séquence que vous avez entendu).\n\nEst-ce que vous avez compris?\nPour pratiquer, on va faire quelques examples. Après, je vais vous dire si votre réponse c'était correct.\n\nAppuyez sur R pour relire ces instructions.\nAppuyez sur espace pour continuer."
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY+[pygame.K_r])

        keepGoing= (key==2)
    
    return 
    




def showInstructions(block):
    """Show the instructions for a particular block"""

    print ("Showing instructions")

    if block in ["train"]:
        instruct = u"Maintenant on va continuer avec un nouveau bloc.\nJe ne vais plus vous dire si votre réponse était correct ou pas.\nDu coup, les différences vont être plus petites maintenant.\nDonc écoutez bien!\n\nAppuyez sur espace quand vous êtes prêt(e)."
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY)



    if block in ["1","2","3"]:
        instruct = u"Maintenant on commence le bloc %s (sur 3).\n\nAppuyez sur espace pour continuer."%block
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY)





participant=""
while not len(participant)>0:
    participant = input("Participant: ")

screen = init()

instruct()

blocks = ["try","train","1","2","3"]
for block in blocks:

    showInstructions(block)
    runblock(block,participant)

ending()


