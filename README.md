# OP-TEE 외부 승인 기반 서명 서비스

STM32MP157F-DK2 실물 보드에서 CA/TA 통신, 영속 서명 키, 외부 승인 검증을 구현하고 시험한 공개 포트폴리오입니다.

- **[제출용 PDF · 5쪽](downloads/p0-optee-portfolio.pdf)**
- **[실증 사례](docs/case-study.md)**
- **[전체 시험 결과와 로그](evidence/p0-20261002T115454Z/report.md)**
- [시험 절차 기록](docs/test-procedure.md)

GitHub Pages 설정과 배포가 완료되면 다음 주소로 볼 수 있습니다.

`https://grapesgun67.github.io/stm32mp1-optee-showcase/`

## 확인한 결과

2026-10-02, portfolio-hello 1.0-r0.10 기준 21개 실행·확인 항목이 기대 조건을 충족했습니다.

| 범위 | 결과 |
|---|---|
| CA/TA 기초 | PING 카운터, ECHO, SHA-256 분할 결과, 예상 명령/타입 오류 |
| 승인 정책 | 정상 승인 성공, 서명 변조·다른 승인키·새 요청에 과거 승인 재사용 거부 |
| 재부팅 | 새 boot ID, 동일 공개키 n/e, CA/TA 파일 해시와 서비스 유지 |

21 PASS는 상세 로드맵 전체 완료율이나 보안 인증을 의미하지 않습니다. 같은 세션 재전송/직접 명령 우회, 이전 공개키 파일을 입력한 독립 검증, HUK·보안 부팅·저장소 롤백 방지는 이번 범위에서 미검증입니다.

웹페이지의 패널은 실제 SSH 실행 로그의 공개용 발췌이며 데스크톱 스크린샷을 가장하지 않습니다. 공개 사본에서 호스트 식별값과 긴 공개키를 생략했습니다.

## 저장소 범위

이 저장소는 **전시용 자료만** 관리합니다. CA/TA 구현 소스·Yocto 레시피·개발 이력은 별도 private 저장소에 있습니다. 이 저장소를 clone하면 전시 페이지를 볼 수 있지만 Yocto를 빌드할 수 있는 것은 아닙니다.

보고서의 source HEAD는 시험 조사 당시 개발 저장소의 식별값입니다. 설치 파일과 deb 해시는 대조했지만 그 HEAD가 과거 deb의 빌드 입력이었다고 확정하지 않습니다.

## 로컬 열기

index.html을 브라우저에서 직접 열거나 이 전시 저장소에서 실행합니다.

```bash
python3 -m http.server 8766 --bind 127.0.0.1
```

브라우저: http://localhost:8766

## Pages 최초 설정

1. 사용자가 최초 커밋을 만든 뒤 origin/main으로 push합니다.
2. GitHub **Settings → Pages → Source: GitHub Actions**를 선택합니다.
3. **Actions → Publish OP-TEE showcase → Run workflow**에서 main을 선택합니다.
4. 완료 후 페이지·로그·PDF 링크를 확인합니다.

워크플로는 수동 실행입니다. 단순 push만으로 사이트를 배포하지 않습니다. 배포 대상으로 전시용 HTML·evidence·downloads만 선택합니다.

## PDF 갱신

scripts/build-pdf.py는 공개 결과 JSON에서 PDF를 만듭니다. CA/TA 구현 소스가 아니라 발표 자료 생성 도구입니다.

```bash
python3 -m pip install --target .local/pdf-tools reportlab==5.0.1
PYTHONPATH=.local/pdf-tools python3 scripts/build-pdf.py \
    evidence/p0-20261002T115454Z/results.json
```

기본 한글 글꼴은 WSL의 Windows 맑은 고딕 경로입니다. 다른 환경에서는 --font/--bold-font에 한글 TTF를 지정합니다. 원본 글꼴 파일은 이 저장소에 포함하지 않습니다. 다른 시험 회차를 반영할 때는 문장·수치·판정도 함께 검토합니다.
