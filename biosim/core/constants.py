# Node Limits
MAX_NEURONS = 10

# Sensor Indices
S_LOC_X, S_LOC_Y, S_RANDOM, S_LAST_MOVE_X, S_LAST_MOVE_Y, S_OSC, \
S_DIST_BARRIER_FWD, S_DIST_SAFE_FWD, S_DENS_AGENTS_FWD = range(9)
NUM_SENSORS = 9

# Action Indices
# Removed Colors. Only Movement remains.
A_MOVE_X, A_MOVE_Y, A_MOVE_FWD = range(3)
NUM_ACTIONS = 3

# World
BARRIER = -1 

# Labels
SENSOR_NAMES = {
    0: "LocX", 1: "LocY", 2: "Rnd", 
    3: "LmvX", 4: "LmvY", 5: "Osc",
    6: "DstBar", 7: "DstSafe", 8: "DensAg"
}
ACTION_NAMES = {
    0: "MvX", 1: "MvY", 2: "MvFwd"
}