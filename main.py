from z3 import unsat, set_param
import sat
import qbf
import drn_parser

dirs = [
    # "example_drns/ex1",
    # "example_drns/ex2",
    # "example_drns/sat1",
    # "example_drns/memory",
    # "example_drns/mem2test",
    "example_drns/test",
]
for dir in dirs:
    memdp = drn_parser.read_memdp(dir)

    solver, print_policy = qbf.get_solver(memdp)

    with open(dir + "/expr.txt", "w") as f:
        f.write(solver.sexpr())

    print("------")
    print(dir)
    # set_param(verbose=2)
    if solver.check() == unsat:
        print("not satisfiable")
    else:
        model = solver.model()
        print_policy(model)
        print(solver.statistics())
