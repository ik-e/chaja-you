#!/usr/bin/env python3
"""Archive explicitly listed, instructor-permitted public course originals without crawling."""
import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"docs/guidelines/originals/2026-11-12_a512febe31"
MANIFEST=BASE/"manifest.json"

def verify(entry):
    path=ROOT/entry["archived_path"]
    if not path.is_file():
        raise ValueError("missing original: "+str(path.relative_to(ROOT)))
    raw=path.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if len(raw)!=entry["expected_bytes"] or sha!=entry["expected_sha256"]:
        raise ValueError("hash/size mismatch for "+entry["name"])
    if path.suffix.lower()==".docx":
        with zipfile.ZipFile(path) as z:
            if "word/document.xml" not in z.namelist():
                raise ValueError("DOCX lacks word/document.xml: "+entry["name"])
    if path.suffix.lower()==".pdf" and not raw.startswith(b"%PDF"):
        raise ValueError("not a PDF: "+entry["name"])
    return sha

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--download",action="store_true",help="download precisely fixed files, verify and do not overwrite conflicting originals")
    ap.add_argument("--check",action="store_true",help="verify originals already saved in this repo")
    args=ap.parse_args()
    if args.download==args.check:
        ap.error("choose exactly one of --download or --check")
    m=json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries=m["files"]
    if len(entries)!=13 or m["snapshot_source_commit"]!="a512febe318739fc6e926abd0328d12585336378":
        raise ValueError("unexpected original source manifest")
    for item in entries:
        if "/raw/commit/"+m["snapshot_source_commit"]+"/" not in item["source_raw"]:
            raise ValueError("source is not pinned to the declared commit: "+item["name"])
        path=ROOT/item["archived_path"]
        if not path.is_relative_to(BASE) or path.suffix.lower() not in {".docx",".pdf",".html",".md"}:
            raise ValueError("unsupported path: "+str(path))
        if args.download and not path.exists():
            path.parent.mkdir(parents=True,exist_ok=True)
            req=urllib.request.Request(item["source_raw"],headers={"User-Agent":"chaja-you-course-source-archive/1.0"})
            with urllib.request.urlopen(req,timeout=45) as res:
                content=res.read(item["expected_bytes"]+1)
            if len(content)!=item["expected_bytes"] or hashlib.sha256(content).hexdigest()!=item["expected_sha256"]:
                raise ValueError("download failed checksum: "+item["name"]+"; refused to store")
            path.write_bytes(content)
            time.sleep(0.25)
        verify(item)
        print("Verified",item["id"],item["name"],item["expected_bytes"],item["expected_sha256"][:12])
    print("SUCCESS: all 13 original source bytes verified; total expected size",
          sum(x["expected_bytes"] for x in entries))

if __name__=="__main__":
    main()
