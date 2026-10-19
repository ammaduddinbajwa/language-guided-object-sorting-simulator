"""Image-only perception/planning; world state is confined to rendering/execution."""
import base64, heapq, math, re, time
from dataclasses import dataclass, asdict
import cv2
import numpy as np
W,H=640,400
COLORS={'red':(65,65,220),'blue':(220,100,45),'green':(70,170,60)}
TRAYS={'left':(15,110,115,350),'right':(525,110,625,350)}
@dataclass
class Object:
    color:str; shape:str; x:int; y:int; radius:int

def scene(seed=0,case='normal'):
    rng=np.random.default_rng(seed)
    objs=[Object(c, ['circle','block'][int(rng.integers(2))],x,int(rng.integers(150,290)),int(rng.integers(11,19))) for c,x in zip(COLORS,[190,310,450])]
    obs=[(250,115,270,255),(370,200,390,340)]
    if case=='oversize':objs[0].radius=35
    if case=='ambiguous':objs.append(Object('red','circle',190,330,12))
    if case=='blocked':obs=[(125,0,145,H-1)]
    return {'objects':objs,'obstacles':obs}

def render(world):
    im=np.full((H,W,3),245,np.uint8)
    for x1,y1,x2,y2 in TRAYS.values():cv2.rectangle(im,(x1,y1),(x2,y2),(220,230,220),-1)
    for x1,y1,x2,y2 in world['obstacles']:cv2.rectangle(im,(x1,y1),(x2,y2),(50,50,50),-1)
    for o in world['objects']:
        if o.shape=='circle':cv2.circle(im,(o.x,o.y),o.radius,COLORS[o.color],-1)
        else:cv2.rectangle(im,(o.x-o.radius,o.y-o.radius),(o.x+o.radius,o.y+o.radius),COLORS[o.color],-1)
    return im

def detect(im):
    """No world or generator metadata accepted here."""
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV);out=[]
    ranges={'red':[(0,12),(170,179)],'green':[(35,85)],'blue':[(90,130)]}
    for color,bands in ranges.items():
        mask=np.zeros(im.shape[:2],np.uint8)
        for lo,hi in bands:mask|=cv2.inRange(hsv,(lo,100,80),(hi,255,255))
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area=cv2.contourArea(contour)
            if area<60:continue
            x,y,w,h=cv2.boundingRect(contour);m=cv2.moments(contour)
            poly=cv2.approxPolyDP(contour,.03*cv2.arcLength(contour,True),True)
            out.append({'color':color,'shape':'block' if len(poly)==4 else 'circle','x':round(m['m10']/m['m00']),'y':round(m['m01']/m['m00']),'width':w,'height':h,'size':'small' if max(w,h)<=40 else 'large','contour':contour})
    return out

def parse(command):
    m=re.fullmatch(r'\s*(move|put|place|sort)\s+(?:the\s+)?(.+?)\s+(?:to|into|in)\s+(?:the\s+)?(left|right)\s+(?:tray|bin)[.!]?\s*',command.lower())
    if not m:raise ValueError('Use: Move the red object to the left tray.')
    terms=m[2].split(); allowed={'red','blue','green','small','large','circle','block','square','object'}
    if any(t not in allowed for t in terms):raise ValueError('Unsupported object description.')
    terms=['block' if t=='square' else t for t in terms];result={'tray':m[3]}
    for key,values in [('color',COLORS),('shape',['block','circle']),('size',['small','large'])]:
        selected=set(terms)&set(values)
        if len(selected)>1:raise ValueError('Conflicting object properties.')
        if selected:result[key]=selected.pop()
    return result

def occupancy(im,selected,radius):
    # Pixel obstacles include dark fixtures and all other detected objects.
    mask=(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)<90).astype(np.uint8)*255
    for obj in detect(im):cv2.drawContours(mask,[obj['contour']],-1,255,-1)
    cv2.drawContours(mask,[selected['contour']],-1,0,-1)
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*radius+1,2*radius+1))
    mask=cv2.dilate(mask,kernel)
    mask[:radius+1]=255;mask[-radius-1:]=255;mask[:,:radius+1]=255;mask[:,-radius-1:]=255
    return mask

def astar(mask,start,goal):
    """4-connected pixel A*: each edge is collision-checked, no corner cutting."""
    if mask[start[1],start[0]] or mask[goal[1],goal[0]]:return []
    queue=[(0,0,start)];cost={start:0};parent={};h,w=mask.shape
    while queue:
        _,g,p=heapq.heappop(queue)
        if g!=cost[p]:continue
        if p==goal:
            path=[p]
            while p in parent:p=parent[p];path.append(p)
            return path[::-1]
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            q=(p[0]+dx,p[1]+dy)
            if not(0<=q[0]<w and 0<=q[1]<h) or mask[q[1],q[0]]:continue
            ng=g+1
            if ng<cost.get(q,math.inf):
                cost[q]=ng;parent[q]=p;heapq.heappush(queue,(ng+abs(q[0]-goal[0])+abs(q[1]-goal[1]),ng,q))
    return []

def plan(im,command):
    t=time.perf_counter();spec=parse(command);objects=detect(im)
    matches=[o for o in objects if all(o[k]==v for k,v in spec.items() if k!='tray')]
    if not matches:raise ValueError('No matching object detected.')
    if len(matches)>1:raise ValueError('Ambiguous command: add shape or size.')
    obj=matches[0]
    if obj['width']>50:raise ValueError('Object exceeds the 50-pixel gripper opening.')
    radius=math.ceil(math.hypot(obj['width'],obj['height'])/2)+3
    mask=occupancy(im,obj,radius);x1,y1,x2,y2=TRAYS[spec['tray']]
    goals=[(x,y) for y in range(y1+radius+1,y2-radius,20) for x in range(x1+radius+1,x2-radius,20) if not mask[y,x]]
    if not goals:raise ValueError('No free placement with sufficient tray clearance.')
    _,components=cv2.connectedComponents((mask==0).astype(np.uint8),connectivity=4)
    component=components[obj['y'],obj['x']]
    goals=[g for g in goals if component and components[g[1],g[0]]==component]
    goals.sort(key=lambda p:abs(p[0]-obj['x'])+abs(p[1]-obj['y']))
    path=[]
    for goal in goals:
        path=astar(mask,(obj['x'],obj['y']),goal)
        if path:break
    if not path:raise ValueError('No collision-free route to the tray.')
    return {'object':obj,'tray':spec['tray'],'path':path,'radius':radius,'planning_ms':(time.perf_counter()-t)*1000,'mask':mask}

def verify(before,after,chosen,tray):
    """Check new image: matching object inside tray and departed source."""
    x1,y1,x2,y2=TRAYS[tray]
    def match(o):return o['color']==chosen['color'] and o['shape']==chosen['shape'] and abs(o['width']-chosen['width'])<=2
    def inside(o):return o['x']-o['width']/2>x1 and o['x']+o['width']/2<x2 and o['y']-o['height']/2>y1 and o['y']+o['height']/2<y2
    old=detect(before);new=detect(after)
    arrived=sum(match(o) and inside(o) for o in new)>sum(match(o) and inside(o) for o in old)
    departed=not any(match(o) and abs(o['x']-chosen['x'])<3 and abs(o['y']-chosen['y'])<3 for o in new)
    return bool(arrived and departed and len(new)==len(old))

def execute(world,p,fail=False):
    # Executor alone sees world truth. Association models a gripper at the perceived point.
    obj=min(world['objects'],key=lambda o:(o.x-p['object']['x'])**2+(o.y-p['object']['y'])**2)
    if not fail:obj.x,obj.y=p['path'][-1]

def png(im):return 'data:image/png;base64,'+base64.b64encode(cv2.imencode('.png',im)[1]).decode()
def annotated(im,p):
    out=im.copy();cv2.polylines(out,[np.array(p['path'],np.int32)],False,(160,80,160),2)
    for o in detect(im):
        cv2.drawContours(out,[o['contour']],-1,(0,0,0),1)
        cv2.putText(out,o['color']+' '+o['shape'],(o['x']-35,o['y']-25),cv2.FONT_HERSHEY_SIMPLEX,.35,(0,0,0),1)
    cv2.circle(out,(p['object']['x'],p['object']['y']),4,(0,0,0),-1)
    return out
