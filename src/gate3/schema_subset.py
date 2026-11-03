"""Narrow stdlib JSON-Schema subset validator. No third-party dependency."""
from __future__ import annotations

def validate(instance, schema, path="$"):
    errors=[]
    _validate(instance,schema,path,errors)
    return errors

def _type_ok(value,t):
    return {
        "object":isinstance(value,dict),"array":isinstance(value,list),"string":isinstance(value,str),
        "integer":isinstance(value,int) and not isinstance(value,bool),
        "number":isinstance(value,(int,float)) and not isinstance(value,bool),
        "boolean":isinstance(value,bool),"null":value is None,
    }[t]

def _const_match(inst,const):
    """Strict JSON identity for `const`. JSON (and JSON Schema) keep booleans and
    numbers distinct, but Python equates False==0 and True==1. A bool on EITHER
    side therefore requires a bool on both; numbers still compare mathematically
    so 1 and 1.0 remain the same JSON value."""
    if isinstance(inst,bool) or isinstance(const,bool):
        return isinstance(inst,bool) and isinstance(const,bool) and inst is const
    return inst==const

def _validate(inst,schema,path,errors):
    if not isinstance(schema,dict): return
    if "type" in schema:
        types=schema["type"] if isinstance(schema["type"],list) else [schema["type"]]
        if not any(_type_ok(inst,t) for t in types):
            errors.append(f"{path}: expected {types}, got {type(inst).__name__}"); return
    if "const" in schema and not _const_match(inst,schema["const"]): errors.append(f"{path}: expected const {schema['const']!r}, got {inst!r}")
    if "enum" in schema and inst not in schema["enum"]: errors.append(f"{path}: {inst!r} not in enum {schema['enum']}")
    if isinstance(inst,str) and "minLength" in schema and len(inst)<schema["minLength"]: errors.append(f"{path}: shorter than minLength {schema['minLength']}")
    if isinstance(inst,int) and not isinstance(inst,bool) and "minimum" in schema and inst<schema["minimum"]: errors.append(f"{path}: below minimum {schema['minimum']}")
    if isinstance(inst,list) and "minItems" in schema and len(inst)<schema["minItems"]: errors.append(f"{path}: shorter than minItems {schema['minItems']}")
    for clause in schema.get("allOf",[]):
        if "if" in clause:
            if not validate(inst,clause["if"],path): _validate(inst,clause.get("then",{}),path,errors)
        else: _validate(inst,clause,path,errors)
    if isinstance(inst,dict):
        for key in schema.get("required",[]):
            if key not in inst: errors.append(f"{path}: missing required {key!r}")
        props=schema.get("properties",{})
        if schema.get("additionalProperties") is False:
            for key in inst:
                if key not in props: errors.append(f"{path}: additional property {key!r} not admitted")
        for key,sub in props.items():
            if key in inst: _validate(inst[key],sub,f"{path}.{key}",errors)
    if isinstance(inst,list) and "items" in schema:
        for i,item in enumerate(inst): _validate(item,schema["items"],f"{path}[{i}]",errors)
