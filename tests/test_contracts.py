import json
import unittest
from genereticore.contracts import Request, validate_decision
from genereticore.catalog import model_entry

class ContractTests(unittest.TestCase):
    def test_normalizes_specialist_scores(self):
        r = validate_decision({'choice':'a', 'scores':{'a':.8, 'b':.4}}, ['a', 'b'])
        self.assertAlmostEqual(sum(r['probabilities'].values()), 1)
    def test_rejects_unsafe_scores_and_labels(self):
        cases = [{'choice':'x','scores':{'a':.9,'b':.1}}, {'choice':'b','scores':{'a':.9,'b':.1}},
            {'choice':'a','scores':{'a':float('nan'),'b':.1}}, {'choice':'a','scores':{'a':True,'b':.1}},
            {'choice':'a','scores':{'a':0,'b':0}}, {'choice':'a','scores':{'a':.9}},
            {'choice':'a','scores':{'a':.9,'b':.1},'code':'execute()'}]
        for value in cases:
            with self.subTest(value=value), self.assertRaises(ValueError): validate_decision(value, ['a','b'])
    def test_tutorial_score_edit_explains_mismatch(self):
        with self.assertRaises(ValueError) as caught:
            validate_decision({'choice':'blue','scores':{'blue':.1,'orange':.2}}, ['blue','orange'])
        message = str(caught.exception)
        self.assertIn('"blue" (score 0.1)', message)
        self.assertIn('"orange" has the highest score (0.2)', message)
        self.assertIn('Set choice to "orange"', message)
        result = validate_decision({'choice':'orange','scores':{'blue':.1,'orange':.2}}, ['blue','orange'])
        self.assertEqual(result['choice'], 'orange')
        self.assertAlmostEqual(result['probabilities']['orange'], 2/3)

    def test_capability_mismatch(self):
        with self.assertRaises(ValueError): model_entry('qwen3-vl-2b', 'text.generate')
    def test_bounded_inputs(self):
        with self.assertRaises(ValueError): Request('text.generate',inputs={'prompt':'hi'},options={'max_tokens':10000})
        with self.assertRaises(ValueError): Request('decision.evaluate',inputs={'prompt':'hi','choices':['same','same']})
        with self.assertRaises(ValueError): Request('text.generate',inputs={'prompt':'hi'},options={'temperature':float('inf')})

if __name__ == '__main__': unittest.main()
