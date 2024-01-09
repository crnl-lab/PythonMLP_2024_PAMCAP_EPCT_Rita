"""

Implementing the MLP threshold detection procedure,
as described in Green (1993 JASA) and Gu and Green (1994 JASA).
Furthermore, we'll be adding catch trials to counteract 
bias in estimating false alarm rate (e.g. Leek et al (2000 JASA)).

"""
#
import numpy as np
import random





## This is the implementation of the psychometric function
def pyes( x, a, m, k ):
    """
    Return the probability of a "yes" response,
    given the logistic psychmetric function.
     x is the stimulus intensity,
     a is the false alarm rate
     k is the slope parameter (fiddle with this so it gives the right transition range)
     m is the mean of the distribution
    """
    return a+((1-a)*(1/(1+np.exp(-k*(x-m)))))




# Ok, some quantities we can already calculate on the basis of what we have now
# For example, the target P can be computed, given that we assume no attentional
# lapses (Green 1993 JASA, eq. 6)
def optimalp( a ):
    # Return the sweetpoint p for a given false alarm rate
    return (2*a+1+np.sqrt(1+8*a))/(3+np.sqrt(1+8*a))






class MLP:
    """
    This is the object that is in charge of running the MLP algorithm.
    So it will decide the stimulus level on each trial, and keep track
    of our hypotheses.
    """



    def print(self):

        print("--- MLP object ---")
        print("Psychometric curve slope : {}".format(self.slope))
        print("# of hypotheses: {}".format(len(self.hypotheses)))
        print("     {} midpoints between {:.3f} and {:.3f}".format(self.hyp_n,self.hyp_min,self.hyp_max))
        print("     false alarm rates : {}".format(", ".join([ str(f) for f in self.fa])))
        print("")

        print("History: {} answer(s)".format(len(self.history)))
        if len(self.history):
            prop_yes = np.mean([ x['response'] for x in self.history])
            print("     prop. yes response = {:.3f}".format(prop_yes))
        
        opts = self.get_max_like()
        a_s, m_s, _ = zip(*opts)
        print("# Maximum likelihood curves: {}".format(len(opts)))
        print("    Midpoints {:.3f} - {:.3f}, FA rates {} - {}".format(min(m_s),max(m_s),min(a_s),max(a_s)))
        print("    Midpoint estimate : {:.3f}".format(self.get_midpoint_estimate()))
        print("")
              
        
        
    

    def __init__(
            self,

            # The slope of our psychometric curves
            slope, # e.g. = .1,
            
            # The minimum and maximum of the hypothesised thresholds
            hyp_min, # e.g. = 0,
            hyp_max, # e.g. = 200,

            # The number of hypotheses
            hyp_n, # e.g. = 200,
            
            # Our false alarm rates (these will be crossed with the threshold hypotheses)
            fa, # e.g. = [0.,.1,.2,.3,.4],
            
            # The number of trials
            # The number of catch trials (at the lowest stimulus level, to reduce biases in false alarm estimate)
            #NTRIALS_A        = 10
            #N_CATCH_TRIALS_A = 2
            #NTRIALS_B        = 20
            #N_CATCH_TRIALS_B = 4
    ):
        

        self.slope = slope
        self.hyp_min = hyp_min
        self.hyp_max = hyp_max
        self.hyp_n   = hyp_n

        self.fa = fa


        # The threshold hypotheses
        THRESHOLD_HYPOTHESES = np.linspace(self.hyp_min,
                                           self.hyp_max,
                                           self.hyp_n)

        # Initialise our hypotheses
        self.hypotheses = [ (a,m,1.)  # false alarm rate, threshold, and probability (initially just one)
                            for a in self.fa
                            for m in THRESHOLD_HYPOTHESES ]

        # History
        self.history = []




    def calculate_target(self):
        # Determine the tracking target, which is a target probability (p)
        # on the psychometric curve for which we'll later try to find the corresponding
        # stimulus level.

        # We calculate the optimal tracking p values for the different false alarm rates
        P_YES = [ optimalp(fa) for fa in self.fa ]
        
        # And we take the mean of these and use that as the tracking value
        TARGET_P = np.mean(P_YES) # this is the tracking p-value, i.e. the performance for which we find the stimulus value based on our current maximum likelihood estimate

        return TARGET_P


        

    def update( self, x, answer ):
        # Given a subject's answer (yes=True or no=False) to stimulus intensity x,
        # update the likelihood of the hypotheses.
        # That is, for each hypotheses, calculate the probability p of
        # that observation assuming that hypothesis.
        # Then, we multiply the likelihood of that hypothesis with p.
        # We return the new list of hypotheses.

        self.history.append({"stimulus":x,"response":answer})
        
        newhyp = []
        for (a,m,p) in self.hypotheses:

            # Calculate the likelihood of a "yes" response to this stimulus
            obsp = pyes( x, a, m, self.slope )

            # If this was a no-response, invert the probability
            if not answer:
                obsp = 1-obsp

            # And then add the hypothesis to the new list
            newhyp.append( (a,m,p*obsp) )

        self.hypotheses = newhyp






    def get_max_like(self):

        # If there are several (due to being practically equal), just choose a random one
        # among them
        # Now check for the maximum likelihood one
        maxp = max([ p for (_,_,p) in self.hypotheses ])

        # And then find the hypotheses that have this maximum
        maxlikelihyps = [ (a,m,p)
                          for (a,m,p) in self.hypotheses 
                          if p==maxp ]

        return maxlikelihyps

        

    def get_ml(self):
        """ Get the current maximum likelihood stimulus. """

        opts = self.get_max_like()
        
        # If there are several (due to being practically equal), just choose a random one
        # among them
        return random.choice( opts )




    def get_sweetpoint(
            self,
            params, 
            p
            ):
        """
        For a particular psychometric curve, return the stimulus
        level corresponding to a particular target p value.
        So this is just inverting the psychometric function.
        The psychmetric curve is as before, it is defined by the false alarm rate (a)
        and the threshold location (m).
        The target_p is a probability from 0 to 1.
        """

        (a,m,_)=params
        
        if p<=a:
            print ("Error, calculating a sweet point below the false alarm rate!")
            return None

        y = ((1-a)/(p-a))-1
        return (np.log(y)/(-self.slope))+m





    def next_stimulus(self):
        """ Decide which stimulus level to present now.
        This means essentially: deciding what is the current
        maximum likelihood hypothesis, finding its corresponding
        psychometric curve, and finding the corresponding sweet point.
        """
        
        # Get the most probable psychmetric curve
        candidate = self.get_ml()
        
        # Now we calculate the stimulus level corresponding to the "sweet point",
        # the target p-value that we track, for the maximum likelihood estimate
        stim = self.get_sweetpoint(
            candidate,
            self.calculate_target() )

        return stim




    
    def get_midpoint_estimate(self):
        """ Return the current best estimate of the psychometric curve midpoint """

        opts = self.get_max_like()
        _, m_s, _ = zip(*opts)
        return np.mean(m_s) # if there are several, just return the average






    def plot(self):

        maxp = max([ p for _,_,p in self.hypotheses ])

        import matplotlib.pyplot as plt
        import matplotlib.colors as colors
        import matplotlib.cm as cm

        stims = np.linspace(self.hyp_min,self.hyp_max,300)
        plot_thickness = 3.5
        for (a,m,p) in self.hypotheses:
            pyess = np.array([ pyes(x,a,m,self.slope) for x in stims ])
            plt.plot( stims, pyess, lw=(p/maxp)*plot_thickness,
                      color=cm.jet(p),
                      alpha=.5 )

        # Then plot the maximum likelihood estimate nice and thick in a dashed line
        for (a,m,p) in self.hypotheses:
            pyess = np.array([ pyes(x,a,m,self.slope) for x in stims ])
            if p==maxp:
                plt.plot(
                    stims, pyess, 
                    '--',
                    lw=2.5, 
                    color="black",
                    alpha=p/maxp
                )

        # Finally, we add the individual answers. The "yes" answers to on top (between 1. and 1.1)
        # the "no" answers below (between -.1 and 0.) 
        answercolor={ 0: "black",
                      1: "white" }
        for x in self.history:
            stim=x["stimulus"]
            answer=x["response"]

            if answer==1: answer=1.05
            if answer==0: answer=-.05
            plt.plot( stim, answer+random.normalvariate(0,.02),
                      'o', markersize=8, markeredgewidth=2, markeredgecolor="black",
                      markerfacecolor=answercolor[x["response"]], alpha=.8 )

        

        plt.xlabel("Stimulus level")
        plt.ylabel("Probability of saying 'yes'")
        plt.show()




    def plot_hypotheses(self):

        maxp = max([ p for _,_,p in self.hypotheses ])

        fas = list(set([ a for (a,_,_) in self.hypotheses ]))
        ms  = list(set([ m for (_,m,_) in self.hypotheses ]))
        fas.sort()
        ms.sort()
        
        print("Hello!")

        import numpy as np
        import matplotlib.pyplot as plt
        
        data = np.zeros( (len(fas),len(ms)) )
        for (a,m,p) in self.hypotheses:
            fi = fas.index(a)
            mi = ms.index(m)
            data[fi,mi]=p
            
        # Heat map
        fig, ax = plt.subplots()
        im = ax.imshow(
            data,aspect='auto',interpolation='none',
            #origin = 'lower',
            #extent = [min(ms), max(ms),
            #          min(fas), max(fas)]
        )
        
        # Add the color bar
        cbar = ax.figure.colorbar(im, ax = ax)
        cbar.ax.set_ylabel("Probability", rotation = -90, va = "bottom")

        # Axis labels
        plt.yticks( range(len(fas)), fas)
        #plt.xticks( range(len(ms)), ms)
        plt.xlabel("Hypothesis curve midpoint")
        plt.ylabel("False alarm rate")
        
        plt.show()




