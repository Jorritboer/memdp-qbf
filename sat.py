from z3 import *


def get_solver(MEMDP):
    states = list(range(len(MEMDP["MDPs"][0])))
    actions = list(MEMDP["MDPs"][0][states[0]].keys())
    environments = list(range(len(MEMDP["MDPs"])))
    K = len(states)

    # defining the variables

    # state 0 action a -> A0_a
    Actions = []
    for state in states:
        Actions.append({})
        for action in actions:
            Actions[state][action] = Bool("A" + str(state) + "_" + str(action))

    # environment 1 state 2 => S1_2
    States = []
    for env in environments:
        l = []
        for state in states:
            l.append(Bool("S" + str(env) + "_" + str(state)))
        States.append(l)

    # environment 0 state 1 path length 5 => P0_1_5
    Paths = []
    for env in environments:
        l = []
        for state in states:
            l.append(Int("P" + str(env) + "_" + str(state)))
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
            s.add(Implies(States[env][state], Paths[env][state] <= K))

    # clause 5
    for env in environments:
        for target in MEMDP["winning"][env]:
            s.add(Paths[env][target] == 0)

    # clause 6
    for env in environments:
        for state in states:
            if not state in MEMDP["winning"][env]:
                s.add(Paths[env][state] > 0)

    # clause 7
    for env in environments:
        for state1 in states:
            # for a winning state s, Ps is not equal to a successor + 1
            if not state1 in MEMDP["winning"][env]:
                action_disjunction = []
                for action in actions:
                    state_disjunction = []
                    for state2 in MEMDP["MDPs"][env][state1][action]:
                        state_disjunction.append(
                            Paths[env][state1] == (Paths[env][state2] + 1)
                        )
                    action_disjunction.append(
                        And(Actions[state1][action], Or(state_disjunction))
                    )
                s.add(
                    Or(Or(action_disjunction), Paths[env][state1] == (K + 1))
                )  # P=K+1 means unreachable

    def policy(model):
        policy = ""
        for state in states:
            a = []
            for action in actions:
                if model[Actions[state][action]]:
                    a.append(action)
            policy += f"State {str(state)}: {a}\n"
        return policy

    return s, policy
