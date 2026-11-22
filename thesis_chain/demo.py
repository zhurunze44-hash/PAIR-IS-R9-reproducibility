"""Demonstrate all three scientific layers on constructed, tiny panels."""
from .core import Contract,Slot,Group,Archive,pair_reference_witness,hindsight_min_cost,online_replay,action_classes
def main():
    x=[[1,1,1],[1,1,0],[1,0,1],[1,0,0]]
    z=pair_reference_witness(x,x,[1,-1,-1,1],[0,0,0,0],
                             [4,7,8,4],[10,6,7,5])
    print("PAIR reference witness:",z)
    actions=[(1,0),(0,1),(1,0),(0,1)]
    slots=tuple(Slot("s%d"%i,"PPI","shared_binary",a) for i,a in enumerate(actions))
    groups=tuple(Group("g%d"%i,("s%d"%i,)) for i in range(4))
    c=Contract("v1","qualified synthetic Y2H","HC@2",("A","B"),("PPI",),slots,groups)
    archive=Archive(c,dict(zip((s.key for s in slots),(1,0,1,0))))
    print("PPI nominal model/action classes:",action_classes(c))
    print("Offline exact minimum:",hindsight_min_cost(c,archive,"strict_model","A"))
    print("Online order:",online_replay(c,archive,("g1","g3","g0","g2"),"strict_model","A"))
    slots=tuple(Slot("p%d_%d"%(p,i),"P%d"%p,"independent_binary") for p in range(2) for i in range(2))
    groups=tuple(Group("p%dg%d"%(p,i),("p%d_%d"%(p,i),)) for p in range(2) for i in range(2))
    h=Contract("v1","synthetic human","binary independent scores",("a","b","c","d"),("P0","P1"),slots,groups)
    ha=Archive(h,{s.key:(0,0,0,0) for s in slots})
    for kind,opts in [("nominal",{}),("one-bit",{"cell_flip":1}),("one-group",{"group_fault":1})]:
        print("Human no-common winner cost",kind,hindsight_min_cost(h,ha,"no_common",**opts)["cost"])
if __name__=="__main__":
    main()
