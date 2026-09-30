"""Small dependency-free JSON Schema validator for the keywords used by public V1 contracts."""
from __future__ import annotations
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
CONTRACTS=ROOT/'contracts'
def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8-sig'))
def load_schema(name: str) -> dict:
    return load_json(CONTRACTS/name)
def _resolve(root: dict, ref: str):
    if not ref.startswith('#/'): raise ValueError(f'External $ref is not supported: {ref}')
    node=root
    for part in ref[2:].split('/'):
        node=node[part.replace('~1','/').replace('~0','~')]
    return node
def _is_type(value: Any, expected: Any) -> bool:
    for typ in expected if isinstance(expected,list) else [expected]:
        if typ=='null' and value is None: return True
        if typ=='object' and isinstance(value,dict): return True
        if typ=='array' and isinstance(value,list): return True
        if typ=='string' and isinstance(value,str): return True
        if typ=='boolean' and isinstance(value,bool): return True
        if typ=='integer' and isinstance(value,int) and not isinstance(value,bool): return True
        if typ=='number' and isinstance(value,(int,float)) and not isinstance(value,bool): return True
    return False
def validate(value: Any, schema: dict, root: dict|None=None, path: str='$') -> list[tuple[str,str]]:
    root=root or schema; errors=[]
    supported={'$schema','$id','title','description','$comment','$defs','$ref','type','enum','const','required','properties','additionalProperties','items','minItems','maxItems','uniqueItems','minLength','maxLength','pattern','minimum','maximum','format','allOf','if','then','not'}
    unknown=set(schema)-supported
    if unknown: return [(path,f'unsupported schema keyword(s): {sorted(unknown)}')]
    if '$ref' in schema:
        try: errors += validate(value,_resolve(root,schema['$ref']),root,path)
        except Exception as exc: return [(path,f'$ref resolution failed: {exc}')]
    if 'type' in schema and not _is_type(value,schema['type']): return errors+[(path,f'expected {schema["type"]}, got {type(value).__name__}')]
    if 'const' in schema and value!=schema['const']: errors.append((path,f'must equal {schema["const"]!r}'))
    if 'enum' in schema and value not in schema['enum']: errors.append((path,f'must be one of {schema["enum"]!r}'))
    if isinstance(value,dict):
        for key in schema.get('required',[]):
            if key not in value: errors.append((f'{path}.{key}','required field is missing'))
        props=schema.get('properties',{})
        for key,item in value.items():
            child=f'{path}.{key}'
            if key in props: errors+=validate(item,props[key],root,child)
            elif schema.get('additionalProperties') is False: errors.append((child,'additional property is not allowed'))
            elif isinstance(schema.get('additionalProperties'),dict): errors+=validate(item,schema['additionalProperties'],root,child)
    if isinstance(value,list):
        if len(value)<schema.get('minItems',0): errors.append((path,f'must contain at least {schema["minItems"]} item(s)'))
        if len(value)>schema.get('maxItems',float('inf')): errors.append((path,f'must contain at most {schema["maxItems"]} item(s)'))
        if schema.get('uniqueItems') and len({json.dumps(x,sort_keys=True,ensure_ascii=False) for x in value})!=len(value): errors.append((path,'items must be unique'))
        if 'items' in schema:
            for i,item in enumerate(value): errors+=validate(item,schema['items'],root,f'{path}[{i}]')
    if isinstance(value,str):
        if len(value)<schema.get('minLength',0): errors.append((path,f'must have at least {schema["minLength"]} character(s)'))
        if len(value)>schema.get('maxLength',float('inf')): errors.append((path,f'must have at most {schema["maxLength"]} character(s)'))
        if 'pattern' in schema and re.search(schema['pattern'],value) is None: errors.append((path,'does not match required pattern'))
        if schema.get('format')=='date-time':
            try: dt.datetime.fromisoformat(value.replace('Z','+00:00'))
            except ValueError: errors.append((path,'must be ISO date-time'))
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        if value<schema.get('minimum',float('-inf')): errors.append((path,f'must be >= {schema["minimum"]}'))
        if value>schema.get('maximum',float('inf')): errors.append((path,f'must be <= {schema["maximum"]}'))
    for sub in schema.get('allOf',[]): errors+=validate(value,sub,root,path)
    if 'if' in schema and not validate(value,schema['if'],root,path) and 'then' in schema: errors+=validate(value,schema['then'],root,path)
    if 'not' in schema and not validate(value,schema['not'],root,path): errors.append((path,'matches a forbidden schema'))
    return errors
def validate_instance(name: str, instance: Any):
    schema=load_schema(name)
    return validate(instance,schema,schema)
