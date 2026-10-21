"""Shared runner for UI and evaluation. No silent model-to-rule fallback."""
import time
from core import plan,plan_selected
from foundation import interpret,resolve

def make_plan(im,command,mode='rules',send=None):
    start=time.perf_counter()
    if mode=='rules':
        p=plan(im,command);meta={'source':'rule_based','mode':mode,'api_ms':0,'model':None}
    elif mode in ['model-text','model-vision']:
        proposal,meta=interpret(im,command,mode,send)
        obj,tray=resolve(im,proposal)
        p=plan_selected(im,obj,tray);meta['proposal']=proposal
    else:raise ValueError('Unknown interpretation mode.')
    meta['total_ms']=round((time.perf_counter()-start)*1000,2)
    return p,meta
