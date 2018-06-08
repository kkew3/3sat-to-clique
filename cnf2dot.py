#!/usr/bin/python
import sys
import argparse
import json
from collections import namedtuple
from itertools import combinations

# cid: integer
# nodes: semicolon-separated node lists
node_group_templ = '''subgraph cluster_{cid} {{
    color = blue;
    label = "clause #{cid}";
    node [style = filled];
    
    {nodes}
}}'''

# nodegroups: semicolon-separated node group definitions
# edges: semicolon-separated edge definitions
dot_templ = '''graph G {{
    edge [splines = false];

    {nodegroups}

    {edges}
}}'''


def make_parser():
    parser = argparse.ArgumentParser(description='Convert CNF to dot file')
    parser.add_argument('cnf', help='the CNF expression in JSON, or \'-\' '
                        'to read from stdin')
    parser.add_argument('out', help='the outfile name')
    parser.add_argument('-c', action='store_true', help='with cluster id '
                        'in node label; for example, "x1" in cluster 2 '
                        'will be denoted as "x1_2"; default False')
    return parser


VarValue = namedtuple('VarValue', ['name', 'tf'])


class CNFClause(object):
    def __init__(self, cid, clause, with_cid=False):
        """
        :param cid: integer cluster id
        :param clause: list of (name, True/False) tuples
        :param with_cid: whether to include cid in node label
        """
        self.var_values = map(lambda x: VarValue(*x), clause)
        self.cid = cid
        self.with_cid = with_cid
    
    def var2literal(self, vid):
        return 'n{}_{}'.format(self.cid, vid)

    def var2label(self, vid):
        var_name, val = self.var_values[vid]
        label =  '{}{}'.format(var_name, '' if val else "'")
        if self.with_cid:
            label += '_{}'.format(self.cid)
        return label

    def __len__(self):
        return len(self.var_values)

    @property
    def dot_nodes(self):
        var_literals = map(self.var2literal, range(len(self.var_values)))
        var_labels = map(self.var2label, range(len(self.var_values)))
        node_defs = map(lambda x: '{} [label = "{}"];'.format(*x),
                        zip(var_literals, var_labels))
        return '\n'.join(node_defs)


def dot_edge(cl1, vid1, cl2, vid2):
    return '{} -- {};'.format(cl1.var2literal(vid1),
                              cl2.var2literal(vid2))

def _get_dot_edges_2clauses(cl1, cl2):
    """
    Connect from each node in cl1 to cl2.
    """
    edge_defs = list()
    for vid1, vv1 in enumerate(cl1.var_values):
        for vid2, vv2 in enumerate(cl2.var_values):
            if not (vv1.name == vv2.name and vv1.tf != vv2.tf):
                edge_defs.append(dot_edge(cl1, vid1, cl2, vid2))
    return edge_defs

def get_dot_edges(clauses):
    edge_defs = list()
    for cl1, cl2 in combinations(clauses, 2):
        edge_defs.append('# group{} -> group{}'.format(cl1.cid, cl2.cid))
        edge_defs.extend(_get_dot_edges_2clauses(cl1, cl2))
    return edge_defs

def get_dot_subgraph(cl):
    return node_group_templ.format(cid=cl.cid, nodes=cl.dot_nodes)

def get_dot_file(nodegroups, edge_defs):
    return dot_templ.format(nodegroups='\n'.join(nodegroups),
                            edges='\n'.join(edge_defs))


def main():
    args = make_parser().parse_args()
    if args.cnf == '-':
        if not sys.stdin.isatty():
            args.cnf = sys.stdin.read().strip()
        else:
            print >> sys.stderr, 'CNF expression not found in stdin'
            sys.exit(1)
    cnf = json.loads(args.cnf)
    clauses = [CNFClause(*x, with_cid=args.c) for x in enumerate(cnf)]
    nodegroups = map(get_dot_subgraph, clauses)
    edge_defs = get_dot_edges(clauses)
    dot_content = get_dot_file(nodegroups, edge_defs)
    with open(args.out, 'w') as outfile:
        outfile.write(dot_content)


if __name__ == '__main__':
    main()
