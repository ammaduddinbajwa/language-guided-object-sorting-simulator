import unittest
from core import *
class Tests(unittest.TestCase):
 def test_perception(self):
  w=scene(100);d=detect(render(w));self.assertEqual(len(d),3)
  for truth in w['objects']:
   o=next(o for o in d if o['color']==truth.color);self.assertEqual((o['x'],o['y'],o['shape']),(truth.x,truth.y,truth.shape))
 def test_parse(self):self.assertEqual(parse('Put the small blue square into the right tray.')['shape'],'block')
 def test_bad_commands(self):
  for c in ['delete everything','move the red blue object to the left tray','move the red object to the outside tray']:
   with self.assertRaises(ValueError):parse(c)
 def test_ambiguous(self):
  with self.assertRaisesRegex(ValueError,'Ambiguous'):plan(render(scene(100,'ambiguous')),'move red object to left tray')
 def test_oversize(self):
  with self.assertRaisesRegex(ValueError,'gripper'):plan(render(scene(100,'oversize')),'move red object to left tray')
 def test_blocked(self):
  with self.assertRaisesRegex(ValueError,'route'):plan(render(scene(100,'blocked')),'move red object to left tray')
 def test_collision_clearance(self):
  p=plan(render(scene(100)),'move red object to right tray')
  self.assertTrue(all(p['mask'][y,x]==0 for x,y in p['path']))
  self.assertTrue(all(abs(a[0]-b[0])+abs(a[1]-b[1])==1 for a,b in zip(p['path'],p['path'][1:])))
 def test_verification(self):
  w=scene(100);im=render(w);p=plan(im,'move red object to left tray')
  self.assertFalse(verify(im,im,p['object'],'left'));execute(w,p);self.assertTrue(verify(im,render(w),p['object'],'left'))
 def test_wrong_tray(self):
  w=scene(100);im=render(w);p=plan(im,'move red object to right tray');execute(w,p);self.assertFalse(verify(im,render(w),p['object'],'left'))
if __name__=='__main__':unittest.main()
