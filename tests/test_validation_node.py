import json
import sys
import types
import unittest
from unittest.mock import patch
from genereticore.nodes import GeneretiCoreValidateDecision

class ValidationNodeTests(unittest.TestCase):
    def test_invalid_edits_return_inline_feedback_and_silent_blockers(self):
        class Blocker:
            def __init__(self, message): self.message = message
        module = types.ModuleType('comfy_execution.graph_utils')
        module.ExecutionBlocker = Blocker
        for value in ['{"choice":"blue","scores":{"blue":0.1,"orange":0.2}}', '{',
                      '{"choice":"blue","scores":{"blue":-1,"orange":0.2}}']:
            with self.subTest(value=value), patch.dict(sys.modules, {'comfy_execution.graph_utils':module}):
                reply = GeneretiCoreValidateDecision().validate('["blue","orange"]', value)
                self.assertFalse(reply['ui']['validation'][0]['valid'])
                self.assertIn('Needs correction:', reply['ui']['text'][0])
                self.assertTrue(all(isinstance(v, Blocker) and v.message is None for v in reply['result']))
    def test_corrected_input_restores_normal_outputs(self):
        reply = GeneretiCoreValidateDecision().validate('["blue","orange"]',
            '{"choice":"orange","scores":{"blue":0.1,"orange":0.2}}')
        self.assertTrue(reply['ui']['validation'][0]['valid'])
        self.assertEqual(reply['result'][0], 'orange')
        self.assertAlmostEqual(json.loads(reply['result'][1])['probabilities']['orange'], 2/3)
