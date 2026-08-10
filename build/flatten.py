# -*- coding: utf-8 -*-
"""Flatten each component's members across its (possibly multi-) inheritance
chain, annotating the defining source and whether a member is an override."""
import json


def load():
    with open("components_raw.json", encoding="utf-8") as f:
        return json.load(f)


def collect(name, raw, cache, visited):
    """Return {properties, events, methods} keyed by member name -> item.
    Leafmost definition wins (child overrides parent)."""
    if name in cache:
        return cache[name]
    if name in visited:
        return {"properties": {}, "events": {}, "methods": {}}
    visited.add(name)
    comp = raw[name]
    props, events, methods = {}, {}, {}
    for it in comp.get("properties", []):
        props[it["name"]] = dict(it, source=name, overridden=False)
    for it in comp.get("events", []):
        events[it["name"]] = dict(it, source=name, overridden=False)
    for it in comp.get("methods", []):
        methods[it["name"]] = dict(it, source=name, overridden=False)
    for parent in comp.get("extends", []):
        if parent not in raw:
            continue
        pd = collect(parent, raw, cache, visited)
        for k, v in pd["properties"].items():
            if k not in props:
                props[k] = dict(v, overridden=False)
        for k, v in pd["events"].items():
            if k not in events:
                events[k] = dict(v, overridden=False)
        for k, v in pd["methods"].items():
            if k not in methods:
                methods[k] = dict(v, overridden=False)
    visited.discard(name)
    res = {"properties": props, "events": events, "methods": methods}
    cache[name] = res
    return res


def ancestor_names(name, raw, cat, visited=None):
    """Union of member names from all ancestors (excluding self)."""
    if visited is None:
        visited = set()
    if name in visited:
        return set()
    visited.add(name)
    out = set()
    for parent in raw.get(name, {}).get("extends", []):
        if parent not in raw:
            continue
        pdata = collect(parent, raw, {}, set())
        out.update(pdata[cat].keys())
        out.update(ancestor_names(parent, raw, cat, visited))
    return out


def chains(name, raw, prefix=None):
    """All root-to-leaf paths through the inheritance DAG (leaf at front)."""
    if prefix is None:
        prefix = [name]
    comp = raw.get(name, {})
    parents = comp.get("extends", [])
    if not parents:
        return [list(prefix)]
    result = []
    for p in parents:
        if p not in raw:
            continue
        result.extend(chains(p, raw, [p] + prefix))
    return result


def flatten_component(name, raw):
    comp = raw[name]
    data = collect(name, raw, {}, set())
    # sort each category by name
    props = sorted(data["properties"].values(), key=lambda x: x["name"].lower())
    events = sorted(data["events"].values(), key=lambda x: x["name"].lower())
    methods = sorted(data["methods"].values(), key=lambda x: x["name"].lower())
    # override detection: own members (source==name) whose name also appears in ancestors
    for cat, lst in (("properties", props), ("events", events), ("methods", methods)):
        anc = ancestor_names(name, raw, cat)
        for it in lst:
            if it["source"] == name and it["name"] in anc:
                it["overridden"] = True
    return {
        "name": name,
        "display": comp.get("display", name),
        "category": comp.get("category", ""),
        "url": comp.get("url", ""),
        "extends": comp.get("extends", []),
        "depends": comp.get("depends", []),
        "desc": comp.get("desc", ""),
        "inheritance_chains": chains(name, raw),
        "properties": props,
        "events": events,
        "methods": methods,
        "counts": {"properties": len(props), "events": len(events), "methods": len(methods)},
    }


def main():
    raw = load()
    flat = {}
    for name in raw:
        flat[name] = flatten_component(name, raw)
    with open("components_flat.json", "w", encoding="utf-8") as f:
        json.dump(flat, f, ensure_ascii=False, indent=2)
    # quick report
    for name in sorted(raw):
        c = flat[name]
        print(f"{name:14s} extends={c['extends']} "
              f"P={c['counts']['properties']} E={c['counts']['events']} M={c['counts']['methods']}")
    print(f"\nFlattened {len(flat)} components -> components_flat.json")


if __name__ == "__main__":
    main()
