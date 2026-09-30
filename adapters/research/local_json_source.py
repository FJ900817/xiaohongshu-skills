"""Offline adapter for explicit user-supplied JSON, CSV and Markdown sources."""
from __future__ import annotations
import csv
import json
from pathlib import Path

def load_sources(path: Path) -> list[dict]:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == '.json':
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        rows = data.get('sources') if isinstance(data, dict) else data
        if not isinstance(rows, list): raise ValueError('JSON source must be an array or contain a sources array')
    elif suffix == '.csv':
        with path.open('r', encoding='utf-8-sig', newline='') as f: rows = list(csv.DictReader(f))
        for i, row in enumerate(rows):
            row['source_type'] = 'csv'
            row['synthetic'] = str(row.get('synthetic', '')).lower() == 'true'
            for field in ('user_questions','user_problems','candidate_topics','limitations'):
                value = row.get(field)
                if value: row[field] = [x.strip() for x in value.split('|') if x.strip()]
                else: row[field] = []
            row['phrases'] = []
            for pair in filter(None, row.get('phrases_text','').split('|')):
                phrase, _, intent = pair.partition('::'); row['phrases'].append([phrase.strip(), intent.strip() or 'unspecified'])
            row.pop('phrases_text', None)
    elif suffix in ('.md', '.markdown', '.txt'):
        text = path.read_text(encoding='utf-8-sig')
        rows = [{'source_id':path.stem,'source_type':'user_upload','title':path.stem,'uri':path.name,'summary':text[:500], 'excerpt':text[:3000], 'synthetic':False,'limitations':['仅代表用户提供的本地文档，未验证总体代表性。'],'user_questions':[],'user_problems':[],'phrases':[],'candidate_topics':[]}]
    else: raise ValueError(f'unsupported local source format: {suffix}')
    for i, source in enumerate(rows):
        if not isinstance(source, dict) or not source.get('source_id') or not source.get('title'):
            raise ValueError(f'sources[{i}] needs source_id and title')
        source.setdefault('source_type', 'local_json')
    return rows
