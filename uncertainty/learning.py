from pomegranate import*

rain = DiscreteDistribution({'yes': 0.2, 'no': 0.8})
sprinkler = ConditionalProbabilityTable([
    ['yes', 'on', 0.01],
    ['yes', 'off', 0.99],
    ['no',  'on', 0.4],
    ['no',  'off', 0.6]
], [rain])
wetgrass = ConditionalProbabilityTable([
    ['yes', 'on', 'wet', 1],
    ['yes', 'on', 'dry', 0],
    ['yes', 'off', 'wet', 1],
    ['yes', 'off', 'dry', 0],
    ['no',  'on', 'wet', 1],
    ['no',  'on', 'dry', 0],
    ['no',  'off', 'wet', 0],
    ['no',  'off', 'dry', 1]
], [rain, sprinkler])

rain_state = State(rain, name='rain')
sprinkler_state = State(sprinkler, name='sprinkler')
wetgrass_state = State(wetgrass, name='wetgrass')

network = BayesianNetwork("Weather")
network.add_states(rain_state, sprinkler_state, wetgrass_state)
network.add_edge(rain_state, sprinkler_state)
network.add_edge(sprinkler_state, wetgrass_state)
network.add_edge(rain_state, wetgrass_state)

network.bake()

beliefs = network.predict_proba({'wetgrass': 'wet', 'sprinkler': 'off'})
for state, belief in zip(network.states, beliefs):
    print(f"{state.name}: {belief}")
