# PythonMLP

A python implementation of the Maximum Likelihood Procedure to establish psychophysical thresholds.



## Usage

This allows you to run the MLP procedure. It's like a psychophysical staircase except that it estimates the participants' psychometric curve online and uses that estimate to choose which stimulus to present.

You first create an MLP object. Suppose you have a stimulus intensity dimension. This could be the intensity of a light shown, or the loudness of a sound, or the contrast of a visual grating. Let's call that dimension x. Now we hypothesize that for low intensities, participants will not preceive it. For high intensities, they will. So their responses (detect or not) can be described by a psychometric curve. MLP will try to estimate this psychometric curve. It does so by entertaining a series of candidate (hypothetical) psychometric curve and seeing which one fits the data best.

In the call below, we create an MLP object and we specify that we want 200 hypothetical psychometric curves with midpoints between 0 and 200 stimulus intensity. The slope is fixed at 0.1 so it's the same for all hypothetical psychometric curves. Now sometimes participants make little mistakes. They give a different answer than what they intended, or due to an attentional glitch, they miss a stimulus they should have perceived. The rate at which this happens is called the false alarm rate. Here we hypothesize it is any of 0%, 10%, 20%, 30% or 40%.


```python
import pythonmlp

mlp = pythonmlp.MLP(
    
    # The minimum and maximum of the hypothesised thresholds
    hyp_min = 0,
    hyp_max = 200,
    
    # The number of hypotheses
    hyp_n = 200,

    # The slope of our psychometric curves
    slope = .1,
    
    # Our false alarm rates (these will be crossed with the threshold hypotheses)
    fa = [0.,.1,.2,.3,.4],
)

```

We can see some basic information about the newly created MLP object as follows:

```python
mlp.print()
```

Which prints this:

```
--- MLP object ---
Psychometric curve slope : 0.1
# of hypotheses: 1000
     200 midpoints between 0.000 and 200.000
     false alarm rates : 0.0, 0.1, 0.2, 0.3, 0.4

History: 0 answer(s)
# Maximum likelihood curves: 1000
    Midpoints 0.000 - 200.000, FA rates 0.0 - 0.4
    Midpoint estimate : 100.000
```

Now comes the time to present the first stimulus to your participant. What level to choose? Let's say we present a stimulus at 100 intensity, and the participant responds they have not heard it. We ask MLP to update its estimates based on this response:

```python
mlp.update(100,False)
```

Which prints:

```
--- MLP object ---
Psychometric curve slope : 0.1
# of hypotheses: 1000
     200 midpoints between 0.000 and 200.000
     false alarm rates : 0.0, 0.1, 0.2, 0.3, 0.4

History: 1 answer(s)
     prop. yes response = 0.000
# Maximum likelihood curves: 1
    Midpoints 200.000 - 200.000, FA rates 0.0 - 0.0
    Midpoint estimate : 200.000
```

So we see now only one curve is maximally likely, and it's the one with its midpoint at 200 stimulus intensity, and 0% false alarm rate.

We can ask MLP what is the next stimulus level to present to participants:

```python
mlp.next_stimulus()
```

It responds: `205.8566365333636`

So that is the next intensity to try. Let's say the participant responds that they perceived that stimulus.

```python
mlp.update(205.8566365333636,True)
mlp.print()
```

Which tells us:

```
--- MLP object ---
Psychometric curve slope : 0.1
# of hypotheses: 1000
     200 midpoints between 0.000 and 200.000
     false alarm rates : 0.0, 0.1, 0.2, 0.3, 0.4

History: 2 answer(s)
     prop. yes response = 0.500
# Maximum likelihood curves: 1
    Midpoints 152.764 - 152.764, FA rates 0.0 - 0.0
    Midpoint estimate : 152.764
```

As you can see, MLP now thinks the participant's threshold is roughly halfway between 100 and 200.

And then you can keep going like this. That's all there is to it!


Check out the `tests/` directory for an illustration of this package.






## Development

Install latest development version from Github:

```
python -m pip install --upgrade "pythonmlp @ git+https://github.com/florisvanvugt/PythonMLP"
```


Install locally:

```
pip install .
```

and editable:

```
pip install -e .
```



## Scientific references

Green, D. M. (1990). Stimulus selection in adaptive psychophysical procedures. Journal of the Acoustical Society of America, 87, 2662-2674. doi:10.1121/1.399058

Green, D. M. (1993). A maximum-likelihood method for estimating thresholds in a yes–no task. Journal of the Acoustical Society of America, 93, 2096-2105. doi:10.1121/1.406696

Gu, X., & Green, D. M. (1994). Further studies of a maximum likelihood yes–no procedure. Journal of the Acoustical Society of America, 96, 93-101. doi:10.1121/1.410378



