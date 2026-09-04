#!/usr/bin/env python3
import ipaddress
import json
import shutil
from pathlib import Path

SOURCE_REPO = "bratishkadrugoimamysynishka/geogaga-client-flavor"
SOURCE_REF = "lists"
SOURCE_DIR = Path("/tmp/geogaga-source")
OUT = Path("rules")
STAGING = Path("/tmp/geogaga-rules")

REQUIRED_SOURCE_FILES = (
    "Client-Flavor-geosite/GEOGAGA-BLOCK.lst",
    "Client-Flavor-geosite/GEOGAGA-DIRECT.lst",
    "Client-Flavor-geosite/GEOGAGA-PROXY.lst",
    "Client-Flavor-geoip/GEOGAGA-BLOCK.lst",
    "Client-Flavor-geoip/GEOGAGA-DIRECT.lst",
    "Client-Flavor-geoip/GEOGAGA-PROXY.lst",
)


def convert_geosite(text):
    rules = []
    seen = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        kind, value = line.split(":", 1)
        kind = kind.strip().lower()
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


def fail(message):
    raise SystemExit(f"ERROR: {message}")


if not SOURCE_DIR.exists():
    fail(f"Source repository is missing: {SOURCE_DIR}")

missing = [path for path in REQUIRED_SOURCE_FILES if not (SOURCE_DIR / path).is_file()]
if missing:
    fail("Upstream lists are incomplete; refusing to replace current rules. Missing: " + ", ".join(missing))

source_dirs = [
    path for path in sorted(SOURCE_DIR.iterdir())
    if path.is_dir() and (path.name.endswith("-geosite") or path.name.endswith("-geoip"))
]
if not source_dirs:
    fail("No *-geosite or *-geoip source directories were found.")

if STAGING.exists():
    shutil.rmtree(STAGING)
STAGING.mkdir(parents=True)

meta = {"source": SOURCE_REPO, "ref": SOURCE_REF, "sources": {}}
generated_files = 0
generated_rules = 0

for source_dir in source_dirs:
    is_geosite = source_dir.name.endswith("-geosite")
    source_files = sorted(source_dir.rglob("*.lst"))
    meta["sources"][source_dir.name] = {"files": 0, "rules": 0}

    for source_file in source_files:
        text = source_file.read_text(encoding="utf-8", errors="replace")
        rules = convert_geosite(text) if is_geosite else convert_geoip(text)
        relative = source_file.relative_to(SOURCE_DIR)
        output_path = STAGING / relative.with_suffix(".list")
        write_rules(output_path, rules, str(relative).replace("\\", "/"))
        meta["sources"][source_dir.name]["files"] += 1
        meta["sources"][source_dir.name]["rules"] += len(rules)
        generated_files += 1
        generated_rules += len(rules)

if generated_files == 0:
    fail("No .lst files were converted; refusing to replace current rules.")

for required in REQUIRED_SOURCE_FILES:
    output_path = STAGING / Path(required).with_suffix(".list")
    if not output_path.is_file():
        fail(f"Required output was not generated: {output_path}")

for required in ("Client-Flavor-geosite/GEOGAGA-DIRECT.lst", "Client-Flavor-geosite/GEOGAGA-PROXY.lst"):
    output_path = STAGING / Path(required).with_suffix(".list")
    if not any(line and not line.startswith("#") for line in output_path.read_text(encoding="utf-8").splitlines()):
        fail(f"Required output contains no rules: {output_path}")

meta["generated_files"] = generated_files
meta["generated_rules"] = generated_rules
(STAGING / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

if OUT.exists():
    shutil.rmtree(OUT)
STAGING.rename(OUT)
print(json.dumps(meta, indent=2, ensure_ascii=False))
