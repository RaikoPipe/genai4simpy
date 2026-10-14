"""Diagnostic probe: hbw/vgr usage, unload spacing, utilisation and pre-activity gaps, real vs simulated.

    python analysis/probe.py"""
import numpy as np, pandas as pd
from _common import RUN, block_csv, model_path
import evaluate_v2 as ev

def probe(L,T):
    L=L[L.operation_end_time<=T+1e-9].sort_values('service_start')
    H=L[L.resource.str.match(r'(hbw|vgr)')]
    use=H.groupby(['activity','resource']).size().unstack(fill_value=0)
    un=L[L.activity=='/hbw/unload'].service_start.sort_values().diff().dropna()
    util=(H.assign(d=H.operation_end_time-H.service_start).groupby('resource').d.sum()/T*100)
    return use, un, util
for b in RUN:
    real,T=ev.load_real(block_csv(b))
    mod=ev.load_module(model_path(b),f"s{b}")
    print(f"\n######## {b}  capacities:",getattr(mod,'RESOURCE_CAPACITIES',{}))
    ur,unr,utr=probe(real,T)
    sims=[ev.simulate(mod,42+i,T) for i in range(200)]
    us=probe(sims[0],T)[0]
    uns=pd.concat([probe(s,T)[1] for s in sims]); uts=pd.concat([probe(s,T)[2] for s in sims],axis=1).mean(axis=1)
    print("REAL usage\n",ur.to_string()); print("SIM usage (seed 42)\n",us.to_string())
    print("unload start spacing  real median/mean %.1f/%.1f   sim median/mean %.1f/%.1f"%(unr.median(),unr.mean(),uns.median(),uns.mean()))
    print("utilisation %% real:",utr.round(1).to_dict()," sim:",uts.round(1).to_dict())
    s=pd.concat([x.assign(rep=i) for i,x in enumerate(sims[:50])]).sort_values(['rep','case_id','service_start'])
    s['gap']=s.service_start-s.groupby(['rep','case_id']).operation_end_time.shift()
    r=real.sort_values(['case_id','service_start']); r['gap']=r.service_start-r.groupby('case_id').operation_end_time.shift()
    print("mean gap before hbw activity: real",r[r.resource.str.startswith('hbw')].groupby('activity').gap.mean().round(1).to_dict(),
          "| sim",s[s.resource.str.startswith('hbw')].groupby('activity').gap.mean().round(1).to_dict())
    print("mean gap before vgr activity: real %.1f sim %.1f"%(r[r.resource.str.startswith('vgr')].gap.mean(), s[s.resource.str.startswith('vgr')].gap.mean()))
