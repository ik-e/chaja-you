"""Local mock-only bootstrap; not product behavior."""
import argparse, copy, hashlib, json, os, pathlib, subprocess, sys, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen, Request
from urllib.parse import urlsplit
import threading
ROOT=pathlib.Path(__file__).resolve().parent
REPO=ROOT.parents[1]
def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
def workspace(): return load("WORKSPACE.json")
def fixtures(): return load("fixtures/shared/replay.json")["platforms"]
def git(*args): return subprocess.check_output(["git","-C",str(REPO),*args])
def require(ok,message):
    if not ok: raise ValueError(message)
def owner(path):
    matches=[p["id"] for p in workspace()["packages"] for x in p["paths"] if path==x.rstrip("/") or x.endswith("/") and path.startswith(x)]
    return matches[0] if len(matches)==1 else None
def pinned(name):
    p=next(p for p in workspace()["pins"] if p["path"].endswith("/"+name))
    raw=git("show",p["commit"]+":"+p["path"])
    require(hashlib.sha1(("blob "+str(len(raw))+"\0").encode()+raw).hexdigest()==p["blob"],"pin mismatch")
    require(git("rev-parse","HEAD:"+p["path"]).decode().strip()==p["blob"],"HEAD contract differs")
    require(git("hash-object","--path="+p["path"],str(REPO/p["path"])).decode().strip()==p["blob"],"working contract differs")
    return json.loads(raw)
def doctor():
    for p in workspace()["pins"]: pinned(pathlib.Path(p["path"]).name)
    for p in workspace()["packages"]:
        for x in p["paths"]:
            require((ROOT/x).exists() and owner(x.rstrip("/"))==p["id"],"owned path invalid "+x)
    image=(ROOT/"fixtures/shared/mock-image.png").read_bytes()
    a=fixtures()["kmong"]["cases"]["I2"]["input"]["source"]["asset_refs"][0]
    require(len(image)==a["bytes"] and hashlib.sha256(image).hexdigest()==a["digest"],"image mismatch")
    require(int.from_bytes(image[16:20],"big")==652 and int.from_bytes(image[20:24],"big")==488,"image dimensions")
    print("doctor passed: source pins, ownership, synthetic image")
def replay(platform,case,value):
    row=fixtures()[platform]["cases"][case]
    require(json.dumps(value,sort_keys=True,ensure_ascii=False)==json.dumps(row["input"],sort_keys=True,ensure_ascii=False),"exact fixture required")
    return copy.deepcopy(row["output"])
def check_package(package):
    p=next(p for p in workspace()["packages"] if p["id"]==package)
    for platform,f in fixtures().items():
        for case in p["replay_cases"]:
            row=f["cases"][case]
            require(replay(platform,case,row["input"])==row["output"],"fixture mismatch")
            try: replay(platform,case,{"environment":"live"})
            except ValueError: pass
            else: raise AssertionError("invalid input accepted")
    print(package+": independent bootstrap replay passed")
def check_changes(package,base):
    prefix="product/lesson-registration/"
    paths=set()
    for args in [("diff","--name-only","--no-renames","-z",base+"...HEAD"),("diff","--name-only","--no-renames","-z","HEAD"),("ls-files","--others","--exclude-standard","-z")]:
        paths.update(x for x in git(*args).decode().split("\0") if x)
    bad=[p for p in paths if not p.startswith(prefix) or owner(p[len(prefix):])!=package]
    require(not bad,"outside package: "+str(sorted(bad)))
def make_server(mode,platform,port):
    require(os.environ.get("LR_ENVIRONMENT","mock")=="mock","mock only")
    f=fixtures()[platform]
    state={}
    import secrets, http.cookies
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def send(self,status,value,html=False,cookie=None):
            raw=value.encode() if html else json.dumps(value,ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type",("text/html" if html else "application/json")+"; charset=utf-8")
            self.send_header("X-LR-Stub",mode)
            self.send_header("Cache-Control","no-store")
            if cookie:self.send_header("Set-Cookie","lr_mock="+cookie+"; Path=/; HttpOnly; SameSite=Strict")
            self.send_header("Content-Length",str(len(raw)))
            self.end_headers();self.wfile.write(raw)
        def handle_request(self):
            try:
                u=urlsplit(self.path);require(not(u.scheme or u.netloc or u.query or u.fragment),"fixed path only")
                n=int(self.headers.get("Content-Length","0"));require(0<=n<=1048576,"body limit")
                raw=self.rfile.read(n)
                if mode=="api":
                    if self.command=="GET" and u.path=="/_dev/fixtures":return self.send(200,f)
                    value=json.loads(raw) if raw else None
                    for row in f["http"]:
                        if row["method"]==self.command and row["path"]==u.path and json.dumps(row["input"],sort_keys=True)==json.dumps(value,sort_keys=True):
                            return self.send(row["status"],row["output"])
                    return self.send(400,{"code":"INVALID_REQUEST","message":"No exact synthetic replay"})
                c=http.cookies.SimpleCookie(self.headers.get("Cookie",""))
                sid=c["lr_mock"].value if "lr_mock" in c else ""
                if sid not in state:sid=secrets.token_hex(16);state[sid]={"auth":False,"saved":False}
                s=state[sid]
                if self.command=="GET" and u.path=="/mock":return self.send(200,'<h1>Synthetic mock</h1><form method="post" action="/mock/auth"><button>Mock sign-in</button></form><form method="post" action="/mock/save"><input name="value" value="synthetic-only"><button>Save</button></form><a href="/mock/receipt">Receipt</a>',True,sid)
                if self.command=="POST" and u.path=="/mock/auth" and not raw:s["auth"]=True;return self.send(200,{"authenticated":True},cookie=sid)
                if self.command=="POST" and u.path=="/mock/save":
                    if not s["auth"]:return self.send(403,{"error":"mock auth required"},cookie=sid)
                    if raw!=b"value=synthetic-only" or s["saved"]:return self.send(409,{"error":"invalid or duplicate mock"},cookie=sid)
                    s["saved"]=True;return self.send(200,{"saved":True},cookie=sid)
                if self.command=="GET" and u.path=="/mock/receipt":return self.send(200,{"saved":s["saved"],"environment":"mock"},cookie=sid)
                return self.send(404,{"error":"unknown mock path"})
            except (ValueError,UnicodeError,http.cookies.CookieError):return self.send(400,{"error":"invalid request"})
        do_GET=do_POST=do_PATCH=handle_request
    return HTTPServer(("127.0.0.1",port),Handler)
def smoke():
    doctor()
    for p in workspace()["packages"]:check_package(p["id"])
    for platform,f in fixtures().items():
        with make_server("api",platform,0) as s:
            th=threading.Thread(target=s.serve_forever,daemon=True);th.start()
            try:
                for row in f["http"]:
                    raw=None if row["input"] is None else json.dumps(row["input"]).encode()
                    req=Request("http://127.0.0.1:"+str(s.server_port)+row["path"],data=raw,method=row["method"],headers={"Content-Type":"application/json"})
                    with urlopen(req,timeout=3) as resp:require(resp.status==row["status"] and json.load(resp)==row["output"],"http replay mismatch")
            finally:s.shutdown();th.join()
    import http.cookiejar
    from urllib.request import build_opener,HTTPCookieProcessor
    with make_server("mock","kmong",0) as s:
        th=threading.Thread(target=s.serve_forever,daemon=True);th.start()
        try:
            u="http://127.0.0.1:"+str(s.server_port)
            a=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
            b=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
            a.open(u+"/mock",timeout=3).close()
            a.open(Request(u+"/mock/auth",data=b"",method="POST"),timeout=3).close()
            a.open(Request(u+"/mock/save",data=b"value=synthetic-only",method="POST"),timeout=3).close()
            require(json.load(a.open(u+"/mock/receipt",timeout=3))["saved"],"mock save missing")
            require(not json.load(b.open(u+"/mock/receipt",timeout=3))["saved"],"mock isolation failure")
        finally:s.shutdown();th.join()
    print("bootstrap smoke passed; not product validation")
def main():
    require(os.environ.get("LR_ENVIRONMENT","mock")=="mock","mock only")
    os.chdir(ROOT)
    a=argparse.ArgumentParser();sub=a.add_subparsers(dest="cmd",required=True)
    sub.add_parser("doctor");sub.add_parser("smoke")
    p=sub.add_parser("test");p.add_argument("package")
    p=sub.add_parser("check-changes");p.add_argument("package");p.add_argument("--base",required=True)
    p=sub.add_parser("serve");p.add_argument("mode",choices=["api","mock"]);p.add_argument("--platform",choices=["kmong","soomgo"],default="kmong");p.add_argument("--port",type=int,default=0)
    x=a.parse_args()
    if x.cmd=="doctor":doctor()
    elif x.cmd=="smoke":smoke()
    elif x.cmd=="check-changes":check_changes(x.package,x.base)
    elif x.cmd=="test":
        ps=[p for p in workspace()["packages"] if x.package in ("all",p["id"])]
        require(bool(ps),"unknown package")
        for p in ps:subprocess.run([sys.executable,"-m","unittest","discover","-s",p["tests"],"-p","test_*.py"],check=True,cwd=ROOT,env={**os.environ,"PYTHONPATH":str(ROOT)+os.pathsep+str(ROOT/"src")})
        if x.package=="all":subprocess.run([sys.executable,"-m","unittest","discover","-s","tests/integration"],check=True,cwd=ROOT)
    else:
        with make_server(x.mode,x.platform,x.port) as s:
            print("http://127.0.0.1:"+str(s.server_port),flush=True);s.serve_forever()
if __name__=="__main__":main()
