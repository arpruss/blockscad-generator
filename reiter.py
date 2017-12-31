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

def get(i,j,v="data"):
    if i >= NUM_LEVELS:
        return EX("beta")
    if i<0:
        return get(1,0,v=v)
    if i <= 1 and j != 0:
        return get(i,0,v=v)
    rs = rowSize(i)
    if j < 0:
        return get(i,-j,v=v)
    elif j >= rs:
        if i % 2:
            return get(i,rs-1-(j-rs),v=v)
        else:
            return get(i,rs-2-(j-rs),v=v)
    assert(0<=i and i<NUM_LEVELS and 0<=j and j<rs)
    return EX("%s%d_%d" % (v,i,j))
    
def receptive(i,j):
    if i==0:
        return (get(0,0)>=1).OR(get(1,0)>=1)
    elif j==0: 
        return (get(i,0)>=1).OR(get(i,1)>=1).OR(get(i+1,0)>=1).OR(get(i+1,1)>=1).OR(get(i-1,0)>=1)
    else:
        return (get(i,j)>=1).OR(get(i,j-1)>=1).OR(get(i,j+1)>=1).OR(get(i+1,j)>=1).OR(get(i+1,j+1)>=1).OR(get(i-1,j)>=1).OR(get(i-1,j-1)>=1)
        
def u(i,j):
    return get(i,j,"u")
    
def neighborUSum(i,j):
    rs = rowSize(i)
    if i == 0:
        return u(1,0)*6
    elif j < 0:
        return neighborUSum(i,-j)
    elif j >= rs:
        if i % 2:
            return u(i,rs-1-(j-rs))
        else:
            return u(i,rs-2-(j-rs))
    elif j == 0:
        return (u(i,1)+u(i+1,1))*2+u(i+1,0)+u(i-1,0)
    else:
        return u(i,j-1)+u(i,j+1)+u(i+1,j)+u(i+1,j+1)+u(i-1,j)+u(i-1,j-1)

def emitter():
    parts = []
    for i in range(NUM_LEVELS):
        for j in range(rowSize(i)):
            parts.append( (get(i,j)>=1).statementif( invokeModule("draw", [EX(i),EX(j),get(i,j)] ) ) )
    return parts[0].union(*parts[1:])    
    
def evolved(i,j):
    return invokeFunction("cell", [get(i,j),get(i,j,"u"),neighborUSum(i,j)]) #(get(i,j,"u")==0).ifthen(get(i,j)+"gamma",(EX(1)-EX("alpha")/2)*get(i,j,"u"))+EX("alpha_12")*neighborUSum(i,j)
    
def iterator():
    args = [EX("n")-1]+[evolved(i,j) for i in range(NUM_LEVELS) for j in range(rowSize(i))]
    return invokeModule("evolve", args)
    
def uValues(nextStatement):
    out = []
    for i in range(NUM_LEVELS):
        for j in range(rowSize(i)):
            if j==0:
                c = invokeFunction("calc_u", [get(i,0),get(i,1),get(i+1,0),get(i+1,1),get(i-1,0),EX(0),EX(0)])
            else:
                c = invokeFunction("calc_u", [get(i,j),get(i,j-1),get(i,j+1),get(i+1,j),get(i+1,j+1),get(i-1,j),get(i-1,j-1)])
#           c = receptive(i,j).ifthen(EX(0),get(i,j)).
            nextStatement = c.assignTo("u%d_%d" % (i,j), nextStatement)
    return nextStatement

vars = ["data%d_%d" % (i,j) for i in range(NUM_LEVELS) for j in range(rowSize(i))]
varCount = len(vars)

out = []

addhead(out)

#out += module("draw", ["i","j"], square(5,5).translate3(EX("i")*6,EX("j")*6,EX(0)) )
module("draw", ["i","j","v"], None)
function("evolve", ["n"]+vars, None)
function("get_beta", [], None)
out += function("calc_u", ["v", "v1", "v2", "v3", "v4", "v5", "v6"],
    (EX("v")>=1).OR(EX("v1")>=1).OR(EX("v2")>=1).OR(EX("v3")>=1).OR(EX("v4")>=1).OR(EX("v5")>=1).OR(EX("v6")>=1).ifthen(EX(0),EX("v")))
out += function("cell", ["v","u","uSum"],
        (EX("u")==0).ifthen(EX("v")+"gamma",(EX(1)-EX("alpha")/2)*"u")+EX("alpha")/12*"uSum")
#out += function("survive", ["neighbors"], EX(1))
#out += function("generate", ["neighbors"], (EX(1)==EX("neighbors")).ifthen(EX(1),EX(0)))
out += module("evolve", ["n"]+vars, uValues((EX("n")==0).statementif( emitter() ).union( (EX("n")>0).statementif( iterator() ) )) )
out += module("go", [], invokeModule("evolve", [EX("iterations")]+[EX(invokeFunction("get_beta",[]) if i>0 else 1) for i in range(varCount)]) )
#out += invokeModule("go", [])

addtail(out)
print('\n'.join([str(line) for line in out]))
