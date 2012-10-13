import numpy as np
import matplotlib.pyplot as plt
import sys
import random

# Ok, so here we analyse the results of an MLP run


# Make sure that you are using the right parameters in configmlp. We don't read them from the metadata file (although they are there)
from configmlp import *
import matplotlib.colors as colors
import matplotlib.cm as cmx
cmap = plt.get_cmap('RdYlGn_r') 


def askOpenFile(dirname="."):
    """ Prompts the user to select a file """

    import Tkinter,tkFileDialog
    root = Tkinter.Tk()
    file = tkFileDialog.askopenfile(parent=root,mode='rb',title='Choose a file',initialdir=dirname)
    return file



# Ask the user to select a file
fname = askOpenFile("./data/")

if not fname:
    # If there's nothing to open...
    sys.exit(0)


dt = np.dtype( [ ('participant','S999'),
                 ('trial', 'i'),
                 ('type','S99'),
                 ('stimulus','f'),
                 ('response','i') ] )

tab = np.genfromtxt(fname,skip_header=1,dtype=dt)





# Now we plot the possible hypotheses that we have been using, coding them
# in thickness according to their likelihood
plt.figure()


# First we quickly "re-run" our analysis, taking stimulus-answer one-by-one
THRESHOLD_HYPOTHESES = np.linspace(MINHYP,MAXHYP,NHYPOTHESES)
hypotheses = [ (a,m,1.)  # false alarm rate, threshold, and probability (initially just one)
               for a in FALSE_ALARM_RATES
               for m in THRESHOLD_HYPOTHESES ]
for x in tab:
    stim=x["stimulus"]
    answer=x["response"]==1 # so that it becomes a boolean
    hypotheses = updatehypotheses( hypotheses, 
                                   stim,
                                   answer )

# Get the maximum likelihood candidate    
maxp = max([ p for (_,_,p) in hypotheses ])
cNorm  = colors.Normalize(vmin=0, vmax=maxp)
scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)

# As an intermission, plot the hypotheses
stims = np.arange(MINHYP,MAXHYP,1)
plot_thickness = 3.5
for (a,m,p) in hypotheses:
    pyess = np.array([ pyes(x,a,m) for x in stims ])
    plt.plot( stims, pyess, lw=(p/maxp)*plot_thickness, color=scalarMap.to_rgba(p), alpha=.5 )

# Then plot the maximum likelihood estimate nice and thick in a dashed line
for (a,m,p) in hypotheses:
    pyess = np.array([ pyes(x,a,m) for x in stims ])
    if p==maxp:
        plt.plot( stims, pyess, 
                  '--',
                  lw=2.5, 
                  color="black" )

# Finally, we add the individual answers. The "yes" answers to on top (between 1. and 1.1)
# the "no" answers below (between -.1 and 0.) 
answercolor={ 0: "black",
              1: "white" }
for x in tab:
    stim=x["stimulus"]
    answer=x["response"]

    if answer==1: answer=1.05
    if answer==0: answer=-.05
    plt.plot( stim, answer+random.normalvariate(0,.02),
              'o', markersize=8, markeredgewidth=2, markeredgecolor="black",
              markerfacecolor=answercolor[x["response"]], alpha=.8 )



        
plt.ylim(-.1,1.1)
plt.yticks( np.arange(0,1,.2) )
plt.ylabel("Probability of saying 'yes'")
plt.xlabel("Stimulus (duration in msec)")
plt.title("Maximum likelihood estimate of psychometric curve")







# First make an overview of the trials, like Grassi et al (2009 Behav Methods Psych) plot them
plt.figure()
plt.xlim(-1,max(tab['trial'])+1)
plt.ylim(min(tab['stimulus'])-1,max(tab["stimulus"])+1)
for (fillcol,response,responselabel) in [ ('white',1,"change heard"),
                                          ('black',0,"change not heard") ]:
    # Select just those responses
    dat = tab[ tab['response']==response ]

    for (pch,trialtype) in [ ('o','mlp'), ('s','catch') ]:

        thistr = dat[ dat['type']==trialtype ]

        plt.plot( thistr['trial'], thistr['stimulus'], pch,
                  markeredgewidth=1.5, markeredgecolor="black",
                  markerfacecolor=fillcol,
                  markersize=8,
                  label="%s %s"%(trialtype,responselabel) )

plt.legend( loc="upper right" )
plt.xlabel("Trial")
plt.ylabel("Stimulus delay (ms)")
plt.title("Asked stimuli and answers")








plt.show()

