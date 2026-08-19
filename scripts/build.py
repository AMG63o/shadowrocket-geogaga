#!/usr/bin/env python3
import ipaddress
import json
import shutil
from pathlib import Path

SOURCE_REPO = "bratishkadrugoimamysynishka/geogaga-client-flavor"
SOURCE_REF = "lists"
SOURCE_DIR = Path("/tmp/geogaga-source")
OUT = Path("rules")


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


if not SOURCE_DIR.exists():
    raise SystemExit("Source repository is missing: /tmp/geogaga-source")

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

meta = {
    "source": SOURCE_REPO,
    "ref": SOURCE_REF,
    "sources": {},
}

for source_dir in sorted(SOURCE_DIR.iterdir()):
    if not source_dir.is_dir():
        continue
    if not (source_dir.name.endswith("-geosite") or source_dir.name.endswith("-geoip")):
        continue

    is_geosite = source_dir.name.endswith("-geosite")
    source_files = sorted(source_dir.rglob("*.lst"))
    meta["sources"][source_dir.name] = {"files": 0, "rules": 0}

    for source_file in source_files:
        text = source_file.read_text(encoding="utf-8", errors="replace")
        rules = convert_geosite(text) if is_geosite else convert_geoip(text)

        relative = source_file.relative_to(SOURCE_DIR)
        output_path = OUT / relative.with_suffix(".list")
        write_rules(output_path, rules, str(relative).replace("\\", "/"))

        meta["sources"][source_dir.name]["files"] += 1
        meta["sources"][source_dir.name]["rules"] += len(rules)

Path("rules/meta.json").write_text(
    json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print(json.dumps(meta, indent=2, ensure_ascii=False))
