import unittest
from PIL import Image
from genereticore.upscale.runtime import validate,refine
class UpscaleTests(unittest.TestCase):
 def test_refinement_blends_downsampled_result_with_original(self):
  calls=[]
  def predict(image):
   calls.append(image.getpixel((0,0)));return Image.new('RGB',(image.width*4,image.height*4),'white')
  output=refine(Image.new('RGB',(8,6),'black'),predict,'2x',2,.5)
  self.assertEqual(output.size,(16,12));self.assertEqual(calls,[(0,0,0),(127,127,127)])
 def test_single_pass_ignores_feedback_and_preserves_source_dimensions(self):
  output=refine(Image.new('RGB',(8,6)),lambda x:x.resize((32,24)),'source',1,.8)
  self.assertEqual(output.size,(8,6))
 def test_reject_invalid_values(self):
  for args in [('other','2x',1,.5),('general','8x',1,.5),('general','2x',True,.5),('general','2x',3,.5),('general','2x',1,float('nan')),('general','2x',1,True)]:
   with self.assertRaises(ValueError):validate(*args)
if __name__=='__main__':unittest.main()
