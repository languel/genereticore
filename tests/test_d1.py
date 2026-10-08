import unittest
from unittest.mock import Mock
from genereticore.catalog import model_entry
from genereticore.contracts import Request
from genereticore.coreml import LocalBackend
from genereticore.nodes import GeneretiCoreDecision

class D1Tests(unittest.TestCase):
    def test_text_only_catalog_and_choice_limit(self):
        entry=model_entry('d1-omni-600m','decision.evaluate')
        self.assertEqual(entry['backend'],'coreml')
        self.assertTrue(all(len(f['sha256'])==64 for f in entry['files']))
        self.assertIn('LICENSE',[f['path'] for f in entry['files']])
        with self.assertRaises(ValueError): model_entry('d1-omni-600m','vision.analyze')
        with self.assertRaises(ValueError): Request('decision.evaluate','d1-omni-600m',{'prompt':'scene','choices':[str(i) for i in range(9)]})
        with self.assertRaises(ValueError): Request('decision.evaluate','d1-omni-600m',{'prompt':'scene','choices':['blue','orange'],'question':3})
    def test_model_routing_and_backend_release(self):
        backend=LocalBackend(); coreai=Mock();coreml=Mock();backend.backends={'coreai':coreai,'coreml':coreml}
        request=Request('decision.evaluate','d1-omni-600m',{'prompt':'scene','choices':['blue','orange']})
        backend.execute(request,lambda *_:None)
        coreai.execute.assert_not_called();coreai.close.assert_called_once()
        self.assertEqual(coreml.execute.call_args.args[0],request)
        self.assertIsNone(backend.active)
        self.assertEqual(GeneretiCoreDecision.INPUT_TYPES()['required']['model'][0],['qwen3-0.6b','d1-omni-600m'])
