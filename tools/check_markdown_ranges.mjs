// Check unescaped tildes in Markdown prose. Not a full GFM parser.
import {readFileSync,writeFileSync,readdirSync,lstatSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
export function scanMarkdown(text) {
  const findings=[];let fence=null,comment=false,offset=0;
  for(const line of text.split("\n")){
    const raw=line.replace(/\r$/,""),f=raw.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);
    if(fence){if(f&&f[1][0]===fence.char&&f[1].length>=fence.length&&!f[2].trim())fence=null;offset+=line.length+1;continue;}
    if(!comment&&f){fence={char:f[1][0],length:f[1].length};offset+=line.length+1;continue;}
    const escaped=i=>{let n=0;while(i>0&&raw[--i]==="\\")n++;return n%2===1;};
    const ref=raw.match(/^ {0,3}\[[^\]]+\]:[ \t]*(<[^>]*>|[^ \t]+)/);
    const refStart=ref?ref[0].length-ref[1].length:-1;
    for(let i=0;i<raw.length;){
      if(comment){const end=raw.indexOf("-->",i);if(end<0)break;comment=false;i=end+3;continue;}
      if(raw.startsWith("<!--",i)){comment=true;i+=4;continue;}
      if(i===refStart){i+=ref[1].length;continue;}
      if(raw[i]==="`"&&!escaped(i)){
        const n=raw.slice(i).match(/^`+/)[0].length;let j=i+n,found=false;
        while(j<raw.length){const at=raw.indexOf("`",j);if(at<0)break;const m=raw.slice(at).match(/^`+/)[0].length;if(m===n){i=at+m;found=true;break;}j=at+m;}
        if(found)continue;i+=n;continue;
      }
      if(raw[i]==="]"&&raw[i+1]==="("&&!escaped(i)){
        let j=i+2,depth=1;for(;j<raw.length;j++){if(escaped(j))continue;if(raw[j]==="(")depth++;if(raw[j]===")"&&--depth===0)break;}
        if(depth===0){i=j+1;continue;}
      }
      if(raw[i]==="<"&&!escaped(i)){const tag=raw.slice(i).match(/^<(?:https?:\/\/[^>]*|mailto:[^>]*|\/?[A-Za-z][^>]*)>/);if(tag){i+=tag[0].length;continue;}}
      const url=raw.slice(i).match(/^https?:\/\/[^\s<>()]+/);if(url){i+=url[0].length;continue;}
      if(raw[i]==="~"&&!escaped(i)){
        const run=raw.slice(i).match(/^~+/)[0];const prev=raw[i-1]||"",next=raw[i+run.length]||"";
        findings.push({offset:offset+i,line:text.slice(0,offset).split("\n").length,column:i+1,length:run.length,fixable:run.length===1&&/[\p{L}\p{N}]/u.test(prev)&&/[\p{L}\p{N}]/u.test(next),sample:raw.trim().slice(0,180)});i+=run.length;continue;
      }
      i++;
    }
    offset+=line.length+1;
  }
  return findings;
}
export function normalizeMarkdownRanges(text){const findings=scanMarkdown(text);let output=text;for(const f of findings.filter(x=>x.fixable).reverse()){output=output.slice(0,f.offset)+"–"+output.slice(f.offset+f.length);}return {output,fixed:findings.filter(x=>x.fixable).length,remaining:scanMarkdown(output)};}
const tests=[
  [
    "12/6~12/22와 20~30분",
    "12/6–12/22와 20–30분",
    0
  ],
  [
    "| T1~T6 | R03~R05 |",
    "| T1–T6 | R03–R05 |",
    0
  ],
  [
    "월~금, 시작~완료",
    "월–금, 시작–완료",
    0
  ],
  [
    "`~/file` 및 `a~b`",
    "`~/file` 및 `a~b`",
    0
  ],
  [
    "[링크](https://a.test/~user/path) 1~2",
    "[링크](https://a.test/~user/path) 1–2",
    0
  ],
  [
    "[1~2](https://a.test/~user/(x))",
    "[1–2](https://a.test/~user/(x))",
    0
  ],
  [
    "https://a.test/~user",
    "https://a.test/~user",
    0
  ],
  [
    "<https://a.test/~user>",
    "<https://a.test/~user>",
    0
  ],
  [
    "[ref]: https://a.test/~user",
    "[ref]: https://a.test/~user",
    0
  ],
  [
    "\\~ 기호",
    "\\~ 기호",
    0
  ],
  [
    "~~의도된 취소선~~",
    "~~의도된 취소선~~",
    2
  ],
  [
    "1 ~ 2, ~5",
    "1 ~ 2, ~5",
    2
  ],
  [
    "```sh\ncd ~/path\n```\n1~2",
    "```sh\ncd ~/path\n```\n1–2",
    0
  ],
  [
    "~~~mermaid\nA~B\n~~~\n1~2",
    "~~~mermaid\nA~B\n~~~\n1–2",
    0
  ],
  [
    "<!-- 1~2\nstill ~ --> 3~4",
    "<!-- 1~2\nstill ~ --> 3–4",
    0
  ],
  [
    "1~2\r\n3~4\r\n",
    "1–2\r\n3–4\r\n",
    0
  ]
];
function selfTest(){let fails=0;for(const [input,expected,left] of tests){const x=normalizeMarkdownRanges(input);if(x.output!==expected||x.remaining.length!==left||normalizeMarkdownRanges(x.output).output!==x.output){console.error('FAIL',JSON.stringify(input));fails++;}}console.log((tests.length-fails)+'/'+tests.length+' self-tests passed');return fails?1:0;}
function collect(path,files){const stat=lstatSync(path);if(stat.isSymbolicLink())return;if(stat.isDirectory()){for(const entry of readdirSync(path).sort()){if(entry==='.git'||entry==='node_modules'||entry==='.venv')continue;collect(join(path,entry),files);}}else if(stat.isFile()&&/\\.md$/i.test(path))files.add(path);}
function main(args){if(args.length===1&&args[0]==='--self-test')return selfTest();const fix=args.includes('--fix'),paths=args.filter(a=>a!=='--fix');if(!paths.length||paths.some(a=>a.startsWith('--'))){console.error('Usage: node tools/check_markdown_ranges.mjs [--fix] <file-or-directory> ... | --self-test');return 2;}const files=new Set();for(const p of paths)collect(resolve(p),files);if(!files.size){console.error('No Markdown files found');return 2;}let issues=0,changed=0,fixed=0;for(const path of files){const original=readFileSync(path,'utf8');let findings=scanMarkdown(original);if(fix){const result=normalizeMarkdownRanges(original);if(result.fixed){writeFileSync(path,result.output,'utf8');changed++;fixed+=result.fixed;}findings=result.remaining;}for(const f of findings)console.error(path+':'+f.line+':'+f.column+': unescaped tilde ('+(f.fixable?'range; use en dash':'review manually; escape literal or keep intentional syntax')+')');issues+=findings.length;}console.log(JSON.stringify({files:files.size,issues,changed,fixed}));return issues?1:0;}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)process.exitCode=main(process.argv.slice(2));
