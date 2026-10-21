import json,os,unittest
from unittest.mock import patch
from urllib.error import HTTPError,URLError
from core import *
from foundation import *
from pipeline import make_plan

def action(**kw):
 d=dict(decision='act',action='move',color='red',shape=None,size=None,selector='unique',destination='left',reason='Move requested object.');d.update(kw);return d

def response(d):return {'status':'completed','model':'mock-model','id':'mock-response','usage':{'input_tokens':10},'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(d)}]}]}

class ModelTests(unittest.TestCase):
 def setUp(self):self.im=render(scene(100))
 def test_strict_validation(self):
  for d in [dict(action(),extra='code'),action(destination='outside'),action(action='delete'),action(reason=[]),action(decision='clarify')]:
   with self.assertRaises(ModelError):validate(d)
 def test_smallest(self):
  o,t=resolve(self.im,action(color=None,selector='smallest'));self.assertEqual(cv2.contourArea(o['contour']),min(cv2.contourArea(x['contour']) for x in detect(self.im)))
 def test_tie(self):
  w={'objects':[Object('red','block',190,150,12),Object('green','block',400,150,12)],'obstacles':[]}
  with self.assertRaisesRegex(ValueError,'Ambiguous'):resolve(render(w),action(color=None,selector='smallest'))
 def test_two_empty_trays(self):
  with self.assertRaisesRegex(ValueError,'empty tray'):resolve(self.im,action(destination='empty'))
 def test_one_empty_tray(self):self.assertEqual(resolve(render(scene(100,'one_empty')),action(destination='empty'))[1],'right')
 def test_no_empty_tray(self):
  w=scene(100,'one_empty');w['objects'][2].x,w['objects'][2].y=575,200
  with self.assertRaises(ValueError):resolve(render(w),action(destination='empty'))
 def test_ambiguous_model_cannot_bypass(self):
  with self.assertRaisesRegex(ValueError,'Ambiguous'):resolve(render(scene(100,'ambiguous')),action())
 def test_clear_rejection(self):
  with self.assertRaisesRegex(ValueError,'Reject'):resolve(self.im,action(decision='reject',action='none'))
 @patch.dict(os.environ,{'OPENAI_API_KEY':'unit-test-only','OPENAI_MODEL':'mock-model'})
 def test_text_and_image_payloads(self):
  for mode in ['model-text','model-vision']:
   def send(payload,key,timeout):
    self.assertEqual(key,'unit-test-only');self.assertEqual(timeout,30);self.assertFalse(payload['store']);self.assertTrue(payload['text']['format']['strict'])
    content=payload['input'][0]['content'];self.assertEqual(len(content),2 if mode=='model-vision' else 1)
    if mode=='model-vision':self.assertTrue(content[1]['image_url'].startswith('data:image/png;base64,'))
    return response(action())
   p,m=make_plan(self.im,'move red object to left tray',mode,send);self.assertEqual(m['source'],'mock_transport');self.assertEqual(p['tray'],'left')
 @patch.dict(os.environ,{'OPENAI_API_KEY':'unit-test-only','OPENAI_MODEL':'mock-model'})
 def test_model_geometry_rejections(self):
  for case in ['oversize','blocked']:
   with self.assertRaises(ValueError):make_plan(render(scene(100,case)),'move red object to left tray','model-text',lambda *a:response(action()))
 @patch.dict(os.environ,{},clear=True)
 def test_missing_key(self):
  with self.assertRaisesRegex(ModelError,'No live API'):interpret(self.im,'move red object to left tray')
 @patch.dict(os.environ,{'OPENAI_API_KEY':'unit-test-only','OPENAI_MODEL':'mock-model'})
 def test_malformed_refusal_incomplete(self):
  for r in [{'status':'incomplete'}, {'status':'completed','output':[]}, {'status':'completed','output':[{'type':'message','content':[{'type':'refusal'}]}]},response({'wrong':True})]:
   with self.assertRaises(ModelError):interpret(self.im,'x',send=lambda *a:r)
 def test_http_errors_redacted(self):
  for exc in [HTTPError('url',401,'secret',{},None),HTTPError('url',429,'secret',{},None),HTTPError('url',500,'secret',{},None),URLError('secret'),TimeoutError('secret')]:
   with patch('foundation.request.build_opener') as p:
    p.return_value.open.side_effect=exc
    with self.assertRaises(ModelError) as ctx:transport({},'unit-test-only',30)
    self.assertNotIn('secret',str(ctx.exception));self.assertNotIn('unit-test-only',str(ctx.exception))
 def test_unknown_mode(self):
  with self.assertRaises(ValueError):make_plan(self.im,'x','invalid')
if __name__=='__main__':unittest.main()
