# Node Limits
MAX_NEURONS = 10

# Sensor Indices
S_LOC_X, S_LOC_Y, S_RANDOM, S_LAST_MOVE_X, S_LAST_MOVE_Y, S_OSC, \
S_DIST_BARRIER_FWD, S_DIST_SAFE_FWD, S_DENS_AGENTS_FWD, S_SMELL = range(10)
NUM_SENSORS = 10

# Action Indices
A_MOVE_X, A_MOVE_Y, A_MOVE_FWD, A_EMIT = range(4)
NUM_ACTIONS = 4

# World
BARRIER = -1 

# Labels
SENSOR_NAMES = {
    0: "LocX", 1: "LocY", 2: "Rnd", 
    3: "LmvX", 4: "LmvY", 5: "Osc",
    6: "DstBar", 7: "DstSafe", 8: "DensAg",
    9: "Smell"
}
ACTION_NAMES = {
    0: "MvX", 1: "MvY", 2: "MvFwd", 3: "Emit"
}
