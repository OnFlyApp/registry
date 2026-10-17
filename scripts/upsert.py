#!/usr/bin/env python3
"""Insert one plugin release into registry.json."""

import argparse
import json
import re
import sys

NAME = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
VER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
SHA = re.compile(r"^[0-9a-f]{64}$")


def version_less(a, b):
    aa = a.split("-", 1)[0].split(".")
    bb = b.split("-", 1)[0].split(".")
    for i in range(max(len(aa), len(bb))):
        try:
            ai = int(aa[i]) if i < len(aa) else 0
            bi = int(bb[i]) if i < len(bb) else 0
        except ValueError:
            return a < b
        if ai != bi:
            return ai < bi
    return False


def norm_ext(raw):
    out = []
    for item in raw.split(","):
        item = item.strip().lower()
        if item == "":
            continue
        if not item.startswith("."):
            item = "." + item
        out.append(item)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--plugin", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--extensions", required=True)
    args = parser.parse_args()
    if NAME.fullmatch(args.plugin) is None:
        sys.exit("invalid plugin name %r" % args.plugin)
    if VER.fullmatch(args.version) is None:
        sys.exit("invalid version %r" % args.version)
    if not args.url.startswith("https://") or any(ch in args.url for ch in " \t[]()"):
        sys.exit("url must be a plain https string")
    sha = args.sha256.strip().lower()
    if SHA.fullmatch(sha) is None:
        sys.exit("sha256 must be 64 hex characters")
    exts = norm_ext(args.extensions)
    if not exts:
        sys.exit("extensions are required")
    with open(args.path, encoding="utf-8") as handle:
        text = handle.read()
    data = json.loads(text) if text.strip() else {}
    if not isinstance(data, dict):
        sys.exit("registry root must be an object")
    plugin = data.get(args.plugin) or {"latest": "", "versions": {}}
    versions = plugin.setdefault("versions", {})
    release = {"url": args.url, "sha256": sha, "extensions": exts}
    old = versions.get(args.version)
    if old is not None and old != release:
        sys.exit("version %s already exists with different bytes" % args.version)
    versions[args.version] = release
    latest = plugin.get("latest") or ""
    if latest == "" or version_less(latest, args.version):
        plugin["latest"] = args.version
    data[args.plugin] = plugin
    out = json.dumps(data, indent=2, sort_keys=True) + "\n"
    with open(args.path, "w", encoding="utf-8") as handle:
        handle.write(out)


if __name__ == "__main__":
    main()
