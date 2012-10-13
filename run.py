

from task           import *
from hydeperetztask import *
from ehrlesamson    import * 
#from agencytask     import *
from mlp            import MLP



task = EhrleSamson()
#task = HydePeretz()
#task = AgencyTask()
mlp = MLP()

mlp.run( task )


