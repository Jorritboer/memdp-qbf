from z3 import unsat
import sat
import drn_parser

dir = input("directory:")
memdp = drn_parser.read_memdp(dir)

solver, print_policy = sat.get_solver(memdp)

if solver.check() == unsat:
    print("not satisfiable")
else:
    model = solver.model()
    print_policy(model)
