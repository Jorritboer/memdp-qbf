from z3 import *


def get_solver(MEMDP):
    states = list(range(len(MEMDP["MDPs"][0])))
    actions = list(MEMDP["MDPs"][0][states[0]].keys())
    environments = list(range(len(MEMDP["MDPs"])))
    phases = list(range(0, len(environments)))
    K = len(states)

    # defining the variables

    # phase 2 state 0 action a -> 2A0_a
    def getActions(phase):
        Actions = []
        for state in states:
            Actions.append({})
            for action in actions:
                Actions[state][action] = Bool(
                    str(phase) + "A" + str(state) + "_" + str(action)
                )
        return Actions

    def flattenActions(Actions):
        FlatActions = []
        for state in states:
            for action in actions:
                FlatActions.append(Actions[state][action])
        return FlatActions

    # phase 2 environment 1 state 2 => 2S1_2
    def getStates(phase):
        States = []
        for env in environments:
            l = []
            for state in states:
                l.append(Bool(str(phase) + "S" + str(env) + "_" + str(state)))
            States.append(l)
        return States

    def flattenStates(States):
        FlatStates = []
        for env in environments:
            for state in states:
                FlatStates.append(States[env][state])
        return FlatStates

    # phase 2 environment 0 state 1 path length 5 => 2P0_1_5
    def getPaths(phase):
        Paths = []
        for env in environments:
            l = []
            for state in states:
                ll = []
                for k in range(K + 1):
                    ll.append(
                        Bool(
                            str(phase)
                            + "P"
                            + str(env)
                            + "_"
                            + str(state)
                            + "_"
                            + str(k)
                        )
                    )
                l.append(ll)
            Paths.append(l)
        return Paths

    def flattenPaths(Paths):
        FlatPaths = []
        for env in environments:
            for state in states:
                for k in range(K + 1):
                    FlatPaths.append(Paths[env][state][k])
        return FlatPaths

    # phase 2 state 1 action a state 2 => 2T1_a_2
    def getTransitions(phase):
        Transitions = [{} for _ in range(len(states))]
        for state1 in states:
            o = {}
            for action in actions:
                ll = [None for _ in range(len(states))]
                for env in environments:
                    for state2 in MEMDP["MDPs"][env][state1][action]:
                        if any(  # is there any environment in which this transition does not exist?
                            [  # if not it will never gain any knowledge
                                state2 not in MEMDP["MDPs"][env2][state1][action]
                                for env2 in environments
                            ]
                        ):
                            ll[state2] = Bool(
                                str(phase)
                                + "T"
                                + str(state1)
                                + "_"
                                + str(action)
                                + "_"
                                + str(state2)
                            )
                o[action] = ll
            Transitions[state1] = o
        return Transitions

    def flattenTransitions(Transitions):
        FlatTransitions = []
        for state1 in states:
            for action in actions:
                for state2 in states:
                    t = Transitions[state1][action][state2]
                    if not t == None:
                        FlatTransitions.append(t)
        return FlatTransitions

    def getReveals(phase):
        index = 0
        Reveals = [{} for _ in range(len(states))]
        for state1 in states:
            o = {}
            for action in actions:
                ll = [None for _ in range(len(states))]
                for env in environments:
                    for state2 in MEMDP["MDPs"][env][state1][action]:
                        if ll[state2] == None:
                            ll[state2] = index
                            index += 1
                o[action] = ll
            Reveals[state1] = o
        return Reveals

    # clauses 1,3,4,5 are identical for each phase so we make a function to make those
    def clause1(Actions):
        clause = []
        for state in states:
            a = []
            for action in actions:
                a.append(Actions[state][action])
            clause.append(Or(a))
        return clause

    def clause3(States, Paths):
        clause = []
        for env in environments:
            for state in states:
                clause.append(Implies(States[env][state], Paths[env][state][K]))
        return clause

    def clause4(Paths):
        clause = []
        for env in environments:
            for target in MEMDP["winning"][env]:
                for k in range(K + 1):
                    clause.append(Paths[env][target][k])
        return clause

    def clause5(Paths):
        clause = []
        for env in environments:
            for state in states:
                if not state in MEMDP["winning"][env]:
                    clause.append(Not(Paths[env][state][0]))
        return clause

    solver = Solver()

    # variables per phase
    PhaseActions = []
    PhaseStates = []
    PhasePaths = []
    PhaseTransitions = []
    PhaseReveals = []

    phaseClauses = []

    for phase in phases:
        Actions = getActions(phase)
        States = getStates(phase)
        Paths = getPaths(phase)
        Transitions = getTransitions(phase)
        Reveals = getReveals(phase)
        R = Int("R" + str(phase))

        clauses = []
        clauses += clause1(Actions)

        # clause 2, different for last phase
        if phase < len(phases) - 1:
            for env in environments:
                for state1 in states:
                    for action in actions:
                        for state2 in MEMDP["MDPs"][env][state1][action]:
                            if Transitions[state1][action][state2] is not None:
                                clauses.append(
                                    Implies(
                                        And(
                                            States[env][state1], Actions[state1][action]
                                        ),
                                        Or(
                                            States[env][state2],
                                            Transitions[state1][action][state2],
                                        ),
                                    )
                                )
                            else:
                                clauses.append(
                                    Implies(
                                        And(
                                            States[env][state1], Actions[state1][action]
                                        ),
                                        States[env][state2],
                                    ),
                                )
        else:
            for env in environments:
                for state1 in states:
                    for action in actions:
                        for state2 in MEMDP["MDPs"][env][state1][action]:
                            clauses.append(
                                Implies(
                                    And(States[env][state1], Actions[state1][action]),
                                    States[env][state2],
                                )
                            )

        clauses += clause3(States, Paths)
        clauses += clause4(Paths)
        clauses += clause5(Paths)

        # clause 6, different for last phase
        if phase < len(phases) - 1:
            for env in environments:
                for state1 in states:
                    for k in range(1, K + 1):
                        action_disjunction = []
                        for action in actions:
                            state_disjunction = []
                            for state2 in MEMDP["MDPs"][env][state1][action]:
                                if Transitions[state1][action][state2] is not None:
                                    state_disjunction.append(
                                        Or(
                                            Paths[env][state2][k - 1],
                                            Transitions[state1][action][state2],
                                        )
                                    )
                                else:
                                    state_disjunction.append(Paths[env][state2][k - 1])
                            action_disjunction.append(
                                And(Actions[state1][action], Or(state_disjunction))
                            )
                        clauses.append(Paths[env][state1][k] == Or(action_disjunction))
        else:
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
                        clauses.append(Paths[env][state1][k] == Or(action_disjunction))

        # clause 7 for first phase
        if phase == 0:
            for start_state in MEMDP["starting"]:
                for env in environments:
                    clauses.append(States[env][start_state])
        else:  # clause 8 for later phases
            for env in environments:
                for state1 in states:
                    for action in actions:
                        for state2 in MEMDP["MDPs"][env][state1][action]:
                            if (
                                PhaseTransitions[phase - 1][state1][action][state2]
                                is not None
                            ):
                                clauses.append(
                                    Implies(
                                        And(
                                            [
                                                PhaseTransitions[phase - 1][state1][
                                                    action
                                                ][state2],
                                                R == Reveals[state1][action][state2],
                                                PhaseStates[phase - 1][env][state1],
                                                PhaseActions[phase - 1][state1][action],
                                            ]
                                        ),
                                        States[env][state2],
                                    )
                                )

        phaseClauses.append(clauses)

        PhaseActions.append(Actions)
        PhaseStates.append(States)
        PhasePaths.append(Paths)
        PhaseTransitions.append(Transitions)
        PhaseReveals.append(R)

    # First phase clauses aren't bound so can be added immediately
    solver.add(phaseClauses[0])

    # add last phase clauses because those don't include T variables
    phase = len(phases) - 1
    R = PhaseReveals[phase]
    quantifiedClauses = ForAll(
        R,
        Exists(
            flattenActions(PhaseActions[phase])
            + flattenStates(PhaseStates[phase])
            + flattenPaths(PhasePaths[phase]),
            And(phaseClauses[phase]),
        ),
    )

    # rest of clauses:
    # In reverse order because we start with the last clause
    # and add the quantifiers backwards. So we get
    # ∀∃ phase 1 ... ∀∃ phase n [combinedclauses]
    for phase in list(reversed(phases))[1:-1]:
        R = PhaseReveals[phase]
        quantifiedClauses = ForAll(
            R,
            Exists(
                flattenActions(PhaseActions[phase])
                + flattenStates(PhaseStates[phase])
                + flattenPaths(PhasePaths[phase])
                + flattenTransitions(PhaseTransitions[phase]),
                And(
                    And(phaseClauses[phase]),
                    Implies(
                        Or(flattenTransitions(PhaseTransitions[phase])),
                        quantifiedClauses,
                    ),
                ),
            ),
        )

    solver.add(quantifiedClauses)

    def policy(model):
        policy = ""
        for state in states:
            a = []
            for action in actions:
                if model[PhaseActions[0][state][action]]:
                    a.append(action)
            policy += f"State {str(state)}: {a}\n"
        for t in flattenTransitions(PhaseTransitions[0]):
            if model[t]:
                policy += f"{t}\n"
        return policy

    return solver, policy
