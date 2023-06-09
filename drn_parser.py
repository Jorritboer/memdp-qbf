import re
import os


# assumptions about memdp:
# every state has the same actions
# states are integers and denoted by index
# every environment has the same states, actions
# starting states are same in all envs
# goal states are absorbing
def read_mdp(file):
    line = file.readline()
    while not re.search("@nr_states", line):
        line = file.readline()

    nr_states = int(file.readline())

    while not re.search("@model", line):
        line = file.readline()

    MDP = [{} for _ in range(nr_states)]
    starting = []
    winning = []

    line = file.readline()
    # Read states
    while match := re.search("state\s(\d+)", line):
        state = int(match.group(1))
        if re.search("init", line):
            starting.append(state)
        elif re.search("win|target", line):
            winning.append(state)

        line = file.readline()
        while line.startswith("//"):  # skip comments
            line = file.readline()
        # Read actions
        while match := re.search("action\s(\w+)", line.strip()):
            action = match.group(1)
            line = file.readline()
            # Read transitions
            while match := re.search("(\d+)\s*:\s*\d+", line.strip()):
                transition = int(match.group(1))
                if not action in MDP[state]:
                    MDP[state][action] = []
                MDP[state][action].append(transition)
                line = file.readline()

    return MDP, starting, winning


# Read all drn files in directory as environments
def read_memdp(dir):
    MEMDP = {"starting": [], "winning": [], "MDPs": []}
    for file in sorted(os.listdir(dir)):
        if file.endswith(".drn"):
            path = os.path.join(dir, file)
            with open(path, "r") as file:
                MDP, starting, winning = read_mdp(file)
                MEMDP["starting"] = starting
                MEMDP["winning"].append(winning)
                MEMDP["MDPs"].append(MDP)
    return MEMDP
