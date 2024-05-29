
import datetime


class FileOutput:

    """
    This object takes care of writing what happens during a trial
    to file.
    """

    # The file object to which we keep writing each trial
    outfile = None

    # The file that contains only the "big picture" data
    metafile = None


    def __init__(self, participant, task):

        # Get basic data (e.g. participant name etc.)
        fname = "data/%s--%s.txt"%(participant, datetime.datetime.now().strftime("%d-%m.%Hh%Mm%S") )
        self.metafile = open(fname+".metadata.txt",'w')

        self.metafile.write("task                 : %s\n"%task.NAME)
        self.metafile.write("participant          : %s\n"%participant)
        self.metafile.write("slope                : %f\n"%task.SLOPE)
        self.metafile.write("min-hyp              : %f\n"%task.MINHYP)
        self.metafile.write("max-hyp              : %f\n"%task.MAXHYP)
        self.metafile.write("n.hypotheses         : %i\n"%task.NHYPOTHESES)
        self.metafile.write("false-alarm-rates    : %s\n"%( ",".join([ "%.2f"%f for f in task.FALSE_ALARM_RATES ]) ))
        self.metafile.write("target p             : %f\n"%task.TARGET_P)
        self.metafile.write("n.trials.A           : %i\n"%task.NTRIALS_A)
        self.metafile.write("n.catch trials.A     : %i\n"%task.N_CATCH_TRIALS_A)
        self.metafile.write("n.trials.B           : %i\n"%task.NTRIALS_B)
        self.metafile.write("n.catch trials.B     : %i\n"%task.N_CATCH_TRIALS_B)
        self.metafile.write("initial stim         : %f\n"%task.INITIAL_STIM)

        self.outfile = open(fname,'w')
        self.outfile.write("PARTICIPANT TRIAL TYPE STIMULUS RESPONSE\n")



    def log( self, x ):
        """ Log the result of this particular trial. """ 
        logreport = '%s %i %s %f %i\n'%x
        print logreport,
        self.outfile.write(logreport)



    def closefiles( self, likelihoodestimate ):

        # Make a little summary
        (a,m,p)=likelihoodestimate

        self.metafile.write('\n\n')
        self.metafile.write('Maximum likelihood estimate: %.2f\n'%m)
        self.metafile.write('False alarm rate estimate: %.2f\n\n'%a)

        self.metafile.close()
        self.outfile.close()



