
""" 
This is an example script that shows how to run the
python implementation of MLP.

First you have to create a task (here just a null task that
asks you for a response). You then feed this to the run()
method of an MLP object, and it will run the given task.
"""

from mlpcore.task           import *
from mlpcore.mlp            import MLP



task = Task()
mlp = MLP()

mlp.run( task )


