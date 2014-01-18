import pygraphviz as pgv

def draw_model(M, filename):
    G = pgv.AGraph(strict = False, directed = True)
    G.add_nodes_from(M.W)
    G.add_edges_from(M.R)
    G.layout(prog='dot')
    G.draw(filename)
