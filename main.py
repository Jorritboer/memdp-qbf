from z3 import unsat, unknown
import sat
import qbf
import drn_parser
import argparse

parser = argparse.ArgumentParser(
    description="MEMDP Almost-Sure Reachability QBF/SAT Formula"
)
parser.add_argument("memdps", nargs="+", help="directories of memdps to process")
parser.add_argument(
    "-f", "--formula", choices=["sat", "qbf"], default="qbf", help="sat or qbf"
)
parser.add_argument("-t", "--timeout", type=int, help="Timeout in seconds")
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument(
    "-e",
    "--expression",
    action="store_true",
    help="If this flag is set, the expression for each memdp is written to a expression.txt file in the directory",
)
parser.add_argument("-p", "--phases", type=int, help="Number of phases, (only for QBF)")

args = parser.parse_args()

# only prints if args.verbose
verboseprint = print if args.verbose else lambda *a, **k: None

print("=================")
print(f"{args.formula} timeout={args.timeout}")
print("=================")

for dir in args.memdps:
    verboseprint("reading drn files")
    memdp = drn_parser.read_memdp(dir)

    verboseprint("generating formulas")
    if args.formula == "qbf":
        solver, policy = qbf.get_solver(memdp, args.phases)
    else:
        solver, policy = sat.get_solver(memdp)

    if args.expression:
        with open(dir + "/expr.txt", "w") as f:
            f.write(solver.sexpr())

    verboseprint("------")
    verboseprint("checking")
    print(dir, end="")

    if args.timeout:
        solver.set("timeout", args.timeout * 1000)  # s -> ms
    check = solver.check()
    time = solver.statistics().get_key_value("time")
    if check == unsat:
        print(f":\tunsat\t{time}")
    elif check == unknown:
        print(f":\ttimeout\t{time}")
    else:
        print(f":\tsat\t{time}")
        verboseprint(policy(solver.model()))
