from z3 import *

# assumptions about memdp:
# every state has the same actions
# states are integers and denoted by index
# every environment has the same states, actions
# starting and winning states are same in all envs
# goal states are absorbing
def get_solver(MEMDP):
    states = list(range(len(MEMDP["MDPs"][0])))
    actions = list(MEMDP["MDPs"][0][states[0]].keys())
    environments = list(range(len(MEMDP["MDPs"])))
    K = len(states)

    # defining the variables

    # state 0 action a -> A0,a
    Actions = []
    for state in states:
        Actions.append({})
        for action in actions:
            Actions[state][action] = Bool("A" + str(state) + "_" + str(action))

    # environment 1 state 2 => S1,2
    States = []
    for env in environments:
        l = []
        for state in states:
            l.append(Bool("S" + str(env) + "_" + str(state)))
        States.append(l)

    # environment 0 state 1 path length 5 => P0,1,5
    Paths = []
    for env in environments:
        l = []
        for state in states:
            ll = []
            for k in range(K + 1):
                ll.append(Bool("P" + str(env) + "_" + str(state) + "_" + str(k)))
            l.append(ll)
        Paths.append(l)

    # clauses
    s = Solver()
    # clause 1
    for state in states:
        a = []
        for action in actions:
            a.append(Actions[state][action])
        s.add(Or(a))

    # clause 2
    for env in environments:
        for state1 in states:
            for action in actions:
                for state2 in MEMDP["MDPs"][env][state1][action]:
                    s.add(
                        Implies(
                            And(States[env][state1], Actions[state1][action]),
                            States[env][state2],
                        )
                    )

    # clause 3
    for start_state in MEMDP["starting"]:
        for env in environments:
            s.add(States[env][start_state])

    # clause 4
    for env in environments:
        for state in states:
            s.add(Implies(States[env][state], Paths[env][state][K]))

    # clause 5
    for env in environments:
        for target in MEMDP["winning"]:
            for k in range(K + 1):
                s.add(Paths[env][target][k])

    # clause 6
    for env in environments:
        for state1 in states:
            for k in range(1, K + 1):
                action_disjunction = []
                for action in actions:
                    state_disjunction = []
                    for state2 in MEMDP["MDPs"][env][state1][action]:
                        state_disjunction.append(Paths[env][state2][k - 1])
                    action_disjunction.append(
                        And(Actions[state1][action], Or(state_disjunction))
                    )
                s.add(Paths[env][state1][k] == Or(action_disjunction))

    # clause 7??
    for env in environments:
        for state in states:
            if not state in MEMDP["winning"]:
                s.add(Paths[env][state][0] == False)

    def print_policy(model):
        for state in states:
            a = []
            for action in actions:
                if model[Actions[state][action]]:
                    a.append(action)
            print("State " + str(state) + ":" + str(a))

    return s, print_policy
