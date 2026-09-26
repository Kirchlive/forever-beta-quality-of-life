"""Extract Forever-only loot observations from locally saved Wowhead item pages.

Never executes page scripts or downloads anything. Only new NPCs or new items
qualify: old entities on /forever/ can contain inherited Classic observations.
Usage: python tools/import_wowhead_drops.py CACHE_DIRECTORY CATALOG_JSON
Then: python tools/import_questie_drops.py
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DECODER = json.JSONDecoder()


def positive_int(value):
    return type(value) is int and value > 0


def valid_name(value):
    return isinstance(value, str) and bool(value.strip()) and not any(ord(c) < 32 for c in value)


def listview_rows(source, template, tab):
    for block in re.split(r'new\s+Listview\(\s*\{', source)[1:]:
        data = re.search(r'\bdata\s*:\s*', block)
        if not data:
            continue
        header = block[:data.start()]
        if (re.search(r'\btemplate\s*:\s*[\'\"]' + re.escape(template) + r'[\'\"]', header)
                and re.search(r'\bid\s*:\s*[\'\"]' + re.escape(tab) + r'[\'\"]', header)):
            rows, _ = DECODER.raw_decode(block[data.end():])
            if not isinstance(rows, list):
                raise ValueError('Expected a literal Listview array')
            return rows
    return []


def extract_item_page(source, expected_id):
    meta = re.search(r'<script\b[^>]*\bid="data.pageMeta"[^>]*>(.*?)</script>', source, re.S)
    if not meta:
        raise ValueError('Missing Wowhead page metadata')
    meta = json.loads(meta[1])
    if meta.get('page') != 'item' or meta.get('dataEnv', {}).get('env') != 16:
        raise ValueError('Not a Forever item page')
    start = re.search(r'\$\.extend\(g_items\[' + str(expected_id) + r'\],\s*', source)
    if not start:
        raise ValueError('Item page ID does not match the requested item')
    item, _ = DECODER.raw_decode(source[start.end():])
    if item.get('id') != expected_id or not valid_name(item.get('name')):
        raise ValueError('Invalid item identity')
    status = item.get('envChange', {}).get('status', 'unknown')
    result = dict(item_id=expected_id, name=item['name'], item_status=status,
                  quest_ids=sorted({q['id'] for q in listview_rows(source, 'quest', 'objective-of')
                                    if positive_int(q.get('id'))}), drops=[])
    for row in listview_rows(source, 'npc', 'dropped-by'):
        npc_status = row.get('envChange', {}).get('status', 'unknown')
        count, total = row.get('count'), row.get('outof')
        if status != 'new' and npc_status != 'new':
            continue
        if not (positive_int(row.get('id')) and valid_name(row.get('name'))
                and positive_int(count) and positive_int(total) and count <= total):
            continue
        modes = row.get('modes')
        if modes is not None and (modes.get('mode') != [0]
                or modes.get('0', {}).get('count') != count
                or modes.get('0', {}).get('outof') != total):
            continue
        result['drops'].append(dict(npc_id=row['id'], npc_name=row['name'],
                                    npc_status=npc_status, count=count, outof=total))
    result['drops'].sort(key=lambda row: row['npc_id'])
    return result


def merge_records(records, npcs, names):
    seen = set()
    for record in records:
        item = record['item_id']
        if not positive_int(item) or not valid_name(record['name']):
            raise ValueError('Invalid source item')
        for drop in record['drops']:
            npc, count, total = drop['npc_id'], drop['count'], drop['outof']
            if (not all(positive_int(v) for v in (npc, count, total)) or count > total
                    or (record['item_status'] != 'new' and drop['npc_status'] != 'new')):
                raise ValueError(f'Invalid Forever observation: item {item}, NPC {npc}')
            if (npc, item) in seen:
                raise ValueError(f'Duplicate Forever observation: item {item}, NPC {npc}')
            seen.add((npc, item))
            npcs.setdefault(npc, {})[item] = 100 * count / total
            names[item] = record['name']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cache', type=Path)
    parser.add_argument('catalog', type=Path)
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding='utf-8-sig'))
    records, missing, invalid = [], [], {}
    for item in sorted(catalog, key=lambda row: row['id']):
        path = args.cache / f"{item['id']}.html"
        if not path.exists():
            missing.append(item['id'])
            continue
        raw = path.read_bytes()
        try:
            record = extract_item_page(raw.decode('utf-8-sig'), item['id'])
        except (ValueError, KeyError, TypeError) as exc:
            invalid[item['id']] = str(exc)
            continue
        if record['drops']:
            record['url'] = f"https://www.wowhead.com/forever/item={item['id']}"
            record['page_sha256'] = hashlib.sha256(raw).hexdigest()
            records.append(record)
    if not records:
        raise ValueError('No usable Forever observations; existing snapshot was not changed')
    npcs, names = {}, {}
    merge_records(records, npcs, names)
    result = dict(schema=1, source='Wowhead Forever item dropped-by Listviews',
                  generated_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                  coverage=dict(catalog_items=len(catalog), parsed_items=len(catalog)-len(missing)-len(invalid),
                                missing_items=missing, invalid_pages=invalid,
                                included_items=len(records), included_npcs=len(npcs),
                                included_pairs=sum(len(rows) for rows in npcs.values())),
                  items=records)
    destination = ROOT / 'Data/Source/wowheadForeverDrops.json'
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['coverage']))


if __name__ == '__main__':
    main()
