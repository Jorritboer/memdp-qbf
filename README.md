# MEMDP AS Reachability => QBF Formula
This repository provides a reduction from MEMDP models to a QBF formula implemented in the Z3 theorem prover. 
Part of my [bachelor thesis](https://www.cs.ru.nl/bachelors-theses/2023/Jorrit_de_Boer___1026441___Solving_Robust_Reachability_Using_Quantified_Boolean_Formulas.pdf). 

## Usage
```
usage: main.py [-h] [-f {sat,qbf}] [-t TIMEOUT] [-v] [-e] [-p PHASES] memdps [memdps ...]

MEMDP Almost-Sure Reachability QBF/SAT Formula

positional arguments:
  memdps                directories of memdps to process

options:
  -h, --help            show this help message and exit
  -f {sat,qbf}, --formula {sat,qbf}
                        sat or qbf
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout in seconds
  -v, --verbose
  -e, --expression      If this flag is set, the expression for each memdp is written to a expression.txt file in the directory
  -p PHASES, --phases PHASES
                        Number of phases, (only for QBF)
```
Each MEMDP should be a directory containing `.drn` files, each of which represent one MDP in the MEMDP. 
Example `.drn` file:
```
@type: MDP
@parameters

@nr_choices
8

@nr_states
4

@model
state 0 init
    action a
        1 : 0.5
        2 : 0.5
    action b
        3 : 1
state 1
    action a
        2 : 1
    action b
        0 : 1
state 2 win
    action a
        2 : 1
    action b
        2 : 1
state 3
    action a
        3 : 1
    action b
        3 : 1
```

The `--formula` and `--phases` options are explained in my thesis. 
