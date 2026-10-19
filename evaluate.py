"""Held-out seeds 100..119. Ground truth is used only by the scorer/executor."""
import csv,json,platform
from pathlib import Path
from core import *
out=Path(__file__).parent/'evidence';out.mkdir(exist_ok=True);rows=[]
for seed in range(100,120):
 for case in ['normal','oversize','ambiguous','blocked','failed_grasp']:
  w=scene(seed,case);before=render(w);truth=w['objects'][0];det=detect(before)
  accurate=len(det)==len(w['objects']) and all(any(o['color']==t.color and o['shape']==t.shape and abs(o['x']-t.x)<=1 and abs(o['y']-t.y)<=1 for o in det) for t in w['objects'])
  row={'seed':seed,'case':case,'perception_correct':int(accurate),'selection_correct':'','planning_ms':'','path_pixels':'','outcome':'','expected_outcome':{'normal':'verified','failed_grasp':'failed_verification'}.get(case,'rejected')}
  try:
   p=plan(before,'move red object to left tray');o=p['object'];row.update(selection_correct=int(abs(o['x']-truth.x)<=1 and abs(o['y']-truth.y)<=1),planning_ms=round(p['planning_ms'],3),path_pixels=len(p['path'])-1)
   execute(w,p,case=='failed_grasp');after=render(w);row['outcome']='verified' if verify(before,after,o,p['tray']) else 'failed_verification'
   if seed==100 and case=='normal':
    cv2.imwrite(str(out/'01-camera.png'),before);cv2.imwrite(str(out/'02-detections-and-path.png'),annotated(before,p));cv2.imwrite(str(out/'03-result.png'),after)
  except ValueError as e:row.update(outcome='rejected',reason=str(e))
  rows.append(row)
fields=list(dict.fromkeys(k for r in rows for k in r))
with (out/'experiments.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
summary={'trials':len(rows),'perception_correct':sum(r['perception_correct'] for r in rows),'expected_outcomes':sum(r['outcome']==r['expected_outcome'] for r in rows),'by_case':{c:{'trials':20,'expected':sum(r['outcome']==r['expected_outcome'] for r in rows if r['case']==c)} for c in set(r['case'] for r in rows)},'mean_planning_ms':round(float(np.mean([r['planning_ms'] for r in rows if r['planning_ms']!=''])),3),'python':platform.python_version(),'opencv':cv2.__version__,'numpy':np.__version__}
(out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
