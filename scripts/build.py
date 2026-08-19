#!/usr/bin/env python3
import json
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


def list_dir(path):
    return get_json(f"{API_ROOT}/{path}?ref={SOURCE_REF}")


def raw(path):
    req = urllib.request.Request(f"{RAW_ROOT}/{path}", headers={"User-Agent": "shadowrocket-geogaga"})
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read().decode("utf-8", errors="replace")


def collect_lst_files(directory):
    result = []
    for item in list_dir(directory):
        if item["type"] == "file" and item["name"].lower().endswith(".lst"):
            result.append(item["path"])
        elif item["type"] == "dir":
            result.extend(collect_lst_files(item["path"]))
    return result


def build_geosite():
    domains = set()
    source_files = collect_lst_files("runetfreedom-geosite")
    for path in source_files:
        for line in raw(path).splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("domain:"):
                value = line[len("domain:"):].strip().lower().rstrip(".")
                if value:
                    domains.add(f"DOMAIN-SUFFIX,{value}")
            elif line.startswith("full:"):
                value = line[len("full:"):].strip().lower().rstrip(".")
                if value:
                    domains.add(f"DOMAIN,{value}")
            elif line.startswith("keyword:"):
                value = line[len("keyword:"):].strip()
                if value:
                    domains.add(f"DOMAIN-KEYWORD,{value}")
    return sorted(domains), len(source_files)


def build_geoip():
    networks = set()
    source_files = collect_lst_files("runetfreedom-geoip")
    for path in source_files:
        for line in raw(path).splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "/" in line or line.count(".") == 3:
                networks.add(f"IP-CIDR,{line}")
    return sorted(networks), len(source_files)


def write(path, lines, header):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = header + "\n" + "\n".join(lines) + "\n"
    path.write_text(content, encoding="utf-8")


OUT.mkdir(exist_ok=True)
geosite, geosite_files = build_geosite()
geoip, geoip_files = build_geoip()

write(OUT / "runetfreedom-geosite.list", geosite,
      "# GeoGaGa RunetFreedom geosite -> Shadowrocket RULE-SET\n# Generated automatically. Do not edit manually.\n")
write(OUT / "runetfreedom-geoip.list", geoip,
      "# GeoGaGa RunetFreedom geoip -> Shadowrocket RULE-SET\n# Generated automatically. Do not edit manually.\n")

meta = {
    "source": SOURCE_REPO,
    "ref": SOURCE_REF,
    "geosite_source_files": geosite_files,
    "geoip_source_files": geoip_files,
    "geosite_rules": len(geosite),
    "geoip_rules": len(geoip),
}
Path("rules/meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
print(json.dumps(meta, indent=2))
