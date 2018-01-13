#
# Generate hexagonal cellular automaton BlocksCAD code.
#

from blockscad import *
from math import *
from sys import argv

if len(argv) > 1:
    NUM_LEVELS = int(argv[1])
else:
    NUM_LEVELS = 20

def rowSize(i):
    return 1 if i == 0 else int(ceil((i+1)/2.));

def get(i,j):
    if i >= NUM_LEVELS:
        return EX(0)
    if i<0:
        return get(1,0)
    if i <= 1 and j != 0:
        return get(i,0)
    rs = rowSize(i)
    if j < 0:
        return get(i,-j)
    elif j >= rs:
        if i % 2:
            return get(i,rs-1-(j-rs))
        else:
            return get(i,rs-2-(j-rs))
    assert(0<=i and i<NUM_LEVELS and 0<=j and j<rs)
    return EX("u%d_%d" % (i,j))
    
def getNeighbors(i,j):
    rs = rowSize(i)
    if i == 0:
        return [get(1,0)]*6
    elif j < 0:
        return getNeighbors(i,-j)
    elif j >= rs:
        if i % 2:
            return getNeighbors(i,rs-1-(j-rs))
        else:
            return getNeighbors(i,rs-2-(j-rs))
    elif j == 0:
        return [get(i,1),get(i+1,1)]*2+[get(i+1,0),get(i-1,0)]
    else:
        return [get(i,j-1),get(i,j+1),get(i+1,j),get(i+1,j+1),get(i-1,j),get(i-1,j-1)]
    
def emitter():
    parts = []
    for i in range(NUM_LEVELS):
        for j in range(rowSize(i)):
            parts.append( invokeModule("draw", [EX(i),EX(j),get(i,j)] ) ) 
    return parts[0].union(*parts[1:])
    
def evolved(i,j):
    return invokeFunction("cell", [EX("n"),get(i,j)]+getNeighbors(i,j))
    
def iterator():
    args = [EX("n")-1]+[evolved(i,j) for i in range(NUM_LEVELS) for j in range(rowSize(i))]
    return invokeModule("evolve", args)

vars = ["u%d_%d" % (i,j) for i in range(NUM_LEVELS) for j in range(rowSize(i))]
varCount = len(vars)

out = []

addhead(out)

module("draw", ["i","j","v"], None)
function("evolve", ["n"]+vars, None)
function("cell", ["n", "v0", "v1", "v2", "v3", "v4", "v5", "v6"], None)
out += module("evolve", ["n"]+vars, (EX("n")==0).statementif( emitter(), elseStatement=iterator() ) )
out += module("go", [], invokeModule("evolve", [EX("iterations")]+[EX(0 if i>0 else EX("iterations")+1) for i in range(varCount)]) )
#out += invokeModule("go", [])

addtail(out)
print('\n'.join([str(line) for line in out]))
