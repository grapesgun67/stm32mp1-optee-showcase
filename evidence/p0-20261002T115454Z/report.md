# P0 실물 보드 시험 기록

회차: `p0-20261002T115454Z`. 수집 시작(UTC): 2026-10-02T11:54:54.215650+00:00.

PASS 21 / FAIL 0 / 미실행 0. 이 숫자는 아래 실행 단위의 결과이며 기존 상세 P0 전체 항목의 완료율이 아니다.

## 시험 기준

- 보드: STM32MP157F-DK2, SSH로 직접 수집. 승인 암호 입력은 사용자 로컬 터미널에서 수행.
- 패키지: `portfolio-hello_1.0-r0.10_armhf.deb`
- deb SHA-256: `3a40219abc43714e549975a67e2c54029eca297309493dc1660e832d1d7feeea`
- 조회 시 저장소 HEAD: `44b7917a028a1eb6863b4bdc7b68ec05a9abff0f` (빌드 커밋 확정값이 아님)
- manifest SHA-256: `a26407058004af94ae4c9a4ce68818023d3c8902f49be2aabf0feddaad4ba034`
- CA SHA-256: `be5098269436f7ec177f0b23755ca04742fda4aaa679a5c8c069aa723ab410c6`
- TA SHA-256: `52a0436a3bfa3b0d61105918e162a20569ffd10df3357539e527739c19137982`

## 결과

| ID | 시험 | 판정 | 종료 코드 | 근거 |
|---|---|---|---|---|
| ENV | 실물 환경·설치 파일 확인 | PASS | 0 | [출력](logs/ENV.txt) |
| PING-4 | 같은 세션 PING 4회 | PASS | 0 | [출력](logs/PING-4.txt) |
| PING-NEW | 새 실행 카운터 초기화 | PASS | 0 | [출력](logs/PING-NEW.txt) |
| ECHO | ECHO 일반 입력 | PASS | 0 | [출력](logs/ECHO.txt) |
| ECHO-EMPTY | ECHO 빈 입력 | PASS | 0 | [출력](logs/ECHO-EMPTY.txt) |
| ECHO-16 | ECHO 최대 16바이트 | PASS | 0 | [출력](logs/ECHO-16.txt) |
| BAD-COMMAND | 알 수 없는 명령 거부 | PASS | 0 | [출력](logs/BAD-COMMAND.txt) |
| BAD-TYPES | PING 타입 오류 거부 | PASS | 0 | [출력](logs/BAD-TYPES.txt) |
| HASH-REF | sha256sum 기준값 | PASS | 0 | [출력](logs/HASH-REF.txt) |
| HASH-1 | SHA-256 / 1바이트 분할 | PASS | 0 | [출력](logs/HASH-1.txt) |
| HASH-2 | SHA-256 / 2바이트 분할 | PASS | 0 | [출력](logs/HASH-2.txt) |
| HASH-4 | SHA-256 / 4바이트 분할 | PASS | 0 | [출력](logs/HASH-4.txt) |
| KEY-BEFORE | 재부팅 전 공개키 조회 | PASS | 0 | [출력](logs/KEY-BEFORE.txt) |
| STORAGE | 영속 저장소 마운트 | PASS | 0 | [출력](logs/STORAGE.txt) |
| AUTH-NORMAL | 정상 승인 → 데이터 서명 | PASS | 0 | [출력](logs/AUTH-NORMAL.txt) |
| AUTH-TAMPER | 승인 서명 1바이트 변조 거부 | PASS | 1 | [출력](logs/AUTH-TAMPER.txt) |
| AUTH-WRONG-KEY | 다른 승인키 거부 | PASS | 1 | [출력](logs/AUTH-WRONG-KEY.txt) |
| AUTH-REPLAY | 새 요청에 과거 승인 재사용 거부 | PASS | 1 | [출력](logs/AUTH-REPLAY.txt) |
| REBOOT | 재부팅 및 새 boot ID 확인 | PASS | 0 | [출력](logs/REBOOT.txt) |
| KEY-AFTER | 재부팅 후 동일 공개키 확인 | PASS | 0 | [출력](logs/KEY-AFTER.txt) |
| ENV-AFTER | 재부팅 후 패키지·서비스 확인 | PASS | 0 | [출력](logs/ENV-AFTER.txt) |

## 판정 방법

PING은 카운터 및 PASS 출력, ECHO는 반환 바이트 비교 PASS, HASH는 Python hashlib 기준값과 보드 sha256sum/TA 출력을 대조했다. 승인 실패 시험은 파일 읽기 실패가 아니라 SIGN_AUTHORIZED의 nonzero 결과와 TA origin=4, nonzero 프로세스 종료 및 정상 서명 PASS 부재를 확인한다. BAD-COMMAND/BAD-TYPES는 예상 오류를 확인하는 시험 프로그램이므로 종료 코드 0이 정상이다.

재부팅은 실제 boot ID 전후 값을 호스트에서 비교했다. REBOOT 카드의 문장은 호스트 판정이며 UART 부팅 출력이 아니다. KEY-AFTER의 MATCH도 호스트에서 공개 n/e를 직접 비교한 결과다.

NORMAL/TAMPER는 기존 승인 도구에서 사용자가 승인한다. TAMPER는 그 서명 사본 1바이트만 바꾼다. WRONG-KEY는 검증한 새 요청에 대해 별도 메모리 내 시험키로 서명하고 그 키로 자체 검증한 뒤 TA에 제출한다. 기존 승인키는 교체하지 않는다. REPLAY는 NORMAL의 서명을 새 요청에 재사용한다.

## 공개 사본 처리

원본은 저장소 밖의 별도 회차 디렉터리에 보관한다. 공개 사본은 보드 호스트명/IP/PARTUUID/boot ID를 대체하고 긴 공개키 n/e를 생략한다. 원본 실행 결과와 오류 코드는 바꾸지 않는다. 개인키/암호/전체 환경 덤프는 포함하지 않는다. 웹페이지의 로그 패널은 실제 수집 출력의 발췌이며 화면 캡처를 가장하지 않는다.

## 한계

- 재부팅 키 유지와 REE FS 롤백 방지는 별개입니다. 단조 카운터 경고의 해결, HUK와 보안 부팅은 미검증입니다.
- 같은 세션 승인 재제출, 미준비·직접 명령 우회, 원문 결합 변조 및 상세 버퍼/상태 오류 시험은 이번 간단 실증 범위에서 제외했습니다.
- CA는 실행 시 TA에서 조회한 공개키로 검증합니다. 재부팅 전 공개키 파일을 입력한 독립 서명 검증은 미실행입니다.
- 보드와 로컬 deb의 CA/TA 파일 해시는 대조했습니다. 기록한 저장소 HEAD가 과거 deb의 정확한 빌드 입력이었다는 증명은 확보하지 않았습니다.
- SSH로 수집한 실제 출력의 공개용 발췌입니다. UART 전체 부팅 로그, 실제 데스크톱 스크린샷과 보드 사진은 포함하지 않았습니다.
