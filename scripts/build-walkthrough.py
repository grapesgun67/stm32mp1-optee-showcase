#!/usr/bin/env python3
"""Render the reviewed public narrative; never reads the private repository."""
import json
from html import escape as e
from pathlib import Path
from textwrap import dedent
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'docs/implementation-story.json').read_text())
css='''*{box-sizing:border-box}body{word-break:keep-all;overflow-wrap:break-word;margin:0;background:#f6f4ef;color:#102e32;font:16px/1.85 system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:32px 24px}a{color:#176650}h1{font-size:clamp(28px,4vw,44px);line-height:1.35}h2{font-size:25px}section{padding:28px 0;border-bottom:1px solid #d9ded8}small{color:#536a6d}pre{word-break:normal;overflow-wrap:normal;padding:22px;background:#102e32;color:#eef4f0;overflow:auto;border-radius:12px;font-size:13px;line-height:1.8}.flow{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}.flow span{flex:1;min-width:140px;background:#e4eee7;padding:18px;border-radius:12px}.table{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:12px;border:1px solid #d9ded8;text-align:left}img{width:100%;background:white;border-radius:12px}.back{display:inline-block;padding:5px 12px;border:1px solid #d9ded8;border-radius:20px;font-size:13px}nav{display:flex;gap:18px;flex-wrap:wrap}@media print{pre{white-space:pre-wrap;font-size:9px}section{break-inside:avoid}nav{display:none}}'''
h=[f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(d["title"])}</title><style>{css}</style><main>', '<nav><a href="index.html">실증 포트폴리오</a><a href="fundamentals.html">01–05 기초·키 설명</a><a href="downloads/p0-optee-portfolio.pdf">PDF</a><a href="#s2">핵심 코드</a><a href="#map">기능별 코드 위치</a></nav>',f'<p>IMPLEMENTATION NOTES / 06</p><h1>{e(d["title"])}</h1><p>기능 구현 → 커밋 → AI 검토 → diff 확인 → 선택 반영. 결과에 이르는 코드와 학습 과정을 설명합니다.</p>', '<div class="flow" aria-label="TA 처리 순서"><span>① 입력·상태 검사</span><span>② 요청 재구성</span><span>③ 승인 요청 소비</span><span>④ 승인 검증 → 데이터 서명</span></div>']
m=[f'# {d["title"]}\n','기능 구현 → 커밋 → AI 검토 → diff 확인 → 선택 반영.\n']
h.append('<nav id="toc" aria-label="설명 목차">'+''.join(f'<a href="#s{i}">{e(s["title"])}</a>' for i,s in enumerate(d['sections']) if i not in (0,7))+'</nav>')
for i,s in enumerate(d['sections']):
 if i in (0,7): continue
 h.append(f'<section id="s{i}"><small>{e(s["label"])}</small><h2>{e(s["title"])}</h2><p>{e(s["text"])}</p>')
 m.extend([f'## {s["title"]}\n',s['text']+'\n'])
 if i==1:
  h.append('<img src="assets/diagrams/sequence.svg" alt="CA·ノ트북 승인 도구·TA 사이의 요청 승인 순서">'.replace('ノ','노'))
  m.append('![승인 흐름](../assets/diagrams/sequence.svg)\n')
 if 'code' in s:
  display=s['prototype']+'\n\n/* 본문 일부: 앞뒤 코드는 생략 */\n'+dedent(s['code'])
  h.append(f'<p><small>entry.c {s["lines"]}행 · 함수 원형 + 본문 발췌</small></p><pre><code>{e(display)}</code></pre>')
  m.append(f'entry.c {s["lines"]}행 · 함수 원형 + 본문 발췌\n\n```c\n{display}\n```\n')
 h.append('<a class="back" href="#toc">↑ 목차로</a></section>')
h.append('<section id="map"><h2>다른 기능은 어느 코드를 읽으면 되는가?</h2><p><a href="fundamentals.html">세션·ECHO·해시·키 생성·영속 저장 상세 설명 →</a></p><p>아래 경로는 개발 저장소의 portfolio-hello/files 기준입니다. 전체 소스는 비공개이며, 이번 페이지는 승인 처리 코드 일부만 공개합니다.</p><div class="table"><table><tr><th>기능</th><th>CA</th><th>TA</th></tr>')
m.append('## 기능별 코드 위치\n\n개발 저장소의 portfolio-hello/files 기준. 전체 소스는 비공개이며 승인 처리 일부만 공개한다.\n\n| 기능 | CA | TA |\n|---|---|---|')
for row in d['map']:
 h.append('<tr>'+''.join(f'<td>{e(c)}</td>' for c in row)+'</tr>');m.append('| '+' | '.join(row)+' |')
h.append('</table></div></section>')
scope='초기 구현·커밋 → AI 검토 → diff 확인 → 선택 반영 방식으로 진행했습니다. TA 입력 검사 보완에 AI 도움을 받았습니다. 정상 승인·변조·다른 승인키·새 요청에 과거 승인 재사용은 확인했고, 같은 세션 재제출·직접 명령 우회·모든 파라미터 오류는 미시험입니다.'
h.append('<section><details><summary>개발 방식과 확인 범위</summary><p>'+e(scope)+'</p><p>소스 스냅샷이 설치 패키지의 확정 빌드 입력임을 의미하지 않습니다.</p></details></section>')
m.extend(['\n## 개발 방식과 확인 범위\n',scope+'\n'])
ref=f'발췌 기준: {d["source_commit"]}\n{d["source_path"]}\n파일 SHA-256: {d["source_sha256"]}'
h.append(f'<section><h2>근거와 공개 범위</h2><pre>{e(ref)}</pre><p>2026-10-04 코드 대조. 개인정보·키 값·호스트 경로를 포함하지 않는 함수 일부만 발췌했습니다. 사용자의 구현 회고와 현재 이해, Git으로 확인한 변화, 실물 시험을 구분합니다.</p><p><a href="assets/code/LICENSE">발췌 코드 BSD-2-Clause 라이선스</a> · <a href="report.html">실제 시험 결과</a></p></section></main></html>')
m.extend(['\n## 근거와 공개 범위\n',ref+'\n','[발췌 코드 라이선스](../assets/code/LICENSE) · [실제 시험 결과](../evidence/p0-20261002T115454Z/report.md)\n'])
(R/'implementation.html').write_text('\n'.join(h)+'\n');(R/'docs/implementation-walkthrough.md').write_text('\n'.join(m)+'\n')
