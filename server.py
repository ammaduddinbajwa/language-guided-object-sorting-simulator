"""Loopback-only demonstration server. Each request uses an independent scene."""
import json
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from core import *
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path!='/':self.send_error(404);return
        data=Path(__file__).with_name('index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if self.path!='/run':self.send_error(404);return
        length=int(self.headers.get('Content-Length',0))
        if length>4096:self.send_error(413);return
        try:
            q=json.loads(self.rfile.read(length));world=scene(int(q.get('seed',0)),q.get('case','normal'));before=render(world)
            result={'before':png(before),'detections':[{k:v for k,v in o.items() if k!='contour'} for o in detect(before)]}
            if q.get('preview'):result.update(status='Ready',message='New scene rendered. Detection uses its pixels.')
            else:
                try:
                    p=plan(before,str(q.get('command',''))[:300]);execute(world,p,bool(q.get('fail',False)));after=render(world);ok=verify(before,after,p['object'],p['tray'])
                    result.update(status='Verified' if ok else 'Failed verification',message='Placement confirmed from the resulting image.' if ok else 'Object did not reach the tray.',after=png(after),planned=png(annotated(before,p)),path=p['path'],selected={k:v for k,v in p['object'].items() if k!='contour'},planning_ms=round(p['planning_ms'],2),clearance=p['radius'])
                except ValueError as e:result.update(status='Rejected',message=str(e))
            data=json.dumps(result).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data)
        except (ValueError,TypeError,KeyError):self.send_error(400,'Invalid request')
if __name__=='__main__':
    print('Open http://127.0.0.1:8765',flush=True);HTTPServer(('127.0.0.1',8765),Handler).serve_forever()
