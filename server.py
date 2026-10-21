"""Loopback-only demonstration server. Each request uses an independent scene."""
import json, os
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from core import *
from pipeline import make_plan
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=='/config':
            data=json.dumps({'configured':bool(os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_MODEL')),'model':os.getenv('OPENAI_MODEL','Not configured')}).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data);return
        if self.path!='/':self.send_error(404);return
        data=Path(__file__).with_name('index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if self.path!='/run':self.send_error(404);return
        host=self.headers.get('Host','')
        if host not in ['127.0.0.1:8765','localhost:8765'] or self.headers.get('Origin') not in [None,'http://127.0.0.1:8765','http://localhost:8765'] or self.headers.get('Content-Type')!='application/json':self.send_error(403);return
        try:length=int(self.headers.get('Content-Length',0))
        except ValueError:self.send_error(400);return
        if not 0<length<=4096:self.send_error(413);return
        try:
            q=json.loads(self.rfile.read(length))
            if not isinstance(q,dict):raise ValueError('Invalid body')
            seed=q.get('seed',0)
            if type(seed) is not int or not 0<=seed<=999999:raise ValueError('Invalid seed')
            if q.get('case','normal') not in ['normal','oversize','ambiguous','blocked','one_empty']:raise ValueError('Invalid scenario')
            world=scene(seed,q.get('case','normal'));before=render(world)
            result={'before':png(before),'detections':[{k:v for k,v in o.items() if k!='contour'} for o in detect(before)]}
            if q.get('preview'):result.update(status='Ready',message='New scene rendered. Detection uses its pixels.')
            else:
                try:
                    p,meta=make_plan(before,str(q.get('command',''))[:500],q.get('mode','rules'));result['interpretation']=meta;execute(world,p,bool(q.get('fail',False)));after=render(world);ok=verify(before,after,p['object'],p['tray'])
                    result.update(status='Verified' if ok else 'Failed verification',message='Placement confirmed from the resulting image.' if ok else 'Object did not reach the tray.',after=png(after),planned=png(annotated(before,p)),path=p['path'],selected={k:v for k,v in p['object'].items() if k!='contour'},planning_ms=round(p['planning_ms'],2),clearance=p['radius'])
                except ValueError as e:result.update(status='Rejected',message=str(e))
            data=json.dumps(result).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data)
        except (ValueError,TypeError,KeyError):self.send_error(400,'Invalid request')
if __name__=='__main__':
    print('Open http://127.0.0.1:8765',flush=True);HTTPServer(('127.0.0.1',8765),Handler).serve_forever()
