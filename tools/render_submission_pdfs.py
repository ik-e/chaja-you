#!/usr/bin/env python3
"""Render the four canonical submission projections; no product execution."""
from pathlib import Path
from datetime import date, timedelta
import subprocess, sys, json, re, html, hashlib, posixpath, os
import xml.etree.ElementTree as ET
from urllib.parse import quote, urlsplit
from bs4 import BeautifulSoup
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"submission-pdf"
PREVIEW=ROOT/"submission-preview"
OUT.mkdir(exist_ok=True); PREVIEW.mkdir(exist_ok=True)
COMMIT=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
ITEMS=[
 ("01_기획서","docs/step1/기획서_제출본.md",False),
 ("02_WBS","docs/step1/WBS_제출본.md",True),
 ("03_API_설계서","docs/step2/API_설계_문서.md",False),
 ("04_DB_스키마_설계서","docs/step2/데이터베이스_스키마_설계서.md",True),
]
def run(args, **kw):
    return subprocess.run(args,check=True,**kw)
def esc(x): return html.escape(str(x))
def q(x): return json.dumps(str(x),ensure_ascii=False)
def render_flow(code, dest):
    nodes={}; edges=[]
    for line in code.splitlines()[1:]:
        m=re.fullmatch(r"\s*(\w+)(?:\[(.*?)\])?\s*-->\s*(?:\|(.*?)\|\s*)?(\w+)(?:\[(.*?)\])?\s*",line)
        if not m:
            if line.strip(): raise ValueError("unparsed flow: "+line)
            continue
        a,al,edge,b,bl=m.groups()
        if al:nodes[a]=al
        if bl:nodes[b]=bl
        edges.append((a,b,edge or ""))
    dot=['digraph G {','graph [rankdir=TB,bgcolor="transparent",pad=0.18,nodesep=0.33,ranksep=0.36];','node [shape=box,style="rounded,filled",fillcolor="#F0F5FA",color="#7B91AA",fontname="Noto Sans CJK KR",fontsize=12,margin="0.15,0.10"];','edge [color="#60758E",fontname="Noto Sans CJK KR",fontsize=10,arrowsize=0.7];']
    dot += [f'{n} [label={q(label)}];' for n,label in nodes.items()]
    dot += [f'{a} -> {b} [label={q(label)}];' for a,b,label in edges]
    dot.append("}")
    run(["dot","-Tsvg","-o",str(dest)],input="\n".join(dot),text=True)
def render_er(code,dest):
    nodes=set();edges=[]
    for line in code.splitlines()[1:]:
        m=re.fullmatch(r"\s*(\w+)\s+(\|\||o\|)--(o\{|\|\||o\|)\s+(\w+)\s*:\s*(.*?)\s*",line)
        if not m:
            if line.strip(): raise ValueError("unparsed ER: "+line)
            continue
        a,l,r,b,label=m.groups();nodes.update([a,b]);edges.append((a,b,l,r,label))
    dot=['digraph G {','graph [rankdir=TB,bgcolor="transparent",pad=0.15,nodesep=0.30,ranksep=0.60,splines=polyline];','node [shape=box,style="rounded,filled",fillcolor="#EDF3F9",color="#8398AE",fontname="Noto Sans CJK KR",fontsize=11,margin="0.10,0.08"];','edge [color="#60758E",fontname="Noto Sans CJK KR",fontsize=9,arrowsize=0.5,dir=none];']
    card={"||":"1","o|":"0..1","o{":"0..N"}
    dot += [f'{n} [label={q(n)}];' for n in sorted(nodes)]
    dot += [f'{a} -> {b} [label={q(label)},taillabel={q(card[l])},headlabel={q(card[r])},labeldistance=1.5];' for a,b,l,r,label in edges]
    dot.append("}")
    run(["dot","-Tsvg","-o",str(dest)],input="\n".join(dot),text=True)
def render_gantt(code,dest):
    rows=[];title=""
    for line in code.splitlines()[1:]:
        x=line.strip()
        if not x: continue
        if x.startswith("title "):title=x[6:];continue
        if x.startswith(("dateFormat ","axisFormat ")):continue
        if x.startswith("section "):rows.append(("section",x[8:]));continue
        label,sep,params=x.partition(":")
        if not sep:raise ValueError("bad gantt "+line)
        vals=[v.strip() for v in params.split(",")]
        status=vals.pop(0) if vals[0] in ("active","done","milestone","crit") else "planned"
        if len(vals)!=3:raise ValueError("bad gantt params "+line)
        _,start,end=vals;start=date.fromisoformat(start)
        end=start+timedelta(days=int(end[:-1])) if end.endswith("d") else date.fromisoformat(end)
        rows.append(("task",label.strip(),status,start,end))
    dates=[v for r in rows if r[0]=="task" for v in r[3:]]
    start=min(dates);end=max(dates)+timedelta(days=1)
    width=1200;left=425;right=1170;top=64;rh=23;height=top+len(rows)*rh+40
    x=lambda d:left+(right-left)*(d-start).days/(end-start).days
    z=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK KR" fill="#24364a">']
    def txt(x,y,t,size=15,extra=""):z.append(f'<text x="{x}" y="{y}" font-size="{size}" {extra}>{esc(t)}</text>')
    txt(18,27,title,20,'font-weight="bold"')
    for i in range(0,(end-start).days,4):
        d=start+timedelta(days=i);xx=x(d);z.append(f'<line x1="{xx}" y1="45" x2="{xx}" y2="{height-30}" stroke="#D9E2ED"/>');txt(xx,42,d.strftime("%m/%d"),12,'text-anchor="middle"')
    for i,r in enumerate(rows):
        y=top+i*rh
        if r[0]=="section":
            z.append(f'<rect x="12" y="{y-14}" width="1170" height="21" fill="#E5EDF6"/>');txt(18,y+1,r[1],14,'font-weight="bold"');continue
        _,label,status,a,b=r;txt(24,y+1,label,14)
        xa,xb=x(a),x(b)
        if status=="milestone":z.append(f'<path d="M{xa},{y-9} l7,7 l-7,7 l-7,-7 z" fill="#334E70"/>')
        else:z.append(f'<rect x="{xa}" y="{y-10}" width="{max(3,xb-xa)}" height="12" rx="3" fill="{ {"done":"#2B826D","active":"#D28B33","planned":"#6285AD","crit":"#A94B48"}[status]}"/>')
    txt(18,height-12,"녹색: 작성 완료 보고 / 주황: 진행 중 / 청색: 잠정 계획 / ◆: 목표일",13)
    z.append("</g></svg>");dest.write_text("".join(z),encoding="utf-8")
def convert(name,path,landscape):
    md=(ROOT/path).read_text(encoding="utf-8");images=[];diagrams=[]
    def diagram(m):
        code=m.group(1).strip();idx=len(images)+1;dest=PREVIEW/f"{name}-diagram-{idx}.svg"
        kind=code.splitlines()[0].split()[0]
        {"flowchart":render_flow,"gantt":render_gantt,"erDiagram":render_er}[kind](code,dest)
        images.append(dest);diagrams.append(kind)
        return f'\n\n![{ {"flowchart":"업무 흐름도","gantt":"간트 차트","erDiagram":"데이터 관계도 (1 / 0..1 / 0..N)"}[kind]}]({dest.as_uri()})\n\n'
    md=re.sub(r"(?m)^ *\x60\x60\x60mermaid[ \t]*\n([\s\S]*?)^ *\x60\x60\x60[ \t]*$",diagram,md)
    if re.search(r"(?m)^\s*\x60\x60\x60mermaid",md):raise RuntimeError("unrendered Mermaid")
    rendered=subprocess.check_output(["pandoc","--from=gfm","--to=html5","--wrap=none"],input=md,text=True)
    soup=BeautifulSoup(rendered,"html.parser")
    for a in soup.find_all("a",href=True):
        href=a["href"]
        if href.startswith("#") or urlsplit(href).scheme:continue
        parts=href.split("#",1);target=posixpath.normpath(posixpath.join(posixpath.dirname(path),parts[0]))
        if target.startswith("../"):raise ValueError("relative link outside repo")
        from urllib.parse import unquote
        a["href"]=f"https://github.com/ik-e/chaja-you/blob/{COMMIT}/"+quote(unquote(target),safe="/")+("#"+parts[1] if len(parts)>1 else "")
    for table in soup.find_all("table"):
        header=table.find("thead")
        hs=header.find_all("th") if header else []
        if not hs: continue
        cols=len(hs);rows=table.find_all("tr");weights=[]
        for idx,h in enumerate(hs):
            lens=[len(row.find_all(["td","th"])[idx].get_text()) for row in rows if len(row.find_all(["td","th"]))==cols]
            lens.sort();p=lens[min(len(lens)-1,int(len(lens)*0.7))] if lens else 10
            weights.append(max(1.0,min(4.5,(max(len(h.get_text()),p)/12)**0.53)))
        cg=soup.new_tag("colgroup")
        for weight in weights:
            col=soup.new_tag("col");col["style"]=f"width:{100*weight/sum(weights):.3f}%";cg.append(col)
        old=table.find("colgroup")
        if old:old.decompose()
        table.insert(0,cg)
    css=f"""@page {{size:A4 {'landscape' if landscape else 'portrait'};margin:14mm 14mm 16mm;
      @top-left {{content:'찾아you | 최종 프로젝트 1팀';font-family:'Noto Sans CJK KR';font-size:8pt;color:#597086}}
      @top-right {{content:'{COMMIT[:7]} | 2026-11-26';font-family:'Noto Sans CJK KR';font-size:8pt;color:#597086}}
      @bottom-center {{content:counter(page) ' / ' counter(pages);font-family:'Noto Sans CJK KR';font-size:8pt;color:#597086}}
    }}
    html {{font-family:'Noto Sans CJK KR',sans-serif;font-size:10pt;line-height:1.55;color:#24364a;word-break:normal;overflow-wrap:anywhere}}
    h1 {{font-size:21pt;line-height:1.3;margin:0 0 7mm;border-bottom:2px solid #375B7D;padding-bottom:3mm}}
    h2 {{font-size:15pt;color:#2E5679;margin:6mm 0 2.5mm;break-after:avoid}}
    h3 {{font-size:12pt;color:#375B7D;margin:4mm 0 1.6mm;break-after:avoid}}
    h4 {{font-size:10.5pt;break-after:avoid}}
    p {{margin:0 0 3mm;orphans:2;widows:2}}
    blockquote {{margin:3mm 0 4mm;padding:3mm;border-left:2px solid #6C8DAA;background:#EDF3F8;font-size:9pt}}
    table {{width:100%;table-layout:fixed;border-collapse:collapse;margin:2mm 0 4mm;font-size:8.6pt;line-height:1.45}}
    thead {{display:table-header-group}}
    th {{background:#DFE9F3;color:#24364a;font-weight:700;text-align:left}}
    td,th {{border:0.5px solid #C9D5E1;vertical-align:middle;padding:1.6mm 1.8mm;overflow-wrap:anywhere;word-break:break-word}}
    tr {{break-inside:avoid}} tbody tr:nth-child(even) {{background:#F7F9FB}}
    pre {{font-family:'Noto Sans Mono CJK KR',monospace;font-size:8pt;line-height:1.38;white-space:pre-wrap;overflow-wrap:anywhere;background:#F4F7FA;border:0.5px solid #DCE5ED;padding:2mm;break-inside:auto;}}
    code {{font-family:'Noto Sans Mono CJK KR',monospace;font-size:0.92em;overflow-wrap:anywhere}}
    a {{color:#245983;text-decoration:none;overflow-wrap:anywhere}}
    figure {{margin:3mm 0 4mm;break-inside:avoid;text-align:center}}
    img {{max-width:100%;max-height:{150 if landscape else 215}mm;object-fit:contain}}
    figcaption {{font-size:8pt;color:#526C83}}
    li {{margin-bottom:1mm}} hr {{border:0;border-top:1px solid #C9D5E1}}
    """
    page=PREVIEW/(name+".html");page.write_text("<!doctype html><html lang='ko'><head><meta charset='utf-8'><style>"+css+"</style></head><body>"+str(soup)+"</body></html>",encoding="utf-8")
    pdf=OUT/(name+".pdf")
    run(["weasyprint",str(page),str(pdf)])
    info=subprocess.check_output(["pdfinfo",str(pdf)],text=True)
    pages=int(re.search(r"^Pages:\s+(\d+)",info,re.M).group(1))
    extracted=subprocess.check_output(["pdftotext","-layout",str(pdf),"-"],text=True)
    if "\ufffd" in extracted or len(extracted.strip())<1000:raise RuntimeError("text extraction failed "+name)
    bbox=PREVIEW/(name+"-bbox.html")
    run(["pdftotext","-bbox-layout",str(pdf),str(bbox)])
    xml=ET.parse(bbox);errors=[];ns="{http://www.w3.org/1999/xhtml}"
    for pi,p in enumerate(xml.iter(ns+"page"),1):
        w,h=float(p.attrib["width"]),float(p.attrib["height"])
        for word in p.iter(ns+"word"):
            if float(word.attrib["xMin"])<0 or float(word.attrib["yMin"])<0 or float(word.attrib["xMax"])>w+0.5 or float(word.attrib["yMax"])>h+0.5:errors.append((pi,word.text))
    if errors:raise RuntimeError("off-page text "+str(errors[:10]))
    run(["pdftoppm","-r","90","-png",str(pdf),str(PREVIEW/name)])
    renders=sorted(PREVIEW.glob(name+"-*.png"))
    if len(renders)!=pages:raise RuntimeError("render count mismatch")
    thumbs=[]
    for idx,p in enumerate(renders,1):
        im=Image.open(p).convert("RGB")
        im.thumbnail((360,270) if landscape else (270,360))
        tile=Image.new("RGB",(380,390),"#E3E8EE");tile.paste(im,((380-im.width)//2,12))
        ImageDraw.Draw(tile).text((10,365),f"{idx} / {pages}",fill="black")
        thumbs.append(tile)
    for group in range(0,len(thumbs),12):
        subset=thumbs[group:group+12];sheet=Image.new("RGB",(380*4,390*((len(subset)+3)//4)),"white")
        for i,tile in enumerate(subset):sheet.paste(tile,((i%4)*380,(i//4)*390))
        sheet.save(PREVIEW/f"{name}-contact-{group//12+1}.png")
    return {"file":pdf.name,"source":path,"source_sha256":hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),"pdf_sha256":hashlib.sha256(pdf.read_bytes()).hexdigest(),"pages":pages,"diagram_types":diagrams,"rendered_pages":len(renders),"text_offpage_errors":len(errors)}
manifest={"commit":COMMIT,"scope":"four instructor-reviewed submission PDFs; independent render and bounds checks, visual human review separate","files":[convert(*x) for x in ITEMS]}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(manifest,ensure_ascii=False,indent=2))
