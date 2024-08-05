# -*- coding: utf-8 -*-


"""

Here we present the MLPy through a graphical user interface
(based on pygame).

"""

import random
import sys
import os
import platform
from pathlib import Path
import time
from datetime import datetime
import logging
import pandas as pd

import pygame
from pitchtask import PitchTask
import pythonmlp

if platform.system() == "Windows":
    os.environ['SDL_VIDEODRIVER'] = 'windows'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# log level for printing
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
logger.addHandler(ch)

PATH_GESTION_META_PROTO = './../Gestion_Meta_Protocoles/'
PATH_GESTION_META_PROTO_WD = PATH_GESTION_META_PROTO + 'Rita_Working_Dir/'

ALL_BLOCKS = ["try","train","1"]

DISPLAY_SIZE = (1024,600) # for widescreen
# The background of the screen
BGCOLOR = (255,255,255)
# The default font color
FGCOLOR = (91,155,213)
# Pygame configuration constants
DISPLAY_FLAGS = pygame.FULLSCREEN
DISPLAYNUM = 1


MAINFONT = None
MAINFONTSIZE = 32
SCREEN = None

CONTINUE_KEY  = [ pygame.K_RETURN ]
RESPONSE_KEYS = [ pygame.K_r, pygame.K_i ]
REPLAY_KEY = [ pygame.K_SPACE ]

# Where to save csv files
PATH_DATA = './data'

# Where to read story.xlsx icons and png files
PATH_STORY = "./stories/Lala"

# Prompt for participant code if empty
PARTICIPANT = ""

# Skip initial blocks if START_BLOCK >=0
START_BLOCK = -1

# The (fixed) slope of our psychometric curves
SLOPE_HYP = 1.

# The minimum and maximum of the hypothesised thresholds
MINHYP = 0
MAXHYP = 300

# The number of hypotheses
NHYPOTHESES = 301

# Our false alarm rates (these will be crossed with the threshold hypotheses)
FALSE_ALARM_RATES = [0.,.1,.2,.3,.4]

# The initial stimulus level
INITIAL_STIM = MAXHYP
MAX_STIM = MAXHYP

def init():
    """
    Initialize pygame parameters and random seed.

    Returns
    -------
    scr: pygame.surface.Surface
        the screen initialized.
    fnt: pygame.font.Font
        the default font choosed.
    """
    # Get started
    pygame.init()

    # Initialise the fonts
    fnt= pygame.font.SysFont("Times",MAINFONTSIZE)

    scr = pygame.display.set_mode(DISPLAY_SIZE,DISPLAY_FLAGS, display=DISPLAYNUM)
    # Change icon if provided
    if Path(PATH_STORY).joinpath('icon.png').exists():
        icon_img = pygame.image.load(PATH_STORY + '/icon.png')
        pygame.display.set_icon(icon_img)
    scr.convert()
    pygame.display.set_caption('MLP Experiment')
    pygame.mouse.set_visible(False)
    scr.fill(BGCOLOR)
    # Take full control of the mouse and keyboard
    pygame.event.set_grab(True)

    # Initialise the random numbers
    random.seed()

    return (scr, fnt)

def ending():
    """ Quit pygame. """
    # To stop the program
    pygame.quit()
    logging.shutdown()

def waitforkey( keys ):
    """
    Wait until the user presses one of these keys.

    Parameters
    ----------
    keys : list of int
        List of expected keys (e.g. [pygame.K_SPACE]).

    Returns
    -------
    t-t0: float
        the reaction time in secs.
    idx+1: int
        the number of the key that was pressed.
    """
    t0 = time.time()
    bailout = False
    key = None
    t=t0
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


    return (t-t0,key)

def text_screen(surf, font, text,
                bg_color = BGCOLOR,
                fontcolor = FGCOLOR,
                linespacing = 40,
                img = None):
    """ 
    Display the given text on the screen surface.

    Parameters
    ----------
    surf: pygame.surface.Surface
        The screen surface on which to display this text.
    font: pygame.font.Font
        The font to be used.
    text: str
        The text to display.
    bg_color: tuple of int
        Background color e.g. (0,0,0) for black (255,255,255) for white
        None for no background color behind text
    fontcolor: tuple of int
        Color to use for text.
    linespacing: int
        Vertical disance between lines
    img: str
        png to be displayed or None
    """
    surf.fill( bg_color )

    # Add img if there is one
    if isinstance(img,str):
        add_img(surf,img, text)
    # First convert each line into a separate surface
    lines = text.split("\n")
    textboxes = []
    for line in lines:
        textboxes.append( font.render(line,True,fontcolor, bg_color) )

    # Then blit the surfaces onto the screen
    starty = (surf.get_height()-(len(lines)*linespacing))/2
    i=0
    for i,txt in enumerate(textboxes):
        # Put the image of the text on the screen at 250 x250
        surf.blit( txt , ((surf.get_width()-txt.get_size()[0])/2,
                                   starty+(i*linespacing)) )

    return starty+(len(lines)*linespacing)

def runtest(task,trials):
    """
    Run one test block with the given task with feedback.


    Parameters
    ----------
    task: object 
        implements the playstim method 
    trials: list of str 
        str should be in ("min" or "max")
    """
    logger.info ("MLP Test run")

    # The initial stimulus "guess"
    stims = [ ("max",INITIAL_STIM),
              ("min",MINHYP) ]

    # Randomise the trials
    random.shuffle(trials)

    # The main loop for this block
    for i, trialtype in enumerate(trials):

        # Select the corresponding stimulus
        stim = dict(stims)[trialtype]

        info_txt = str(i+1) + "/" + str(len(trials)) + "(" + trialtype + ":" + str(round(stim)) + ")"
        answer, _ = evaluate_stim(stim, info_txt, task)
        # Give feedback
        if (trialtype=="max") == answer:
            add_img(SCREEN, STORY.Img[STORY.Type=="OK"].iloc[0], "OK")
        else:
            add_img(SCREEN, STORY.Img[STORY.Type=="KO"].iloc[0], "!!!!!!! C'est Faux !!!!!!!")
        pygame.display.flip()
        waitforkey(CONTINUE_KEY)

    return

def evaluate_stim(stim, txt="evaluate_stim", task = PitchTask()):
    """ 
    This is a custom function to evaluate a stimulus level,
    and it is fed into the MLP procedure. We are given a stimulus
    level, present it to the participant, and register the answer.
    That's all, the MLP takes care of the rest.

    Parameters
    ----------
    stim: any
        the stimulus level (parameter of task.playstim())
    txt: str
        text for console feedback to the experimenter
    task: object
        object implementing the playstim method

    Returns
    -------
    ans: bool
        wether the change was detected
    count: int
        the number of times the stimulus was played
    """

    replay = True
    count = 0
    # repeat if replay asked
    while replay:
        count = count + 1
        text_screen(SCREEN, MAINFONT, "Écoute...")
        pygame.display.flip()
        add_img(SCREEN,
            STORY.Img[STORY.Type=="Test"].iloc[0],
            txt, end= ' ' * len(txt) + '\r')
        task.playstim(stim)
        pygame.display.flip()
        _, key = waitforkey(RESPONSE_KEYS + REPLAY_KEY)
        replay = key == 3
        if replay:
            logger.warning('\n!!!!!!! Stimulus rejoué !!!!!!!\n')

    # Get the response for this stimulus
    ans = key==2 # answer is True when response is irregular (change heard)

    return ans, count

def runblock(block, participant):
    """
    run a block of MLP and save results in csv

    Parameters
    ----------
    block: str
        one of 
        - "try" : 4 trials (2min 2max) with feedback, 
        - "train" : 10 trials (MLP selected) without feedback,
        - "1","2","3": real experimental blocks
    participant: str
        participant code to include in csv name
    """

    task = PitchTask()

    if block=="try":
        # A short try-out block that contains only 4 trials,
        # two at the smallest stimulus, two at the biggest one.
        # We also give feedback.
        runtest(task,["min","max","min","max"])
        return

    if block == "train":
        # A short try-out block that contains 10 trials, but
        # follows the MLP procedure (i.e. dynamic selection
        # of the stimuli). We don't give feedback.

        # Make sure that we have only 10 trials in total
        ntrials        = 8
        n_catch_trials = 2

    if block in ["1", "2", "3"]:
        # The "real" experimental blocks
        ntrials        = 20
        n_catch_trials = 4

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
    if ntrials > 10:
        trials = [ "mlp" for _ in range(ntrials-6) ] + [ "catch" for _ in range(n_catch_trials) ]
        random.shuffle(trials)
        # The trials we want to do
        todo =  ["mlp"] * 5 + trials + ["mlp"] # avoid catch trials in the first 5 or last 1
        # catch trials are here to avoid repetitions around the same stimulus level:
        # it is useless at the end of the block when there is nothing left to test
        # and useless at the beginning when stimuli vary a lot
    else:
        trials = [ "mlp" for _ in range(ntrials-1) ] + [ "catch" for _ in range(n_catch_trials) ]
        random.shuffle(trials)
        # The trials we want to do
        todo = ["mlp"] + trials #+ trialsB # this is done so that the first trial is never a catch

    # Now let's run those trials
    stim = INITIAL_STIM # start at the maximum level
    trials = []
    for trial,info in enumerate(todo):

        stim = stim if stim>0 else 0 # set to 0 if lower
        stim = 0 if info=='catch' else stim

        info_txt = str(trial+1) + "/" + str(len(todo)) + "(" +  info + " : " + str(round(stim)) + ")"
        ans, count = evaluate_stim(stim, info_txt, task)

        # Alerts for errors on catch trials and max
        if ans & ((info == "catch") | (stim==0)):
            logger.warning('\n!!!!!!! Erreur sur un catch trial !!!!!!!\n')
        if (not ans) & (stim >= MAXHYP):
            logger.warning('\n!!!!!!! Erreur sur un niveau MAX  !!!!!!!\n')

        mlp.update(stim,ans)
        trials.append({
            "trial":trial+1,
            "kind":info,
            "stimulus":stim,
            "response":ans,
            "count": count
            })
        stim = mlp.next_stimulus()
        update_participant_proto_state(PROTO_PARTICIPANT_FILE, MLP_i_trial=trial)

    current_time = datetime.now()
    fname = f"{participant}-pitchtask-{current_time:%Y%m%d-%H%M%S}.csv"
    trials = pd.DataFrame(trials)
    trials['task']='pitchtask'
    trials.to_csv(PATH_DATA + '/' + fname,index=False)

    # Block feedback for experimenter
    logger.info('\n')
    logger.info(mlp.to_string())
    logger.info('--> %s\n', fname)

def add_img(screen,png, infotxt, end = "\n"):
    """
    Draw the diapositive on the screen

    Parameters
    ----------
    screen: pygame.surface.Surface
        The screen on which image should be drawn.
    infotxt: str
        A text to display on console for experimenter feedback.
    end: str (default: "\n")
        Should experimenter feedback infotxt end with newline or not?
        Alternatives include:
        - "": to continue on the same line after
        - "\r": (carriage return) to overwrite this line after
    """
    img = pygame.image.load(PATH_STORY + '/' + str(png) + '.png')
    r = img.get_rect()
    screen.blit(img,((DISPLAY_SIZE[0] - r.width)/2,(DISPLAY_SIZE[1] - r.height)/2))
    print(infotxt, end = end, flush = True)
    logger.debug(infotxt)

def instruct():
    """Give the instructions for this task"""

    task = PitchTask()
    instructfont = pygame.font.SysFont("arial",60)

    keep_going=True
    while keep_going:
        instruct_line = STORY[STORY.Type=="Instruct"]
        for i in instruct_line.index:
            if pd.isna(instruct_line.Img[i]):
                text_screen(SCREEN,instructfont,instruct_line.Text[i],
                           fontcolor = (91,155,213),
                           linespacing=70)
                logger.info(instruct_line.Text[i])
            else:
                add_img(SCREEN,instruct_line.Img[i],instruct_line.Text[i])
            pygame.display.flip()
            if instruct_line.Sound[i] == "MINHYP":
                task.playstim(MINHYP)
            elif instruct_line.Sound[i] == "MAXHYP":
                task.playstim(MAXHYP)
            if instruct_line.Duration[i]=="Key":
                _, key = waitforkey(CONTINUE_KEY + [pygame.K_r])
                if key == 2:
                    break
            else:
                time.sleep(instruct_line.Duration[i]) # duration in sec
        keep_going = key==2
    return


def show_instructions(block):
    """Show the instructions for a particular block"""

    logger.info ("Showing instructions")

    if block in ["train"]:
        txt = "Maintenant c'est vraiment toi le juge, donc écoute bien!\nAppuie sur entrée pour continuer."
        text_screen(SCREEN, MAINFONT, txt, img = STORY.Img[STORY.Type=="Bloc"].iloc[0])
        pygame.display.flip()
        waitforkey(CONTINUE_KEY)

    if block in ["1","2","3"]:
        txt = "Maintenant on commence une grande compétition.\n\nAppuie sur entrée pour continuer."
        text_screen(SCREEN,MAINFONT,txt, img = STORY.Img[STORY.Type=="Bloc"].iloc[0])
        pygame.display.flip()
        waitforkey(CONTINUE_KEY)


###################################################################################################
# Some methods do deal with current participant name over protocoles and update experiement state #
###################################################################################################

def update_participant_proto_state(proto_participant_file, MLP_starting_time=None, MLP_i_trial=None, MLP_i_block=None, MLP_nb_run=None):
    """
    Read or init the partipant file before updating it

    Parameters
    ----------
    proto_participant_file: str
        the filename for storing current state for participant
    MLP_starting_time: str
        the date when the experiment was restarted in %d/%m/%Y %H:%M:%S format
        When set, the number or run is updated (+1) unless MLP_nb_run is also set
    MLP_i_trial : int
        the last trial run if we want to update it or None
    MLP_i_block : int
        the last bloc run if we want to update it or None
    MLP_nb_run : int
        the number of times the experiment was relounched if we want to set it
    Returns
    -------
    currentDico: a python dictionnary coding for updated state with 4 keys:
        MLP_starting_time,
        MLP_i_trial,
        MLP_i_block,
        MLP_nb_run
    """
    #if the file exists, get the content
    if os.path.isfile(proto_participant_file):
        with open(proto_participant_file,"r",encoding="utf8") as file:
            textdic = file.read()
        currentDico = eval(textdic)

        #update parameters if necessary
        if MLP_starting_time != None:
            currentDico['MLP_starting_time'] = MLP_starting_time
            currentDico['MLP_nb_run']+=1
        if MLP_i_block != None:
            currentDico['MLP_i_block'] = MLP_i_block
            currentDico['MLP_i_trial'] = 0
        if MLP_i_trial != None:
            currentDico['MLP_i_trial'] = MLP_i_trial
        if MLP_nb_run != None:
            currentDico['MLP_nb_run'] = MLP_nb_run
    else:
    # if the file does not exist, create it from scratch
        if MLP_starting_time is None:
            MLP_starting_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        currentDico = { "MLP_starting_time" : MLP_starting_time,
                        "MLP_i_trial" : 0,
                        "MLP_i_block" : 0,
                        "MLP_nb_run" : 1
                    }

    #write or rewrite the dict
    with open(proto_participant_file,"w", encoding="utf8") as file:
        file.write(f"{currentDico}")

def input_with_default(prompt, default):
    """ Prompt for imput with default value. """
    return input(f"{prompt} [{default}]: ").strip() or default

def get_last_participant(current_participant_file):
    """ Read participant code in participant file. """
    with open(current_participant_file, "r", encoding="utf-8") as file:
        last_participant = file.read()
    return last_participant

def set_last_participant(current_participant_file, participant):
    """ Write participant code in participant file, erasing previous content. """
    with open(current_participant_file, 'w', encoding="utf-8") as file:
        file.write(participant)

###################################################################################################
#             Adjust global variables with command line parameters and run experiment             #
###################################################################################################
P = Path(sys.argv[0])
# Write data in current dir/data or fallback to script dir/../data
D = Path(PATH_DATA)
if not D.exists():
    D = P.parent.parent.joinpath('data')
PATH_DATA = str(D)

# Parse command-line args
while len(sys.argv) > 2:
    v = sys.argv.pop()
    c = sys.argv.pop()
    if c == '--display':
        DISPLAYNUM = int(v)
    elif (c == '--story') & Path(v).is_dir():
        PATH_STORY = v
    elif (c == '--data') & Path(v).is_dir():
        PATH_DATA = v
    elif c == '--participant':
        PARTICIPANT = v
    elif c == '--start':
        START_BLOCK = int(v)
    else:
        print('usage : ',
          Path(sys.argv[0]).name,
          '[--display displaynum] \\ \n',
          '[--story path_to_story_directory]  \\ \n',
          '[--data path_to_data_directory]  \\ \n',
          '[--participant particpant_code]  \\ \n',
          '[--start block_num] ',
          '\n\n\n')
        raise ValueError('Unknown option : ' + c)

STORY = pd.read_excel(PATH_STORY + '/story.xlsx')


# For multi-protocol gestion: propose the last current participant name
# and update Participant.protocol state among the experiment
CURRENT_PARTICIPANT_FILE = PATH_GESTION_META_PROTO + 'current_participant.txt'
LAST_PARTICIPANT = get_last_participant(CURRENT_PARTICIPANT_FILE)

PARTICIPANT=""
while len(PARTICIPANT) == 0:
    PARTICIPANT = input_with_default("Participant: ", LAST_PARTICIPANT)

# Create log file for participant
fh = logging.FileHandler(f"{PATH_DATA}/{PARTICIPANT}-pitchtask-{datetime.now():%Y%m%d-%H%M%S}.log")
fh.setLevel(logging.DEBUG) # or any level you want
fh.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
logger.addHandler(fh)
logger.info("Participant: %s", PARTICIPANT)
set_last_participant(CURRENT_PARTICIPANT_FILE, PARTICIPANT)

PROTO_PARTICIPANT_FILE = PATH_GESTION_META_PROTO_WD + PARTICIPANT + '_MLP_pitch.txt'
update_participant_proto_state(PROTO_PARTICIPANT_FILE, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


# Recover from previous run
if START_BLOCK == -1:
    D = Path(PATH_DATA)
    for csv in D.glob(f"{PARTICIPANT}-pitchtask-{datetime.now():%Y%m%d}*.csv"):
        START_BLOCK = START_BLOCK + 1
    if START_BLOCK > -1:
        # no data saved for "try" block
        START_BLOCK = START_BLOCK + 1
    START_BLOCK = min(START_BLOCK, 1)

SCREEN, MAINFONT = init()

if START_BLOCK==-1:
    instruct()

blocks = ALL_BLOCKS[(START_BLOCK+1):]
for b in blocks:
    show_instructions(b)
    update_participant_proto_state(PROTO_PARTICIPANT_FILE, MLP_i_block=ALL_BLOCKS.index(b))
    runblock(b, PARTICIPANT)

ending()
