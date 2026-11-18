#!/usr/bin/env python3
"""Read exactly two preserved instructor DOCX samples; no edits and no external calls."""
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import json
import hashlib

BASE=Path(__file__).resolve().parents[1]/"docs/guidelines/instructor-snapshots/snapshots/f074d8f2698728102a40fba6d0bacb7b4e702ea3/Lecture/FinalProject/Doc"
NS="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
FILES=["최종프로젝트_주요산출물_기획서_샘플.docx","최종프로젝트_주요산출물_WBS_샘플.docx"]

def txt(node):
    parts=[]
    for el in node.iter():
        if el.tag==NS+"t" and el.text: parts.append(el.text)
        elif el.tag==NS+"tab": parts.append(" ")
    return "".join(parts).strip()

def classify(p):
    ps=p.find(NS+"pPr")
    if ps is None:return ""
    s=ps.find(NS+"pStyle")
    return s.get(NS+"val","") if s is not None else ""

def read(path):
    if not path.is_file(): raise RuntimeError("missing sample "+str(path))
    with ZipFile(path) as z: xml=z.read("word/document.xml")
    root=ET.fromstring(xml)
    body=root.find(".//"+NS+"body")
    elems=[]
    for el in body:
        if el.tag==NS+"p":
            t=txt(el)
            if t: elems.append({"type":"paragraph","style":classify(el),"text":t})
        elif el.tag==NS+"tbl":
            rows=[]
            for tr in el.findall(NS+"tr"):
                rows.append([txt(tc) for tc in tr.findall(NS+"tc")])
            elems.append({"type":"table","rows":rows,"row_count":len(rows)})
    return {"filename":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"items":elems}

if __name__=="__main__":
    for fn in FILES:
        result=read(BASE/fn)
        print("SAMPLE_BEGIN "+result["filename"]+" SHA256 "+result["sha256"])
        for i,item in enumerate(result["items"]):
            if item["type"]=="paragraph": print(f"P[{i:03}][{item['style']}]: {item['text']}")
            else:
                print(f"TABLE[{i:03}][rows={item['row_count']}]")
                for j,row in enumerate(item["rows"]): print(f"  ROW[{j:02}]: "+ " || ".join(row))
        print("SAMPLE_END "+result["filename"])
