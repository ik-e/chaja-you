#!/usr/bin/env python3
"""Copy full FinalProject course originals from a pinned Gitea commit.

No crawling: only the instructor-provided public Git repo and its FinalProject directory.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"docs/guidelines/instructor-snapshots/snapshots"
REPO="https://gt.isitsoft.kr/publicproj/aio-01d4-stu.git"
SUBDIR=Path("Lecture/FinalProject")
MAX_BYTES=250_000_000
MAX_FILES=1000

def sh(*args,cwd=None,timeout=180):
    return subprocess.check_output(list(args),cwd=cwd,stderr=subprocess.STDOUT,timeout=timeout).decode().strip()

def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        while True:
            buf=f.read(1024*1024)
            if not buf: break
            h.update(buf)
    return h.hexdigest()

def manifest_from_dir(path):
    entries=[]
    for p in sorted(path.rglob("*")):
        if p.is_symlink(): raise RuntimeError("source symlink not supported: "+str(p))
        if not p.is_file(): continue
        if p.name=="manifest.json" and p.parent==path: continue
        rel=p.relative_to(path).as_posix()
        if ".." in Path(rel).parts: raise RuntimeError("unsafe file path")
        entries.append({"path":rel,"bytes":p.stat().st_size,"sha256":digest(p)})
    return entries

def archive():
    OUT.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="course-finalproject-") as temp:
        repo=Path(temp)/"source"
        sh("git","clone","--depth","1","--filter=blob:none","--sparse","--single-branch","--branch","main",REPO,str(repo),timeout=240)
        sh("git","sparse-checkout","set",SUBDIR.as_posix(),cwd=repo,timeout=180)
        commit=sh("git","rev-parse","HEAD",cwd=repo)
        src=repo/SUBDIR
        if not src.is_dir(): raise RuntimeError("FinalProject not found at pinned commit")
        paths=sh("git","ls-files","--cached","--",SUBDIR.as_posix(),cwd=repo).splitlines()
        if not paths or len(paths)>MAX_FILES:
            raise RuntimeError("unexpected source file count: "+str(len(paths)))
        sizes=sum((repo/p).stat().st_size for p in paths)
        if sizes>MAX_BYTES:
            raise RuntimeError("unexpected total size: "+str(sizes))
        target=OUT/commit
        if target.exists():
            verify_one(target)
            print("Already archived original commit",commit)
            return
        copy=Path(temp)/"snapshot"
        for name in paths:
            p=repo/name
            if not p.is_file() or p.is_symlink(): raise RuntimeError("source is not an ordinary file: "+name)
            rel=Path(name)
            dest=copy/rel
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(p,dest)
        entries=manifest_from_dir(copy)
        if len(entries)!=len(paths):
            raise RuntimeError("file inventory does not match git ls-files")
        manifest={"schema_version":1,"kind":"full_course_originals_git_snapshot",
          "source_repo":REPO,"source_branch":"main","source_commit":commit,
          "source_subdir":str(SUBDIR),"archive_utc":datetime.now(timezone.utc).isoformat(),
          "origin_permission":"R01 reports instructor verbal permission for GitHub preservation (2026-11-18)",
          "preservation":"unaltered original bytes; any new original commit is a new immutable snapshot",
          "file_count":len(entries),"total_bytes":sum(x["bytes"] for x in entries),
          "files":entries}
        (copy/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(str(copy),str(target))
        verify_one(target)
        print("Archived original source",commit,"files",len(entries),"bytes",manifest["total_bytes"])

def verify_one(target):
    m=json.loads((target/"manifest.json").read_text(encoding="utf-8"))
    if target.name!=m["source_commit"] or m["source_subdir"]!=str(SUBDIR):
        raise RuntimeError("snapshot name/source mismatch")
    entries=manifest_from_dir(target)
    if entries!=m["files"] or len(entries)!=m["file_count"] or sum(x["bytes"] for x in entries)!=m["total_bytes"]:
        raise RuntimeError("file/size/hash mismatch: "+str(target))
    print("Verified",target.name,"files",len(entries),"bytes",m["total_bytes"])

def main():
    ap=argparse.ArgumentParser()
    x=ap.add_mutually_exclusive_group(required=True)
    x.add_argument("--archive",action="store_true")
    x.add_argument("--verify",action="store_true")
    a=ap.parse_args()
    if a.archive: archive()
    else:
        folders=[p for p in OUT.iterdir() if p.is_dir()] if OUT.exists() else []
        if not folders: raise SystemExit("No full original snapshot saved yet")
        for p in sorted(folders): verify_one(p)
if __name__=="__main__":
    main()
