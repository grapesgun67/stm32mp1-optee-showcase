"""Single-source architecture figures: SVG for the web, vector drawing for PDF."""
from html import escape
from pathlib import Path
import math
INK='#102e32'; GREEN='#176650'; PALE='#e7f2ec'; GRAY='#536a6d'; LINE='#ccd9d2'; AMBER='#9a4b18'; GOLD='#fff0da'; WHITE='#ffffff'
class Scene:
    def __init__(self,title,desc,w=1040,h=570): self.title=title;self.desc=desc;self.w=w;self.h=h;self.items=[]
    def box(self,x,y,w,h,fill=WHITE,stroke=LINE): self.items.append(('box',x,y,w,h,fill,stroke))
    def text(self,x,y,s,size=19,color=INK,bold=False): self.items.append(('text',x,y,s,size,color,bold))
    def arrow(self,x1,y1,x2,y2,color=GREEN,dashed=False): self.items.append(('arrow',x1,y1,x2,y2,color,dashed))
    def node(self,x,y,w,h,title,lines,secure=False):
        self.box(x,y,w,h,INK if secure else WHITE)
        self.text(x+18,y+31,title,21,WHITE if secure else INK,True)
        for i,line in enumerate(lines):self.text(x+18,y+60+25*i,line,17,'#dceae5' if secure else GRAY)
    def svg(self):
        out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="title desc"><title id="title">{escape(self.title)}</title><desc id="desc">{escape(self.desc)}</desc><rect width="100%" height="100%" fill="#f6f4ef"/>']
        for item in self.items:
            if item[0]=='box':
                _,x,y,w,h,fill,stroke=item;out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}"/>')
            elif item[0]=='text':
                _,x,y,t,z,c,b=item;out.append(f'<text x="{x}" y="{y}" font-family="system-ui,Malgun Gothic,sans-serif" font-size="{z}" fill="{c}" font-weight="{700 if b else 400}">{escape(t)}</text>')
            else:
                _,x,y,x2,y2,c,d=item;a=math.atan2(y2-y,x2-x)
                pts=[(x2,y2),(x2-10*math.cos(a-.45),y2-10*math.sin(a-.45)),(x2-10*math.cos(a+.45),y2-10*math.sin(a+.45))]
                dash=' stroke-dasharray="7 5"' if d else ''
                out.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="2"{dash}/><polygon points="'+ ' '.join(f'{a},{b}' for a,b in pts)+f'" fill="{c}"/>')
        return ''.join(out)+'</svg>'
    def draw(self,c,width):
        from reportlab.lib.colors import HexColor
        scale=width/self.w;c.saveState();c.scale(scale,scale)
        c.setFillColor(HexColor('#f6f4ef'));c.rect(0,0,self.w,self.h,stroke=0,fill=1)
        for item in self.items:
            if item[0]=='box':
                _,x,y,w,h,fill,stroke=item;c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke));c.roundRect(x,self.h-y-h,w,h,12,stroke=1,fill=1)
            elif item[0]=='text':
                _,x,y,t,z,color,bold=item;c.setFillColor(HexColor(color));c.setFont('KR-Bold' if bold else 'KR',z);c.drawString(x,self.h-y,t)
            else:
                _,x,y,x2,y2,color,d=item;c.setStrokeColor(HexColor(color));c.setFillColor(HexColor(color));c.setLineWidth(2);c.setDash([7,5] if d else []);c.line(x,self.h-y,x2,self.h-y2);c.setDash([])
                a=math.atan2(y2-y,x2-x);p=c.beginPath();p.moveTo(x2,self.h-y2)
                for theta in [a-.45,a+.45]:p.lineTo(x2-10*math.cos(theta),self.h-(y2-10*math.sin(theta)))
                p.close();c.drawPath(p,fill=1,stroke=0)
        c.restoreState()

def figures():
    s=Scene('전체 시스템과 신뢰 경계','노트북 승인 도구, 보드 Linux CA와 libteec·TEE 드라이버, OP-TEE TA, tee-supplicant와 REE FS의 역할.',h=650)
    s.box(15,18,270,610,PALE);s.text(35,51,'노트북 / 승인자',22,bold=True)
    s.box(310,18,715,610,'#eef0eb');s.text(332,51,'STM32MP157F-DK2 / 실물 보드',22,bold=True)
    s.box(327,75,320,535,WHITE);s.text(345,105,'Normal World · Linux',20,bold=True)
    s.box(710,75,298,535,PALE);s.text(728,105,'Secure World · OP-TEE',20,bold=True)
    s.node(34,155,232,145,'승인 도구',['원문·대상 키 확인','사람의 APPROVE','요청 전체에 서명'])
    s.node(34,354,232,115,'승인 개인키',['암호화 PEM','노트북에만 보관'])
    s.arrow(150,354,150,303)
    s.node(345,155,282,116,'CA · portfolio-hello',['요청 파일 생성 / 전달','TA 데이터 서명 검증'])
    s.arrow(270,180,342,180);s.text(281,165,'승인',14)
    s.arrow(342,235,270,235);s.text(281,258,'요청',14)
    s.node(345,306,282,76,'libteec → TEE 드라이버',[])
    s.arrow(480,274,480,302)
    s.node(729,155,260,154,'TA · 승인 정책',['승인 공개키 고정','해시·챌린지: 세션 RAM','데이터 개인키 사용'],True)
    s.node(729,348,260,83,'OP-TEE OS',['TA 실행 · 저장소 보호'],True)
    s.arrow(630,343,725,390);s.text(650,338,'호출',16)
    s.arrow(850,345,850,314)
    s.node(345,442,282,68,'tee-supplicant',[])
    s.node(345,544,282,48,'/var/lib/tee · ext4',[])
    s.arrow(729,414,632,474,AMBER,True);s.text(650,456,'저장 RPC',14,AMBER)
    s.arrow(480,512,480,540,AMBER)
    s.text(744,487,'REE에는 보호된 객체 저장',16)
    s.text(744,521,'개인키 반환 API 없음',17,GREEN,True)
    s.text(744,551,'저장소 보호: OP-TEE 담당',16,GRAY)
    s.text(35,546,'실선: 요청/호출',16);s.text(35,579,'점선: 저장소 지원 경로',16)

    q=Scene('승인부터 데이터 서명까지','CA가 TA와 같은 세션을 유지하며 요청을 노트북에서 승인받고, TA는 자기 상태로 요청을 재구성하여 검증한다.',h=650)
    for x,title,sub in [(25,'노트북 승인 도구','승인 개인키'),(385,'Linux CA','같은 세션 유지'),(745,'OP-TEE TA','데이터 개인키')]:q.node(x,18,270,85,title,[sub])
    for x in [160,520,880]:q.arrow(x,114,x,609,LINE,True)
    steps=[(520,880,155,'1  PREPARE: 원문 SHA-256 전달'),(880,520,220,'2  새 챌린지 반환 · TA는 해시 보관'),(520,160,285,'3  CA가 요청 132B 직렬화 → 파일 전달'),(160,520,350,'4  APPROVE → 승인 서명 256B 반환'),(520,880,415,'5  SIGN_AUTHORIZED: 승인 서명 제출'),(880,520,545,'7  데이터 서명 반환 → CA에서 검증')]
    for x1,x2,y,label in steps:
        q.box(min(x1,x2)+5,y-34,350,29,'#f6f4ef','#f6f4ef');q.text(min(x1,x2)+10,y-12,label,17);q.arrow(x1,y,x2,y)
    q.box(610,445,405,61,INK,INK);q.text(625,470,'6  TA 상태로 재구성 → 승인 검증',18,WHITE,True);q.text(625,495,'요청 소비 · 유효한 경우만 데이터 서명',16,WHITE)
    q.text(45,624,'실패: TA 오류 반환, CA 정상 서명 PASS 없음. 정상/변조/다른 키/새 요청 재사용은 실물 시험 완료.',16,GRAY)

    p=Scene('승인 서명이 묶는 132바이트','도메인, TA UUID, 승인 동작, 대상 키 지문, 새 챌린지, 원문 해시 전체를 서명한다.',h=350)
    p.text(24,38,'request.bin = 132 bytes',25,bold=True)
    fields=[('도메인','16 B','0..15'),('TA UUID','16 B','16..31'),('승인 동작','4 B','32..35'),('대상 키 지문','32 B','36..67'),('챌린지','32 B','68..99'),('원문 해시','32 B','100..131')]
    for i,(title,size,offset) in enumerate(fields):
        x=24+i*166;p.box(x,62,154,112,PALE if i<3 else INK);c=INK if i<3 else WHITE
        p.text(x+12,93,title,18,c,True);p.text(x+12,125,size,23,c,True);p.text(x+12,153,offset,15,c)
    p.arrow(520,180,520,211)
    p.box(130,218,780,70,WHITE);p.text(153,247,'전체 132B → SHA-256 → 승인키로 RSA 서명 → approval.sig (256B)',18,GREEN,True)
    p.text(153,274,'TA는 공유 파일을 신뢰하지 않고 자체 세션·실제 키로 같은 바이트열을 재구성한다.',16)
    p.text(24,326,'원문은 포함하지 않고 해시로 결합한다. 동작 8은 승인 대상 식별자이며 실제 제출 명령은 11이다.',16,GRAY)

    t=Scene('세션 상태와 영속 키의 수명','미준비에서 대기로 전이하고 처리 시도는 요청을 소비한다. 세션 데이터는 사라지지만 영속 키는 유지된다.',h=425)
    t.text(24,36,'RAM: 세션과 함께 사라지는 승인 상태',22,bold=True)
    for x,title,lines in [(25,'IDLE',['대기 요청 없음']),(372,'PENDING',['해시 + 챌린지 + 키 핸들']),(719,'IDLE',['처리 시도 후 요청 소비'])]:t.node(x,67,292,109,title,lines)
    t.arrow(321,111,366,111);t.text(322,91,'준비',15)
    t.arrow(669,111,714,111);t.text(665,91,'처리',15)
    t.text(30,202,'유효한 형식으로 처리 진입: 검증 실패도 요청 소비.',17,GRAY)
    t.text(30,225,'타입/길이/SHORT_BUFFER 사전 오류: 대기 요청 유지.',17,GRAY)
    t.box(25,238,990,163,PALE);t.text(45,270,'영속 객체: 세션을 닫거나 재부팅해도 같은 데이터 키를 다시 연다',21,GREEN,True)
    t.text(45,306,'세션 종료 → RAM 상태/키 핸들 정리',18);t.text(45,338,'다음 세션 → 같은 TA UUID + Object ID로 기존 키 열기',18)
    t.text(45,375,'실증: 재부팅 전후 공개키 동일. 키 객체와 세션 상태의 수명은 서로 다르다.',17,AMBER)
    g=Scene('PING과 GET_COUNT의 왕복 흐름','같은 세션에서 CA가 PING으로 증가를 요청하고 GET_COUNT로 카운터를 읽는다. OP-TEE는 진입점을 호출하고 진입점이 state를 내부 함수에 넘긴다.',h=520)
    for x,title,sub in [(20,'CA · run_ping','operation / 같은 session'),(370,'OP-TEE → TA 진입점','TA_InvokeCommandEntryPoint'),(720,'TA 내부 함수','같은 session_state 사용')]:
        g.node(x,18,300,86,title,[sub])
    for x in [170,520,870]:g.arrow(x,112,x,461,LINE,True)
    rows=[(170,520,150,'① InvokeCommand(PING)'),(520,870,208,'② handle_ping(state, types)'),(870,170,276,'③ ping_count 증가 후 SUCCESS 반환'),(170,520,338,'④ InvokeCommand(GET_COUNT)'),(520,870,396,'⑤ handle_ping_get_count(state, types, params)'),(870,170,459,'⑥ params[0].value.a에 count → CA operation으로 반환')]
    for x1,x2,y,label in rows:
        g.text(min(x1,x2)+12,y-13,label,16)
        g.arrow(x1,y,x2,y)
    g.text(30,502,'CA는 반환된 operation.params[0].value.a를 읽고 예상 횟수와 비교한다. 다음 반복도 같은 세션이다.',17,GRAY)
    return {'system':s,'sequence':q,'request':p,'lifetime':t,'ping':g}

if __name__=='__main__':
    out=Path(__file__).resolve().parents[1]/'assets/diagrams';out.mkdir(parents=True,exist_ok=True)
    for name,scene in figures().items(): (out/(name+'.svg')).write_text(scene.svg())
    print('5 shared diagrams generated')
