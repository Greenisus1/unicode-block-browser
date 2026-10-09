import unittest
from browser import valid_url,nearest,blocks
from PIL import Image
class Tests(unittest.TestCase):
 def test_url(self):self.assertEqual(valid_url('https://example.com'),'https://example.com')
 def test_schemes(self):
  for url in ('file:///etc/passwd','javascript:alert(1)','data:text/plain,x','ftp://example.com','http://user:pass@example.com','https://example.com\x1b'):
   with self.assertRaises(ValueError):valid_url(url)
 def test_limit(self):
  with self.assertRaises(ValueError):valid_url('https://example.com/'+ 'a'*5000)
 def test_black(self):self.assertEqual(nearest((0,0,0)),0)
 def test_shape(self):
  b=blocks(Image.new('RGB',(100,200)),50);self.assertEqual((len(b),len(b[0])),(100,50))
 def test_width_limit(self):self.assertEqual(len(blocks(Image.new('RGB',(10,10)),1000)[0]),240)
if __name__=='__main__':unittest.main()
