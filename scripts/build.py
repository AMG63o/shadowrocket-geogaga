#!/usr/bin/env python3
import ipaddress
import json
import shutil
import urllib.request
from pathlib import Path

SOURCE_REPO = "bratishkadrugoimamysynishka/geogaga-client-flavor"
SOURCE_REF = "lists"
API_ROOT = f"https://api.github.com/repos/{SOURCE_REPO}/contents"
RAW_ROOT = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_REF}"
OUT = Path("rules")


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "shadowrocket-geogaga"})
    with urllib.request.urlopen(req, timeout=90) as response:
        return json.load(response)


def list_dir(path=""):
    suffix = f"/{path}" if path else ""
    return get_json(f"{API_ROOT}{suffix}?ref={SOURCE_REF}")


def raw(path):
    req = urllib.request.Request(f"{RAW_ROOT}/{path}", headers={"User-Agent": "shadowrocket-geogaga"})
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read().decode("utf-8", errors="replace")


def top_level_sources():
    sources = []
    for item in list_dir():
        if item["type"] == "dir" and (item["name"].endswith("-geosite") or item["name"].endswith("-geoip")):
            sources.append(item["name"])
    return sorted(sources)


def collect_lst_files(directory):
    result = []
    for item in list_dir(directory):
        if item["type"] == "file" and item["name"].lower().endswith(".lst"):
            result.append(item["path"])
        elif item["type"] == "dir":
            result.extend(collect_lst_files(item["path"]))
    return sorted(result)


def convert_geosite(text):
    rules = []
    seen = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        kind, value = line.split(":", 1)
        value = value.strip()
        if not value:
            continue
        value_no_dot = value.lower().rstrip(".")
        if kind == "domain":
            rule = f"DOMAIN-SUFFIX,{value_no_dot}"
        elif kind == "full":
            rule = f"DOMAIN,{value_no_dot}"
        elif kind == "keyword":
            rule = f"DOMAIN-KEYWORD,{value}"
        elif kind == "regex":
            rule = f"DOMAIN-REGEX,{value}"
        else:
            continue
        if rule not in seen:
            seen.add(rule)
            rules.append(rule)
    return rules


def convert_geoip(text):
    rules = []
    seen = set()
    for line in text.splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        try:
            network = ipaddress.ip_network(value, strict=False)
        except ValueError:
            continue
        kind = "IP-CIDR6" if network.version == 6 else "IP-CIDR"
        rule = f"{kind},{value}"
        if rule not in seen:
            seen.add(rule)
            rules.append(rule)
    return rules


def write_rules(path, rules, source_path):
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# GeoGaGa -> Shadowrocket RULE-SET\n"
        f"# Source: {SOURCE_REPO}/{source_path}\n"
        f"# Source branch: {SOURCE_REF}\n"
        "# Generated automatically.\n"
    )
    path.write_text(header + "\n".join(rules) + "\n", encoding="utf-8")


if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

meta = {
    "source": SOURCE_REPO,
    "ref": SOURCE_REF,
    "sources": {},
}

for source in top_level_sources():
    is_geosite = source.endswith("-geosite")
    source_files = collect_lst_files(source)
    meta["sources"][source] = {"files": 0, "rules": 0}

    for source_path in source_files:
        text = raw(source_path)
        rules = convert_geosite(text) if is_geosite else convert_geoip(text)

        relative = source_path[len(source) + 1:]
        output_name = str(Path(relative).with_suffix(".list"))
        output_path = OUT / source / output_name
        write_rules(output_path, rules, source_path)

        meta["sources"][source]["files"] += 1
        meta["sources"][source]["rules"] += len(rules)

Path("rules/meta.json").write_text(
    json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

print(json.dumps(meta, indent=2, ensure_ascii=False))
