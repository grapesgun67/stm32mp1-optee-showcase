#!/usr/bin/env python3
"""Generate public functional walkthroughs from reviewed excerpts and public evidence."""
import json,re
from textwrap import dedent
from html import escape as e
from pathlib import Path
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'docs/fundamentals-story.json').read_text())
tests={t['id']:t for t in json.loads((R/'evidence/p0-20261002T115454Z/results.json').read_text())['tests']}
css='''*{box-sizing:border-box}body{word-break:keep-all;overflow-wrap:break-word;margin:0;background:#f6f4ef;color:#102e32;font:16px/1.85 system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:32px 24px}a{color:#176650}h1{font-size:clamp(28px,4vw,44px);line-height:1.3}section{padding:36px 0;border-bottom:1px solid #d9ded8}pre{word-break:normal;overflow-wrap:normal;padding:20px;background:#102e32;color:#eef4f0;border-radius:12px;overflow:auto;font-size:13px;line-height:1.8}.flow{display:flex;gap:10px;flex-wrap:wrap}.flow span{flex:1;min-width:150px;padding:15px;background:#e4eee7;border-radius:10px}.note{padding:16px;border-left:4px solid #176650;background:white}img{width:100%;height:auto}.back{display:inline-block;padding:5px 12px;border:1px solid #d9ded8;border-radius:20px;font-size:13px}section{scroll-margin-top:20px}nav{display:flex;gap:16px;flex-wrap:wrap}details{margin:18px 0}summary{cursor:pointer;font-weight:600}small{color:#536a6d}@media print{pre{white-space:pre-wrap;font-size:9px}nav{display:none}}'''
h=[f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>기초 기능에서 영속 키까지 — 코드 설명</title><style>{css}</style><main><nav><a href="index.html">포트폴리오</a><a href="implementation.html">06 승인 검증</a><a href="downloads/p0-optee-portfolio.pdf">PDF</a></nav><h1>기초 기능에서 영속 키까지<br>코드로 따라가는 구현</h1><p>문제 → 호출 흐름 → 실제 CA/TA 코드 → 검사와 자원 정리 → 실물 근거 순서로 읽습니다. 기능의 현재 구현을 설명합니다.</p>']
m=['# 기초 기능에서 영속 키까지 — 코드 설명\n','문제와 호출 흐름, 실제 코드와 실행 결과를 함께 설명한다.\n']
h.append('<nav id="toc" aria-label="기능 목차">'+''.join(f'<a href="#{c["id"]}">{e(c["title"].split(" — ")[0])}</a>' for c in d['chapters'])+'</nav>')
for c in d['chapters']:
 h.append(f'<section id="{c["id"]}"><h2>{e(c["title"])}</h2><p><strong>문제:</strong> {e(c["problem"])}</p><div class="flow">'+''.join(f'<span>{i+1}. {e(v)}</span>' for i,v in enumerate(c['flow']))+'</div>')
 m.extend([f'## {c["title"]}\n',c['problem']+'\n',' → '.join(c['flow'])+'\n'])
 for key in ['explain']:
  h.append(f'<p>{e(c[key])}</p>');m.append(c[key]+'\n')
 if c['id']=='session':
  h.append('<figure><img src="assets/diagrams/ping.svg" alt="CA가 PING과 GET_COUNT를 호출하고 TA 카운터를 읽는 흐름"><figcaption>PING은 증가, GET_COUNT는 조회. 두 명령을 같은 세션에서 반복합니다.</figcaption></figure>')
  m.append('![PING 왕복](../assets/diagrams/ping.svg)\n')
 for s in c['snippets']:
  cap=f'{s["path"]} {s["lines"]}행 · 함수 원형 + 본문 발췌'
  display=s['prototype']+'\n\n/* 본문 일부: 앞뒤 코드는 생략 */\n'+dedent(s['code'])
  h.append(f'<p><small>{e(cap)}</small></p><pre><code>{e(display)}</code></pre>');m.extend([cap+'\n',f'```c\n{display}\n```\n'])
 for key,title in [('detail','코드를 읽는 순서'),('review','검토할 조건'),('evidence','실물 확인 결과')]:
  h.append(f'<h3>{title}</h3><p>{e(c[key])}</p>');m.extend([f'### {title}\n',c[key]+'\n'])
 if c['commands']:
  text='\n'.join(c['commands']);h.append(f'<details><summary>보드에서 실행하는 명령</summary><pre>{e(text)}</pre></details>');m.append(f'보드 실행 명령:\n```sh\n{text}\n```\n')
 else:
  h.append('<p><a href="guide.html">승인 파일 준비와 재부팅을 포함한 시험 절차</a>를 참고하세요. 현재 승인 흐름에서는 단독 --sign 실행만으로 시험이 완료되지 않습니다.</p>' if c['id']=='signing' else '<p>키 생성·삭제나 재부팅은 자동 실행하지 않습니다. <a href="guide.html">기존 시험 절차</a>와 <a href="report.html">재부팅 비교 근거</a>를 함께 읽으세요.</p>')
 for tid in c['test_ids']:
  t=tests[tid];lines=[line for line in t['output'].splitlines() if re.search(r'^PASS:|^TA : ping_cnt|^SHA256:|^SIGN_AUTHORIZED:|^Compared public|^process exit=',line)]
  # Only publish selected diagnostic lines; never dump environment or public key arrays.
  if lines:
   output='\n'.join(lines);h.append(f'<details><summary>{e(tid)} · 실제 로그 발췌</summary><pre>{e(output)}</pre></details>');m.append(f'{tid} 실제 로그 발췌:\n```text\n{output}\n```\n')
 h.append(f'<p><a href="report.html">결과 보고서</a> · 근거 항목: {e(", ".join(c["test_ids"]))}</p><a class="back" href="#toc">↑ 목차로</a></section>')
scope='개발 방식: 초기 구현·커밋 → AI 검토 → diff 확인 → 선택 반영. 타입·버퍼·값 검사 보완에 AI 도움을 받았습니다. 현재 코드의 동작을 설명하며 줄별 작성 기여를 추정하지 않습니다.'
h.append('<section><details><summary>개발 방식과 확인 범위</summary><p>'+e(scope)+'</p><ul>'+''.join('<li>'+e(c['title'].split(' — ')[0]+': '+c['limits'])+'</li>' for c in d['chapters'])+'</ul><p>근거는 기존 실증 기록입니다. 소스 스냅샷과 설치 패키지의 빌드 입력 일치까지 확정한 것은 아닙니다.</p></details></section>')
m.extend(['\n## 개발 방식과 확인 범위\n',scope+'\n']+[c['title'].split(' — ')[0]+': '+c['limits']+'\n' for c in d['chapters']])
h.append(f'<section><h2>다음: 누가 이 요청을 승인했는가?</h2><a href="implementation.html">06 외부 승인 검증 코드 설명 →</a><p>소스 스냅샷: {e(d["source_commit"])}. 개발 저장소의 portfolio-hello/files 기준.</p><p><a href="assets/code/LICENSE">BSD-2-Clause 발췌 코드 라이선스</a></p></section></main></html>')
m.append(f'\n[06 승인 검증](implementation-walkthrough.md) · [실제 결과](../evidence/p0-20261002T115454Z/report.md) · [코드 라이선스](../assets/code/LICENSE)\n\n소스 스냅샷: {d["source_commit"]}. 설치 패키지의 확정 빌드 입력으로 단정하지 않음.\n')
(R/'fundamentals.html').write_text('\n'.join(h)+'\n');(R/'docs/fundamentals-walkthrough.md').write_text('\n'.join(m)+'\n')
