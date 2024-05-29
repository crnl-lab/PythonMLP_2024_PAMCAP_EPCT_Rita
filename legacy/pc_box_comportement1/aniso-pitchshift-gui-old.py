# -*- coding: utf-8 -*-


"""

Here we present the MLPy through a graphical user interface
(based on pygame).

FRENCH INSTRUCTIONS

"""

import pygame

import random
import sys
from pitchshiftedehrlesamson  import * 
from mlp                      import MLP
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





def runblock(task,block,block_name):

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
                 participant="%s-anisochrony-%s"%(participant,
                                                  block_name),
                 evaluate=evaluateGUI,
                 preKeypress=False,
                 )



    if block in ["1","2","3"]:
        # The "real" experimental blocks

        # Then start the MLP
        mlp = MLP()
        mlp.run( task,
                 participant="%s-anisochrony-%s"%(participant,
                                                  block_name),
                 evaluate=evaluateGUI,
                 preKeypress=False,
                 )







def instruct(task):
    """Give the instructions for this task"""

    keepGoing=True
    while keepGoing:
        mx = task.INITIAL_STIM
        mn = task.MINHYP

        instruct=u"Vous allez entendre cinq sons réguliers.\nAppuyez sur espace pour écouter un exemple."
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY)

        textScreen(screen,mainfont,u"Écoutez...")
        pygame.display.flip()
        task.playstim(mn)


        instruct = u"Ces cinq sons avaient un rhythme régulier.\nEn revanche, le quatrième son arrive parfois un peu trop tard,\nce qui rend la séquence irrégulière.\nAppuyez sur espace pour écouter un exemple."
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY)

        textScreen(screen,mainfont,u"Écoutez...")
        pygame.display.flip()
        task.playstim(mx)


        instruct = u"Le quatrième des cinq sons était en retard.\n\nVous allez entendre plusieurs séries de cinq sons.\nAprès chacune, je vais vous demander\nsi les sons étaient réguliers (comme dans le premier exemple)\nou pas (comme dans le dernier exemple).\n\nEst-ce que vous avez compris?\nPour commencer, un petit entrainement. \n\nAppuyez sur R pour relire ces instructions.\nAppuyez sur espace pour continuer."
        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY+[pygame.K_r])

        keepGoing= (key==2)
    
    return 
    




def showInstructions(block):
    """Show the instructions for a particular block"""

    print "Showing instructions"

    if block in ["train"]:


        instruct = u"Continuons avec un nouveau bloc.\nJe ne vais plus vous dire si votre réponse est correcte ou pas.\nDe plus, les différences vont désormais être plus petites.\nDonc écoutez bien!\n\nAppuyez sur espace quand vous êtes prêt(e)."
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


pitch_threshold=0
while not (pitch_threshold>0):
    pitch_threshold = float(raw_input("Pitch threshold: "))



ok = False
while not ok:
    relshift = raw_input("Relative pitch shift (%): ")
    if relshift.isdigit():
        relative_pitch_shift = int(relshift)
        ok = True




# Calculate the shifted pitch (which will be fixed throughout this run)
pitch_shift = pitch_threshold*(float(relshift)/100.)
print "==> Resulting pitch shift = %.2f cents"%pitch_shift
print




instr=""
while not (instr in ["y","n"]):
    instr = raw_input("Show instructions [y/n]? ")
show_instructions= instr=="y"









screen = init()

task = PitchShiftedEhrleSamson("late",pitch_shift)
blocks = []
if show_instructions:
    instruct(task)
    blocks = ["try","train"]

blocks += ["1","2","3"]

for block in blocks:

    # include both timing and pitch info in the block name
    block_name="%s_threshold%.2fcents_relativeshift%i_block%s"%("late",pitch_threshold,relative_pitch_shift,block)

    showInstructions(block)

    task = PitchShiftedEhrleSamson("late",pitch_shift) # Generate a new instance, so that we have the right number of trials
    runblock(task,block,block_name)


    if block=="train":
        instruct = u"Est-ce que tout était clair?\nSi vous voulez, vous pouvez demander l'expérimentateur.\n\nTapez sur espace pour continuer."#%block

        textScreen(screen,mainfont,instruct)
        pygame.display.flip()
        (t,key)=waitforkey(CONTINUE_KEY)
        

ending()


