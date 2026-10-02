#!/usr/bin/env python3
"""Create a five-page submission PDF from the published P0 result JSON."""
import argparse, json, re
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
from reportlab.lib.pagesizes import A4

ROOT=Path(__file__).resolve().parents[1]
INK=colors.HexColor('#102E32'); GREEN=colors.HexColor('#176650'); MUTED=colors.HexColor('#536A6D'); LINE=colors.HexColor('#D9DED8'); PALE=colors.HexColor('#EEF4F0')
W,H=A4; WIDTH=W-84

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('results',type=Path)
    ap.add_argument('--font',default='/mnt/c/Windows/Fonts/malgun.ttf')
    ap.add_argument('--bold-font',default='/mnt/c/Windows/Fonts/malgunbd.ttf')
    ap.add_argument('--output',type=Path,default=ROOT/'downloads/p0-optee-portfolio.pdf')
    a=ap.parse_args(); data=json.loads(a.results.read_text()); tests={r['id']:r for r in data['tests']}; base=data['baseline']
    if len(tests)!=21 or not all(r['verdict']=='PASS' for r in tests.values()):
        raise ValueError('This edition requires the reviewed 21-PASS dataset; revise the narrative for other results.')
    pdfmetrics.registerFont(TTFont('KR',a.font)); pdfmetrics.registerFont(TTFont('KR-Bold',a.bold_font))
    pdfmetrics.registerFontFamily('KR',normal='KR',bold='KR-Bold')
    styles={
      'body':ParagraphStyle('body',fontName='KR',fontSize=10,leading=16,textColor=INK,spaceAfter=10,wordWrap='CJK'),
      'small':ParagraphStyle('small',fontName='KR',fontSize=8.5,leading=13,textColor=MUTED,spaceAfter=7,wordWrap='CJK'),
      'title':ParagraphStyle('title',fontName='KR-Bold',fontSize=29,leading=40,textColor=INK,spaceAfter=18,wordWrap='CJK'),
      'h2':ParagraphStyle('h2',fontName='KR-Bold',fontSize=18,leading=27,textColor=INK,spaceAfter=15,wordWrap='CJK'),
      'h3':ParagraphStyle('h3',fontName='KR-Bold',fontSize=11,leading=18,textColor=GREEN,spaceBefore=10,spaceAfter=8,wordWrap='CJK'),
      'mono':ParagraphStyle('mono',fontName='Courier',fontSize=8,leading=12,textColor=INK,spaceAfter=6),
      'cell':ParagraphStyle('cell',fontName='KR',fontSize=9,leading=14,textColor=INK,wordWrap='CJK'),
    }
    story=[]
    def p(t,style='body'): return Paragraph(t,styles[style])
    def add(t,style='body'): story.append(p(t,style))
    def heading(n,title):
        add('P0 / '+n,'small'); add(title,'h2')
    def table(rows,widths):
        t=Table([[p(escape(str(c)),'cell') for c in row] for row in rows],colWidths=widths,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,LINE),('LINEBELOW',(0,1),(-1,-1),.35,LINE),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
        story.extend([t,Spacer(1,12)])
    def log(lines):
        t=Table([[p(escape(line),'mono')] for line in lines],colWidths=[WIDTH])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('LEFTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,0),10),('BOTTOMPADDING',(0,-1),(-1,-1),8)])); story.extend([t,Spacer(1,10)])
    def actual(id,pattern): return [line for line in tests[id]['output'].splitlines() if re.search(pattern,line)]
    class Diagram(Flowable):
        def __init__(self): Flowable.__init__(self); self.width=WIDTH; self.height=102
        def draw(self):
            c=self.canv; gap=14; bw=(WIDTH-gap*2)/3
            labels=[('노트북 승인 도구','원문·대상 확인','승인키로 요청 서명'),('Linux CA','요청 전달·세션 유지','데이터 서명 검증'),('OP-TEE TA','승인 검증·요청 소비','영속 키로 서명')]
            for i,(title,l1,l2) in enumerate(labels):
                x=i*(bw+gap); c.setFillColor(INK if i==2 else PALE); c.roundRect(x,4,bw,94,8,stroke=0,fill=1)
                c.setFillColor(colors.white if i==2 else INK); c.setFont('KR-Bold',11); c.drawString(x+12,76,title); c.setFont('KR',9); c.drawString(x+12,51,l1); c.drawString(x+12,33,l2)
                if i<2:
                    c.setStrokeColor(GREEN); c.line(x+bw+2,51,x+bw+gap-2,51)
                    c.line(x+bw+gap-5,54,x+bw+gap-2,51); c.line(x+bw+gap-5,48,x+bw+gap-2,51)
    add('EMBEDDED SECURITY  /  REAL HARDWARE','small')
    add('승인된 요청만 서명하는<br/>OP-TEE 서비스','title')
    add('STM32MP157F-DK2 · OpenSTLinux / Yocto · CA/TA 실증','h3')
    add('개인키를 반환하지 않는 것만으로는 무단 서명 요청을 막을 수 없다. 외부 승인자가 허가한 요청을 TA가 직접 검증하고, 세션에 연결된 데이터에만 서명하도록 구현했다.')
    table([['실증 결과','확인 범위'],['21개 실행·확인 항목 PASS','기초 기능 · 승인 정상/거부 · 재부팅 키 유지'],['실물 보드 / SSH 수집','2026-10-02 · portfolio-hello 1.0-r0.10']],[165,WIDTH-165])
    add('두 키의 역할과 실행 경계','h3'); story.append(Diagram()); story.append(Spacer(1,14))
    add('노트북 승인키는 요청 허가를 증명하고, TA 데이터 키는 허가된 데이터에 서명한다. 두 키를 분리했으며 개인키 반환 명령은 제공하지 않는다.')
    add('직접 구현·통합한 범위','h3')
    add('CA/TA 명령 계약과 세션 상태, 스트리밍 해시, 영속 서명 키, 132바이트 승인 요청 직렬화, 승인 검증·요청 소비, 노트북 승인 도구, Yocto 패키징 및 실물 시험.')
    add('OP-TEE 암호/저장 API, OpenSSL, ST BSP는 기반 기술로 사용했다. 본 자료는 실제 SSH 출력과 호스트 비교 결과를 요약하며, 화면 캡처를 합성한 자료가 아니다. 21 PASS는 상세 로드맵 전체 완료나 보안 인증을 의미하지 않는다.','small')
    story.append(PageBreak())

    heading('01 / FOUNDATION','세션·버퍼·해시를 실물 보드에서 확인')
    add('최신 설치 패키지 하나로 기능을 회귀 시험했다. 과거 커밋으로 돌아가 기능별 시연을 구성하지 않았다. 보드와 로컬 deb의 CA/TA 해시도 일치했다.')
    table([['시험','실제 확인 결과'],['PING 4회 → 새 실행 1회','같은 세션 1→4 누적, 새 실행은 다시 1'],['ECHO 일반 / 빈 입력 / 16바이트','입력과 반환 길이·내용 일치'],['잘못된 명령 / PING 타입','TA의 예상 오류를 확인하여 시험 PASS'],['SHA-256 분할 1 / 2 / 4바이트','모든 다이제스트가 sha256sum 기준값과 동일']],[185,WIDTH-185])
    add('실행 로그 발췌 — 카운터','h3')
    log(actual('PING-4',r'TA :|PASS:')+actual('PING-NEW',r'TA :|PASS:'))
    add('실행 로그 발췌 — SHA-256','h3')
    digest=re.search(r'([a-f0-9]{64})',tests['HASH-REF']['output'])[1]
    log(['$ portfolio-hello --hash test 1','$ portfolio-hello --hash test 2','$ portfolio-hello --hash test 4','sha256sum / TA outputs: same 32-byte digest',digest[:32],digest[32:]])
    add('위 명령의 각 실행은 exit=0이며 같은 결과를 반환했다. 다이제스트는 지면상 두 줄로 나눴다. 원본 로그에는 전체 64자리 값이 있다.','small')
    add('검증 범위','h3')
    add('새 실행 카운터 초기화는 확인했다. 최초 COUNT=0 직접 호출, 동시 세션 분리, 내장 NUL·작은 출력 버퍼 재시도 및 HASH 오류 순서 시험은 이번 범위에서 제외했다.','small')
    story.append(PageBreak())

    heading('02 / AUTHORIZATION','정상 승인 성공과 잘못된 승인 거부')
    add('TA가 보관한 메시지 해시와 챌린지를 기준으로 요청을 재구성한다. 노트북은 요청 전체에 서명하고, TA는 고정한 승인 공개키로 검증한 뒤 데이터 키를 사용한다.')
    table([['입력 조건','TA 결과 / CA 종료','판정'],['정상 승인','0x00000000 / exit 0','PASS'],['승인 서명 1바이트 변조','0xffff3072 / exit 1','PASS'],['다른 승인키로 서명','0xffff3072 / exit 1','PASS'],['새 요청에 과거 승인 재사용','0xffff3072 / exit 1','PASS']],[205,WIDTH-265,60])
    add('실행 로그 발췌 — 정상 승인','h3')
    log(actual('AUTH-NORMAL',r'^SIGN_AUTHORIZED:|^PASS: original|^PASS: altered|^process exit='))
    add('실행 로그 발췌 — 변조 승인','h3')
    log(actual('AUTH-TAMPER',r'^SIGN_AUTHORIZED:|^process exit='))
    add('origin=0x00000004는 TA에서 반환된 결과다. 파일 전송이나 길이 검사에서 실패한 것을 승인 거부 성공으로 세지 않았다. 거부 시험에서 nonzero 종료는 기대 동작이므로 시험 판정은 PASS다.','small')
    add('시험 방법과 구분','h3')
    add('정상/변조용 원본 서명은 사용자가 기존 도구에서 APPROVE와 키 암호를 입력했다. 다른 키 시험은 별도 메모리 내 시험키를 사용했고 기존 키를 교체하지 않았다. 재사용 시험은 성공했던 서명을 새 챌린지 요청에 제출했다.','small')
    add('같은 세션에서 두 번 제출한 시험, 준비 없는 호출 및 직접 명령 우회 시험은 미실행이다. 정상 데이터 변조 거부와 승인 서명 변조 거부는 서로 다른 시험이다.','small')
    story.append(PageBreak())

    heading('03 / PERSISTENCE','재부팅 후에도 같은 키가 유지되는가?')
    add('재부팅 전 공개키를 호스트에 보존한 뒤 보드를 재부팅했다. 약 51.5초 후 새 Linux boot ID로 재접속하여 공개키 n/e와 설치 파일을 다시 확인했다.')
    table([['관측 항목','결과'],['Linux boot ID','재부팅 전후 다름: 실제 새 부팅 확인'],['공개키 modulus / exponent','호스트에서 전후 값을 직접 비교하여 동일'],['CA/TA 파일 SHA-256','재부팅 전후 및 로컬 deb와 동일'],['패키지 / 서비스','1.0-r0.10 유지 / tee-supplicant active']],[185,WIDTH-185])
    add('동일 공개키 지문 — SHA256(n[256] || e[3])','h3')
    fp=tests['KEY-AFTER']['key_fingerprint']
    log(['BEFORE = AFTER',fp[:32],fp[32:],'Compared public n/e against pre-reboot capture: MATCH'])
    add('지문은 두 줄로 표시했다. 단순 출력 유무가 아니라 실제 n/e 바이트를 비교했다. 재부팅 판정은 SSH 재접속과 boot ID 비교에 근거하며 UART 부팅 영상은 아니다.','small')
    add('저장 위치와 보안 한계','h3')
    add('기존 레시피 및 마운트 확인에서 REE FS 저장 위치는 /var/lib/tee이며 루트 ext4 파일시스템에 속한다. TA는 영속 객체 API로 키를 저장하고 핸들만 세션에서 관리한다.')
    add('<b>키 유지 성공 ≠ 롤백 방지 입증.</b> 이전 로그의 REE FS 단조 카운터 경고는 미해결로 남겼다. HUK·보안 부팅·저장소 롤백 방지 수준은 이번 시험으로 판단하지 않는다.')
    add('재부팅 후 과거 공개키 파일을 입력한 독립 서명 검증은 아직 하지 않았다. 이번 키 시험은 공개키 동일성과 파일/서비스 유지 확인까지다.','small')
    story.append(PageBreak())

    heading('04 / REPRODUCIBILITY','실행 근거와 한계를 함께 제출')
    add('실증 회차: '+escape(base['run_id']),'small')
    add('설치 패키지: '+escape(base['package']),'body')
    add('deb SHA-256','h3'); log([base['package_sha256'][:32],base['package_sha256'][32:]])
    add('조사 시 저장소 HEAD','h3'); log([base['source_commit']])
    add('보드 CA/TA 파일과 로컬 deb의 일치는 확인했다. 위 HEAD가 해당 deb의 과거 빌드 입력이었다는 증명은 확보하지 않았으므로 빌드 커밋으로 단정하지 않는다. 이번 실증 중 빌드·패키지 재설치·전체 이미지 재기록은 수행하지 않았다.','small')
    add('제출 자료 연결','h3')
    repo='https://github.com/grapesgun67/stm32mp1-optee-showcase'
    add(f'<link href="{repo}" color="#176650">GitHub: grapesgun67/stm32mp1-optee-showcase</link>','body')
    add('저장소 내 증거: evidence/'+escape(base['run_id'])+'/report.md<br/>사례 문서: docs/case-study.md<br/>웹페이지: index.html','small')
    add('GitHub Pages 사이트 주소','h3')
    add('https://grapesgun67.github.io/stm32mp1-optee-showcase/','small')
    add('공개 저장소에는 실증 문서·로그·PDF를 제공한다. CA/TA 소스와 개발 이력은 별도 비공개로 관리한다. 공개 URL을 제출하기 전 Pages 배포 성공과 실제 접근을 확인한다.','small')
    add('미검증 항목과 다음 단계','h3')
    add('동일 세션 재전송·직접 명령 우회, 상세 버퍼/상태 오류, 이전 공개키 독립 검증, 키 교체·회수 및 강한 롤백 방지는 후속 검증 항목이다. 실제 차량 적용, AUTOSAR/Uptane 준수 또는 제품 수준 보안 인증을 주장하지 않는다.','small')
    add('다음 확장은 A7↔M4 및 외부 MCU 통신, 메시지 인증, OTA 설치·복구다. 현재 입증한 키 관리와 요청 승인 범위를 출발점으로 삼는다.','small')
    def page(canvas,doc):
        canvas.setTitle('STM32MP157F-DK2 OP-TEE 실증 포트폴리오')
        canvas.setAuthor('grapesgun67')
        canvas.setFillColor(GREEN); canvas.rect(42,H-36,32,3,stroke=0,fill=1)
        canvas.setFont('KR',8); canvas.setFillColor(MUTED); canvas.drawString(82,H-36,'DEVICE TRUST LAB / P0')
        canvas.setStrokeColor(LINE); canvas.line(42,40,W-42,40)
        canvas.setFont('KR',8); canvas.drawString(42,26,'실증일 2026-10-02  ·  실제 SSH 로그와 호스트 비교 결과')
        canvas.drawRightString(W-42,26,str(doc.page)+' / 5')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    SimpleDocTemplate(str(a.output),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=61,bottomMargin=55).build(story,onFirstPage=page,onLaterPages=page)
    print(a.output)

if __name__=='__main__': main()
