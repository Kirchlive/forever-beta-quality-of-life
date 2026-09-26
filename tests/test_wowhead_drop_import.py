"""Only explicit Forever entities with usable loot observations extend the lookup."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('wowhead_import', ROOT / 'tools/import_wowhead_drops.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def page(item=5085, status='unchanged', rows=None, env=16):
    if rows is None:
        rows = [dict(id=268624, name='Razormane Raider', count=268, outof=386,
                     envChange=dict(status='new'))]
    return ('<script type="application/json" id="data.pageMeta">' +
            json.dumps(dict(page='item', dataEnv=dict(env=env))) + '</script>' +
            '$.extend(g_items[' + str(item) + '], ' +
            json.dumps(dict(id=item, name='Bristleback Quilboar Tusk', envChange=dict(status=status))) + ');' +
            "new Listview({template:'npc', id:'dropped-by', data:" + json.dumps(rows) + '});' +
            "new Listview({template:'quest', id:'objective-of', data:[{\"id\":899}]});")


class WowheadImportTests(unittest.TestCase):
    def test_exact_new_npc_keeps_observation_counts(self):
        result = module.extract_item_page(page(), 5085)
        self.assertEqual(result['quest_ids'], [899])
        self.assertEqual(result['drops'][0]['npc_id'], 268624)
        self.assertEqual(result['drops'][0]['count'], 268)
        self.assertEqual(result['drops'][0]['outof'], 386)

    def test_new_item_on_old_npc_is_also_eligible(self):
        row = dict(id=3258, name='Bristleback Hunter', count=3, outof=10, envChange=dict(status='unchanged'))
        self.assertFalse(module.extract_item_page(page(rows=[row]), 5085)['drops'])
        self.assertEqual(len(module.extract_item_page(page(status='new', rows=[row]), 5085)['drops']), 1)
        self.assertFalse(module.extract_item_page(page(status='updated', rows=[row]), 5085)['drops'])

    def test_rejects_unknown_or_invalid_counts_instead_of_inventing_rates(self):
        for count, outof in [(-1, 0), (0, 100), (1, 0), (11, 10), (True, 10), (1.5, 10), ('3', 10)]:
            with self.subTest(count=count, outof=outof):
                row = dict(id=268624, name='Raider', count=count, outof=outof, envChange=dict(status='new'))
                self.assertFalse(module.extract_item_page(page(rows=[row]), 5085)['drops'])

    def test_wrong_environment_or_item_fails_closed(self):
        for source in [page(env=4), page(item=4894), '<html>Access denied</html>']:
            with self.assertRaises(ValueError):
                module.extract_item_page(source, 5085)

    def test_unobserved_sources_and_other_loot_modes_are_omitted(self):
        row = dict(id=268624, name='Raider', count=10, outof=20, envChange=dict(status='new'),
                   modes={'mode': [1], '1': dict(count=10, outof=20)})
        self.assertFalse(module.extract_item_page(page(rows=[row]), 5085)['drops'])
        source = page().replace("id:'dropped-by'", "id:'skinned-from'")
        self.assertFalse(module.extract_item_page(source, 5085)['drops'])

    def test_never_executes_embedded_script(self):
        source = page().replace('"count": 268', '"count": alert(268)')
        with self.assertRaises(ValueError):
            module.extract_item_page(source, 5085)

    def test_merge_uses_sample_ratio_without_changing_unrelated_classic_rates(self):
        record = module.extract_item_page(page(), 5085)
        npcs, names = {3245: {4894: 40}}, {4894: 'Plainstrider Kidney'}
        module.merge_records([record], npcs, names)
        self.assertAlmostEqual(npcs[268624][5085], 100 * 268 / 386)
        self.assertEqual(npcs[3245][4894], 40)
        self.assertEqual(names[5085], 'Bristleback Quilboar Tusk')

    def test_normalized_source_cannot_bypass_new_entity_or_count_validation(self):
        for change in [dict(count=400), dict(npc_status='unchanged'), dict(npc_id=True)]:
            record = module.extract_item_page(page(), 5085)
            record['drops'][0].update(change)
            with self.assertRaises(ValueError):
                module.merge_records([record], {}, {})


if __name__ == '__main__':
    unittest.main()
