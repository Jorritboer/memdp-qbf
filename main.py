from z3 import unsat, unknown
import sat
import qbf
import drn_parser
import sys

dir = sys.argv[1]

print("reading drn files")
memdp = drn_parser.read_memdp(dir)

print("generating formulas")
solver, print_policy = qbf.get_solver(memdp)

# with open(dir + "/expr.txt", "w") as f:
#     f.write(solver.sexpr())

print("------")
print("checking")
print(dir)

solver.set("timeout", 20000)  # ms
check = solver.check()
if check == unsat:
    print("not satisfiable")
elif check == unknown:
    print("timeout")
else:
    model = solver.model()
    print_policy(model)
print("Time:", solver.statistics().get_key_value("time"))
