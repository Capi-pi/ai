from pomegranate import *

rain = DiscreteDistribution({'yes': 0.2, 'no': 0.8})
sprinkler = ConditionalProbabilityTable([
    ['yes', 'on', 0.01],
    ['yes', 'off', 0.99],
    ['no',  'on', 0.4],
    ['no',  'off', 0.6]
], [rain])

print(rain, sprinkler, sep='\n')