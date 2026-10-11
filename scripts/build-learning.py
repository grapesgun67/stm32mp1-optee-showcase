#!/usr/bin/env python3
"""Render reviewed learning notes. Reads public JSON only; no private-source copying."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'docs/learning-notes.json').read_text())
OUT = ROOT / 'learning'
MD = ROOT / 'docs/learning'
OUT.mkdir(exist_ok=True)
MD.mkdir(exist_ok=True)
e = escape

CSS = '''
:root{--ink:#102e32;--muted:#50666a;--green:#176650;--line:#d9ded8;--paper:#f6f4ef}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.85 system-ui,sans-serif;word-break:keep-all;overflow-wrap:anywhere}
main,footer{max-width:1080px;margin:auto;padding:30px 24px}a{color:var(--green);text-underline-offset:4px}nav{display:flex;flex-wrap:wrap;gap:14px;font-size:14px}
h1{font-size:clamp(30px,4.5vw,48px);line-height:1.3;letter-spacing:-.035em;max-width:900px}h2{font-size:25px;line-height:1.5}h3{font-size:19px;line-height:1.6}
.eyebrow{font-size:12px;letter-spacing:.13em;color:var(--green);margin-top:48px}.lead{font-size:19px;max-width:850px;color:var(--muted)}.meta,small{font-size:13px;color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.card{border:1px solid var(--line);border-radius:14px;background:white;padding:24px}.card h2{font-size:22px;margin:8px 0}.card p{margin:8px 0}.card small{display:block}
.route{background:var(--ink);color:white;border-radius:14px;padding:22px;margin:28px 0}.route a{color:#b7ead3}.route p{margin:6px 0}
section{padding:28px 0;border-bottom:1px solid var(--line);scroll-margin-top:16px}.qa{max-width:880px;margin:26px 0}.qa p{margin-top:8px}.flow{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;padding:0;list-style:none}.flow li{padding:16px;background:#e4eee7;border-radius:10px;font-size:14px}.flow b{display:block;color:var(--green);margin-bottom:6px}
.change{background:white;border-left:4px solid var(--green);padding:20px 24px}.back{display:inline-block;padding:5px 12px;border:1px solid var(--line);border-radius:24px;font-size:13px;margin-top:14px}code{font-size:13px;word-break:break-word}details{padding:18px 0}summary{cursor:pointer;font-weight:600}li{margin:6px 0}a:focus-visible,summary:focus-visible{outline:3px solid #d9a13b;outline-offset:4px}.next{justify-content:space-between;margin-top:28px}footer{font-size:13px;color:var(--muted)}
@media(max-width:680px){.cards,.flow{grid-template-columns:1fr}main,footer{padding:22px 18px}.eyebrow{margin-top:30px}}
@media print{nav,.back,.next{display:none}body{background:white}.cards,.flow{grid-template-columns:1fr}section{break-inside:auto}.qa{break-inside:avoid}h1{font-size:28px}}
'''

def shell(title, content, prefix=''):
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="OP-TEE 구현 과정의 질문, 이해의 변화, 관련 코드와 근거를 연결한 기술 학습 기록">
<title>{e(title)} — DEVICE TRUST LAB</title><style>{CSS}</style></head><body>
<main><nav aria-label="페이지 탐색"><a href="{prefix}index.html">실증 포트폴리오</a><a href="{prefix}fundamentals.html">구현 설명</a><a href="{prefix}learning.html">기술 학습 기록</a></nav>
{content}</main><footer>질의응답과 개발 기록을 바탕으로 정리하고 AI 검토를 활용했습니다. 개인별 코드 기여나 과거 설계 의도를 추정하지 않습니다.</footer></body></html>\n'''

def links_html(items, prefix):
    return '<ul>' + ''.join(f'<li><a href="{e(url if url.startswith("https://") else prefix + url, quote=True)}">{e(label)}</a></li>' for label, url in items) + '</ul>'

articles = DATA['articles']
ids = [a['id'] for a in articles]
assert len(ids) == len(set(ids))
for i, a in enumerate(articles):
    toc = [('question', '질문의 출발점'), ('understanding', '정리한 이해'), ('code', '코드와 연결')]
    content = [f'<p class="eyebrow">LEARNING NOTES / {i + 1:02d} · {e(a["category"])}</p><h1>{e(a["title"])}</h1>',
               f'<p class="meta">정리일 <time datetime="{DATA["organized_on"]}">{DATA["organized_on"]}</time> · 소스 대조 {e(DATA["source_commit"])}</p>',
               '<nav id="toc" aria-label="본문 목차">' + ''.join(f'<a href="#{key}">{title}</a>' for key, title in toc) + '</nav>',
               f'<section id="question"><h2>질문의 출발점</h2><p class="lead">{e(a["question"])}</p><div class="change"><strong>이해가 바뀐 지점</strong><p>{e(a["change"])}</p></div><a class="back" href="#toc">↑ 목차로</a></section>',
               '<section id="understanding"><h2>정리한 이해</h2><ol class="flow" aria-label="개념 흐름">' + ''.join(f'<li><b>{j+1:02d}</b>{e(s)}</li>' for j,s in enumerate(a['flow'])) + '</ol>']
    for q, answer in a['qa']:
        content.append(f'<div class="qa"><h3>{e(q)}</h3><p>{e(answer)}</p></div>')
    content.append('<a class="back" href="#toc">↑ 목차로</a></section>')
    content.append('<section id="code"><h2>코드와 연결</h2><p>개발 저장소의 portfolio-hello 기준 함수·파일입니다. 공개된 기존 발췌는 별도의 과거 스냅샷이며 함수명이 다를 수 있습니다.</p><ul>' + ''.join(f'<li><code>{e(c)}</code></li>' for c in a['code']) + '</ul>')
    content.append(links_html(a['links'], '../'))
    content.append('<details><summary>근거와 확인 범위</summary><p>' + e(a['evidence']) + '</p>' + links_html(a['sources'], '../') + '</details>')
    content.append('<details><summary>다음에 더 확인할 질문</summary><p>' + e(a['followup']) + '</p></details><a class="back" href="#toc">↑ 목차로</a></section>')
    previous = f'<a href="{articles[i-1]["id"]}.html">← 이전 글</a>' if i else '<a href="../learning.html">전체 목록</a>'
    following = f'<a href="{articles[i+1]["id"]}.html">다음 글 →</a>' if i+1 < len(articles) else '<a href="../learning.html">전체 목록</a>'
    content.append(f'<nav class="next" aria-label="글 순서">{previous}{following}</nav>')
    (OUT / f'{a["id"]}.html').write_text(shell(a['title'], '\n'.join(content), '../'))
    md = [f'# {a["title"]}', f'정리일: {DATA["organized_on"]} · 소스 대조: {DATA["source_commit"]}', '## 질문의 출발점', a['question'], '### 이해가 바뀐 지점', a['change'], '## 정리한 이해', ' → '.join(a['flow'])]
    for q, answer in a['qa']:
        md += [f'### {q}', answer]
    md += ['## 코드와 연결', '개발 저장소 기준. 기존 공개 발췌와 현재 함수명이 다를 수 있다.', '\n'.join('- '+c for c in a['code'])]
    md += [f'- [{label}]({url if url.startswith("https://") else "../../"+url})' for label,url in a['links']]
    md += ['## 근거와 확인 범위', a['evidence']]
    md += [f'- [{label}]({url})' for label,url in a['sources']]
    md += ['## 다음에 더 확인할 질문', a['followup'], '[전체 학습 목록](../../learning.html)']
    (MD / f'{a["id"]}.md').write_text('\n\n'.join(md)+'\n')

content = ['<p class="eyebrow">LEARNING NOTES / PHASE 1</p><h1>구현하면서 생긴 질문,<br>코드와 연결해 다시 이해하기.</h1><p class="lead">세션과 메모리에서 키 관리, 요청 인가, 하드웨어 격리까지. 질의응답에서 수정한 이해를 관련 구현과 연결했습니다.</p>',
           f'<p class="meta">12개 주제 · 첫 정리 {DATA["organized_on"]} · 과거 대화의 날짜별 원문이 아닌 주제별 편집본</p>',
           '<div class="route"><strong>처음 읽는다면</strong><p><a href="learning/11-trustzone.html">11 하드웨어 격리</a> → <a href="learning/08-authorization.html">08 요청 인가</a> → <a href="learning/09-deletion.html">09 삭제 대상 확인</a></p><p>구현 순서로 복습하려면 아래 01부터 읽으세요.</p></div>',
           '<section id="topics"><h2>주제별 기록</h2><div class="cards">']
for i,a in enumerate(articles):
    content.append(f'<article class="card"><small>{i+1:02d} / {e(a["category"])}</small><h2><a href="learning/{a["id"]}.html">{e(a["title"])}</a></h2><p>{e(a["question"])}</p></article>')
content += ['</div></section>', '<details><summary>작성 방식과 자료 범위</summary><p>'+e(DATA['scope'])+'</p><p>실물 결과는 기존 로그와 사용자 제공 결과로 구분했습니다. 하드웨어 보안 기능의 이론 설명을 보드에서 완료한 시험으로 표시하지 않습니다. 원문 대화, 호스트 경로, 주소, 계정 정보와 키 값은 수록하지 않습니다.</p><p>배포 절차와 네트워크 설정 등 운영 세부 사항은 기존 개발 문서에서 관리하며, 여기서는 보안 설계와 연결되는 질문을 중심으로 읽을 수 있게 편집했습니다.</p></details>']
(ROOT / 'learning.html').write_text(shell('기술 학습 기록', '\n'.join(content)))
index = ['# 기술 학습 기록', DATA['scope'], f'정리일: {DATA["organized_on"]}', '[브라우저로 읽기](../learning.html)']
index += [f'- [{i+1:02d} {a["title"]}](learning/{a["id"]}.md)' for i,a in enumerate(articles)]
index += ['공개 원문: learning-notes.json. 수정 후 python3 scripts/build-learning.py로 HTML과 Markdown을 함께 생성한다.']
(ROOT / 'docs/learning-index.md').write_text('\n\n'.join(index)+'\n')
print(f'Rendered {len(articles)} articles, index, and Markdown companions.')
