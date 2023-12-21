import pythonmlp

mlp = pythonmlp.MLP(
    # The slope of our psychometric curves
    slope = .1,
    
    # The minimum and maximum of the hypothesised thresholds
    hyp_min = 0,
    hyp_max = 200,
    
    # The number of hypotheses
    hyp_n = 200,
    
    # Our false alarm rates (these will be crossed with the threshold hypotheses)
    fa = [0.,.1,.2,.3,.4],
)

mlp.print()


x = mlp.next_stimulus()
print("Presenting stimulus {}".format(x))

mlp.update(x,True)

mlp.print()

print("Target p value {}".format(mlp.calculate_target()))


mlp.plot()



x = mlp.next_stimulus()
print("Presenting stimulus {}".format(x))





#pythonmlp.pyes()
