# -*- coding: utf-8 -*-


"""

Here we present the MLPy through a graphical user interface
(based on pygame) - the pitch task (based on Hyde & Peretz).

FRENCH INSTRUCTIONS

"""

import pygame
import datetime


import random
import sys
from pitchtask      import *
from mlp            import MLP
import time


displaySize = (1024,768) # for widescreen
#displaySize = (1920,1200) # for widescreen
# The background of the screen
BGCOLOR = (127,127,127)
# Pygame configuration constants
#displayFlags = 0
displayFlags = pygame.FULLSCREEN



mainfont = None
mainFontSize = 22
screen = None
FONTFILE = "fonts/VAG Rounded BT.ttf"

CONTINUE_KEY  = [ pygame.K_SPACE ]
RESPONSE_KEYS = [ pygame.K_i, pygame.K_r ]


def init():
    # Get started
    pygame.init()

    # Initialise the fonts
    global mainfont
    mainfont = pygame.font.Font(FONTFILE, mainFontSize)

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
                bgColor = BGCOLOR,
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

        if i==0:
            textScreen(screen,mainfont,u"Appuyez sur la barre d'espace pour écouter l'extrait")
            pygame.display.flip()
            waitforkey(CONTINUE_KEY)

        # Wait for a keypress to start
        #raw_input("Press <ENTER> for the stimulus.")

        textScreen(screen,mainfont,u"Écoutez...")
        pygame.display.flip()

        task.playstim(stim)

        textScreen(screen,mainfont,u"Y a-t-il eu un changement ? (Oui ou Non)")
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
    task.rideau() # Do some final things

    return







def evaluateGUI(stim):
    """ This is a custom function to evaluate a stimulus level,
    and it is fed into the MLP procedure. We are given a stimulus
    level, present it to the participant, and register the answer.
    That's all, the MLP takes care of the rest."""


    textScreen(screen,mainfont,u"Écoutez...")
    pygame.display.flip()

    task.playstim(stim)

    textScreen(screen,mainfont,u"Y a-t-il eu un changement ? (Oui ou Non)")
    pygame.display.flip()
    (t,key)=waitforkey(RESPONSE_KEYS)
    # Get the response for this stimulus
    answer = (key==2) # answer is True when response is irregular (change heard)

    screen.fill(BGCOLOR)
    pygame.display.flip()

    return answer





def runblock(task,block):

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
                 participant="%s-pitchtask-%s"%(participant,
                                                block),
                 evaluate=evaluateGUI,
                 preKeypress=False,
                 )
        

    if block in ["1","2","3"]:
        # The "real" experimental blocks

        # Then start the MLP
        mlp = MLP()
        ret = mlp.run( task,
                       participant="%s-pitchtask-%s"%(participant,
                                                      block),
                       evaluate=evaluateGUI,
                       preKeypress=False,
                       )
        return ret


    return None





def instruct(task):
    """Give the instructions for this task"""

    keepGoing=True
    while keepGoing:
        mx = task.INITIAL_STIM
        mn = task.MINHYP

        instruct=u"Vous allez entendre cinq sons identiques.\nAppuyez sur espace pour écouter un exemple."
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY)

        textScreen(screen,mainfont,u"Écoutez...")
        pygame.display.flip()
        task.playstim(mn)


        instruct = u"Ces sons étaient identiques.\nEn revanche, le quatrième son sera parfois plus aigu,\ndonc différent des autres.\nAppuyez sur espace pour écouter un exemple."
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY)

        textScreen(screen,mainfont,u"Écoutez...")
        pygame.display.flip()
        task.playstim(mx)


        instruct = u"Le quatrième son était plus aigu.\n\nVous allez entendre plusieurs séries de cinq sons.\nAprès chacune, je vais vous demander\nsi les cinq sons étaient identiques (comme dans le premier exemple)\nou différents (comme dans le dernier exemple).\n\nEst-ce que vous avez compris?\nPour commencer, voici un entrainement.\n\nAppuyez sur R pour relire ces instructions.\nAppuyez sur espace pour continuer."
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY+[pygame.K_r])

        keepGoing= (key==2)
    
    return 
    




def showInstructions(block):
    """Show the instructions for a particular block"""

    print "Showing instructions"

    if block in ["train"]:


        instruct = u"On continue avec un nouveau bloc.\nJe ne vais plus vous dire si votre réponse est correcte où pas.\nDe plus, les différences vont être plus petites.\nDonc écoutez bien!\n\nAppuyez sur espace quand vous êtes prêt(e)."
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY)



    if block in ["1","2","3"]:
        instruct = u"Maintenant, le bloc %s (sur 3).\n\nAppuyez sur espace pour continuer."%block
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY)





participant=""
while not len(participant)>0:
    participant = raw_input("Participant: ")

screen = init()

task=PitchTask()
instruct(task)

blocks = ["try","train","1","2","3"]
block_results = {}
for block in blocks:

    showInstructions(block)

    task=PitchTask() # Generate a new instance, so that we have the right number of trials
    results = runblock(task,block)
    block_results[block]=results # add the results to our trace


    if block=="train":
        instruct = u"Est-ce que tout était clair?\nSi besoin, vous pouvez appeler l'expérimentateur.\n\nAppuyez sur espace pour continuer."#%block
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY)
        
ending()



#
# Now we make a summary of the three blocks. We check whether for each block, the participant
# has not responded "irregular" too often to catch trials. For the remaining (accepted) blocks,
# we take the average.
#
#

CATCH_YES_CUTOFF = .3 # the usual (from van Vugt & Tillmann as well as the BAASTA people)

timestamp = "%s"%datetime.datetime.now().strftime("%d-%m-%Y.%Hh%Mm%S")

summaryblocks = []
report = "PITCH TASK participant %s\n"%participant
report += timestamp
report += "\n\n"
for block in ["1","2","3"]:

    trials_log      = block_results[block]["trials"]
    (_,threshold,_) = block_results[block]["likelihoodestimate"]
    threshold = float(threshold)

    n_catch = len([ x for x in trials_log if x["type"]=="catch" ])
    n_catch_yes = len([ x for x in trials_log if x["type"]=="catch" and x["response"]==1 ])
    catch_yes_ratio = float(n_catch_yes)/float(n_catch)

    report+= "block %s: threshold=%.2f #catch=%i #catch.yes=%i #catch.yes.ratio=%.2f "%(block,
                                                                                        threshold,
                                                                                        n_catch,
                                                                                        n_catch_yes,
                                                                                        catch_yes_ratio)
    if catch_yes_ratio>CATCH_YES_CUTOFF:
        report += "DISCARDED (CATCH-YES)"
    else:
        report += "ACCEPTED"
        summaryblocks.append(threshold)

    report += "\n"


# If there are no valid blocks remaining, report that.
if len(summaryblocks)==0:
    report += "NO VALID BLOCKS REMAINING."
else:
    report += "\nAverage of valid blocks = %.2f cents"%(np.mean(summaryblocks))

#
# Write the report on screen and also write it to a file
#
f = open('data/%s-pitchtask-summary-%s.txt'%(participant,timestamp),'w')
f.write(report)
f.close()

print report
raw_input("Press any key to finish.")



