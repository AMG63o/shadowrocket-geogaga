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

GEOSITE_SOURCE = "Client-Flavor-geosite"
GEOIP_SOURCE = "Client-Flavor-geoip"
CATEGORIES = ("GEOGAGA-DIRECT", "GEOGAGA-PROXY", "GEOGAGA-BLOCK")


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "shadowrocket-geogaga"})
    with urllib.request.urlopen(req, timeout=90) as response:
        return json.load(response)


def raw(path):
    req = urllib.request.Request(f"{RAW_ROOT}/{path}", headers={"User-Agent": "shadowrocket-geogaga"})
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read().decode("utf-8", errors="replace")


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
        if kind == "domain":
            rule = f"DOMAIN-SUFFIX,{value.lower().rstrip('.') }"
        elif kind == "full":
            rule = f"DOMAIN,{value.lower().rstrip('.') }"
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


def write_rules(path, rules, title):
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"# {title}\n"
        "# Source: bratishkadrugoimamysynishka/geogaga-client-flavor\n"
        "# Source branch: lists\n"
        "# Generated automatically for Shadowrocket.\n"
    )
    path.write_text(header + "\n".join(rules) + "\n", encoding="utf-8")


if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

meta = {
    "source": SOURCE_REPO,
    "ref": SOURCE_REF,
    "geosite_source": GEOSITE_SOURCE,
    "geoip_source": GEOIP_SOURCE,
    "categories": {},
}

for category in CATEGORIES:
    geosite_rules = convert_geosite(raw(f"{GEOSITE_SOURCE}/{category}.lst"))
    geoip_rules = convert_geoip(raw(f"{GEOIP_SOURCE}/{category}.lst"))

    write_rules(
        OUT / "geosite" / f"{category}.list",
        geosite_rules,
        f"GeoGaGa {category} geosite",
    )
    write_rules(
        OUT / "geoip" / f"{category}.list",
        geoip_rules,
        f"GeoGaGa {category} geoip",
    )

    meta["categories"][category] = {
        "geosite_rules": len(geosite_rules),
        "geoip_rules": len(geoip_rules),
    }

# Ready-to-paste Shadowrocket rules using standard policy names.
config = [
    "# GeoGaGa Client-Flavor -> Shadowrocket",
    "# Replace PROXY with your actual proxy policy name if needed.",
    "[Rule]",
    "RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geosite/GEOGAGA-BLOCK.list,REJECT",
    "RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geosite/GEOGAGA-DIRECT.list,DIRECT",
    "RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geosite/GEOGAGA-PROXY.list,PROXY",
    "RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geoip/GEOGAGA-BLOCK.list,REJECT",
    "RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geoip/GEOGAGA-DIRECT.list,DIRECT",
    "RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geoip/GEOGAGA-PROXY.list,PROXY",
]
(OUT / "shadowrocket-rules.conf").write_text("\n".join(config) + "\n", encoding="utf-8")

Path("rules/meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(meta, indent=2, ensure_ascii=False))
