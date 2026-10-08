import json
from pathlib import Path
import tempfile
import unittest
from genereticore.examples import install
from genereticore.nodes import GeneretiCoreChoiceValue, GeneretiCoreResult

class ExampleTests(unittest.TestCase):
    def test_preserves_edits_and_backs_up_managed_updates(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); source=root/'examples';source.mkdir();workflows=root/'profile/workflows'
            example=source/'sample.json';example.write_text('{"version":1}')
            target=install(source,workflows)/example.name
            example.write_text('{"version":2}');install(source,workflows)
            self.assertEqual(json.loads(target.read_text())['version'],2)
            self.assertTrue(list((workflows.parent/'.genereticore-workflow-backups').rglob('sample.json')))
            target.write_text('{"my_edit":true}');example.write_text('{"version":3}');install(source,workflows)
            self.assertEqual(json.loads(target.read_text()),{'my_edit':True})
    def test_retires_only_unchanged_managed_samples_with_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'examples'; source.mkdir()
            workflows = root / 'profile/workflows'
            (source / 'old.json').write_text('{}')
            (source / 'edited.json').write_text('{}')
            destination = install(source, workflows)
            (destination / 'edited.json').write_text('{"custom":true}')
            (source / 'old.json').unlink(); (source / 'edited.json').unlink()
            install(source, workflows)
            self.assertFalse((destination / 'old.json').exists())
            self.assertTrue((destination / 'edited.json').exists())
            self.assertEqual(len(list((workflows.parent / '.genereticore-workflow-backups').rglob('old.json'))), 1)

    def test_graph_links_and_lesson_references(self):
        for path in Path('example_workflows').glob('*.json'):
            graph=json.loads(path.read_text());nodes={n['id']:n for n in graph['nodes']}
            for id,src,out,dst,slot,typ in graph['links']:
                self.assertIn(id,nodes[src]['outputs'][out]['links'])
                self.assertEqual(nodes[dst]['inputs'][slot]['link'],id)
            for n in nodes.values():
                if n['type']=='GeneretiDatLesson':
                    guide=json.loads(n['widgets_values'][0])
                    for step in guide['steps']:
                        target=step['target'];self.assertEqual(nodes[target['nodeId']]['type'],target['nodeType'])
    def test_typed_palette_and_result_sink(self):
        self.assertEqual(GeneretiCoreChoiceValue().map_choice('blue','{"blue":210}'),(210.0,))
        with self.assertRaises(ValueError):GeneretiCoreChoiceValue().map_choice('red','{"blue":210}')
        with self.assertRaises(ValueError):GeneretiCoreChoiceValue().map_choice('blue','{"blue":true}')
        self.assertEqual(GeneretiCoreResult().show('hello')['ui']['text'],['hello'])
