(function(root){
const initial=()=>[
{id:'R1',color:'red',shape:'block',size:'small',width:30,x:270,y:190,tray:null},
{id:'B1',color:'blue',shape:'block',size:'small',width:30,x:405,y:260,tray:null},
{id:'G1',color:'green',shape:'circle',size:'small',width:32,x:530,y:180,tray:null},
{id:'R2',color:'red',shape:'circle',size:'small',width:32,x:320,y:350,tray:null},
{id:'B2',color:'blue',shape:'block',size:'large',width:70,x:520,y:355,tray:null}];
function plan(command,objects){
 const t=command.toLowerCase().trim().replace(/[.!?]+$/,'');
 const match=t.match(/^(?:move|put|place|sort)\s+(?:the\s+)?(.+?)\s+(?:to|into|in)\s+(?:the\s+)?(left|right)\s+(?:tray|bin)$/);
 if(!match)return {ok:false,message:'Use: Move the small blue block to the left tray.'};
 let terms=match[1].split(/\s+/).map(x=>({square:'block',disk:'circle',disc:'circle',object:'object'}[x]||x));
 if(terms.some(x=>!['red','blue','green','small','large','block','circle','object'].includes(x)))return {ok:false,message:'Unknown description. Use red/blue/green, small/large, and block/circle/object.'};
 let colors=terms.filter(x=>['red','blue','green'].includes(x)),sizes=terms.filter(x=>['small','large'].includes(x)),shapes=terms.filter(x=>['block','circle'].includes(x));
 if(new Set(colors).size>1||new Set(sizes).size>1||new Set(shapes).size>1)return {ok:false,message:'Describe one object with one colour, size, and shape.'};
 let matches=objects.filter(o=>(!colors.length||o.color===colors[0])&&(!sizes.length||o.size===sizes[0])&&(!shapes.length||o.shape===shapes[0]));
 if(!matches.length)return {ok:false,message:'No object matches that description.'};
 if(matches.length>1)return {ok:false,message:'Ambiguous instruction: '+matches.map(o=>o.id).join(', ')+' match. Add size or shape.'};
 let o=matches[0],tray=match[2];
 if(o.width>50)return {ok:false,message:o.id+' is too large: '+o.width+' units exceeds the 50-unit gripper opening.'};
 if(o.tray===tray)return {ok:false,message:o.id+' is already in the '+tray+' tray.'};
 let count=objects.filter(x=>x.tray===tray).length;
 if(count>=4)return {ok:false,message:'The '+tray+' tray is full.'};
 return {ok:true,id:o.id,tray,target:{x:tray==='left'?100:700,y:190+count*55},steps:['Understand instruction','Select '+o.id,'Check gripper capacity','Approach and grasp','Transfer to '+tray+' tray','Release and verify']};
}
const api={initial,plan};if(typeof module!=='undefined')module.exports=api;else root.SortingEngine=api;
})(globalThis);
