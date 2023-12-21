

# Here we simulate a basic psychometric curve
# and see if PythonMLP can correctly identify it.

# The ground truth
TRUTH_A = .1
TRUTH_M = 50
TRUTH_S = .1

import numpy as np
import pythonmlp
import pandas as pd

def answer(x):
    p = pythonmlp.pyes(x,TRUTH_A,TRUTH_M,TRUTH_S)
    return(np.random.uniform()<p) # transform into true or false


N = 30
for stim in [0,50,100,200]:
    resps = [ answer(stim) for _ in range(N) ]
    print("stimulus {} : proportion yes {:.2f}".format(stim,np.mean(resps)))



MAXSTIM = 200
    
mlp = pythonmlp.MLP(

    # The slope of our psychometric curves
    slope = TRUTH_S, # this is a cheat, we give the real psychometric curve slope...
    
    # The minimum and maximum of the hypothesised thresholds
    hyp_min = 0,
    hyp_max = MAXSTIM,
    
    # The number of hypotheses
    hyp_n = 200,
    
    # Our false alarm rates (these will be crossed with the threshold hypotheses)
    fa = [0.,.1,.2,.3,.4],
)



# Now let's simulate trials

stim = MAXSTIM # start at the maximum level

trials = []
for trial in range(50):

    stim = stim if stim>0 else 0 # set to 0 if lower
    ans = answer(stim)
    mlp.update(stim,ans)
    trials.append({
        "trial":trial,
        "stimulus":stim,
        "response":ans
        })
    stim = mlp.next_stimulus()
        

print(pd.DataFrame(trials))
mlp.print()

m = mlp.get_midpoint_estimate()
print("Midpoint estimate : {}  vs. ground truth : {}".format(m,TRUTH_M))
