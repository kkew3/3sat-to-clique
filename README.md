# Introduction

`cnf2dot.py` converts Conjunctive normal form (CNF) to a graph, the process of
polynomial-time mapping reduction from 3-SAT to CLIQUE. The CNF is encoded in
JSON format.


# CNF JSON expression

CNF consists of a series of clauses. Each clause is represented by a list of 
variables and its labels. For example, clause $x1 \lor x2'$ is encoded by
`[["x1", true],["x2", false]]`; and the CNF 
$(x1 \lor x2') \land (x2 \lor x2'))$ is encoded by 
`[[["x1", true],["x2", false]],[["x2", true],["x2", false]]]`.

# Example usage

	cat example_cnf.json | ./cnf2dot.py - example_out.dot
	dot -Tpng example_out.dot -o example_out.png

# Recommended graphviz layouts for this task

- `fdp`
- `circo`
