# CA의 호출은 누가 TA까지 전달하는가

정리일: 2026-10-11 · 소스 대조: bdb8bd8

## 질문의 출발점

libteec, Linux TEE 드라이버, OP-TEE와 tee-supplicant는 각각 무슨 일을 할까?

### 이해가 바뀐 지점

tee-supplicant를 CA의 일부나 모든 요청의 중간 단계로 보는 대신, OP-TEE가 필요한 Normal World 서비스를 요청할 때 사용하는 별도 프로세스로 구분했다.

## 정리한 이해

CA → libteec → ioctl → Linux TEE 드라이버 → SMC → Monitor → OP-TEE → TA → 결과 반환

### libteec와 드라이버는 무엇이 다른가?

CA는 TEEC API를 호출한다. libteec는 Linux TEE 인터페이스를 통해 세션·명령·메모리 정보를 전달하고, 드라이버는 커널 측 통신과 공유 메모리 처리를 담당한다. TA의 삭제 승인 정책을 드라이버가 판단하는 것은 아니다.

### RPC는 네트워크 통신인가?

여기서는 OP-TEE가 Normal World에 작업을 요청하고 응답을 받아 처리를 재개하는 경로다. 일부 요청은 커널이 처리하고, 파일 읽기 같은 작업은 tee-supplicant가 지원한다. 노트북 승인 도구와의 파일 전송은 별도의 응용 흐름이다.

### PING이면 tee-supplicant가 전혀 필요 없는가?

PING 처리 자체는 파일 저장을 요구하지 않지만, TA를 처음 로드할 때 REE 파일시스템의 .ta를 전달받는 데 supplicant가 관여할 수 있다. TA 로딩과 명령 본문을 나눠 생각해야 한다.

### 출력의 result와 origin은 어떻게 읽는가?

result=0은 성공 코드이며 origin은 결과가 어느 계층에서 왔는지 나타낸다. PASS/FAIL은 프로그램이 기대한 결과와 비교한 판정이다. altered data rejected는 변조한 데이터의 검증 실패를 기대한 시험이다. 명령 종료 코드는 직후에 확인해야 한다.

### 프로세스와 도구는 어떻게 확인했는가?

systemctl status로 서비스 상태, ps -ef로 프로세스, command -v로 셸이 찾는 실행 명령 위치를 확인했다. xtest의 존재는 시험 실행·성공 증거와 다르다. 예제 프로그램 부재는 optee-examples를 제외한 구성과도 구분해서 해석했다.

## 코드와 연결

개발 저장소 기준. 기존 공개 발췌와 현재 함수명이 다를 수 있다.

- host/main.c: invoke_command
- ta/entry.c: TA_InvokeCommandEntryPoint

- [시스템 구조](../../index.html#architecture)

- [PING 코드 설명](../../fundamentals.html#session)

## 근거와 확인 범위

기존 보드 로그의 tee-supplicant 실행·TEE 장치·PING 결과와 연결한다. 드라이버 전체 경로를 런타임 추적했다는 의미는 아니다.

- [Linux OP-TEE 인터페이스](https://docs.kernel.org/tee/op-tee.html)

## 다음에 더 확인할 질문

ioctl, SMC, RPC를 각각 어느 경계를 넘는 호출인지 설명할 수 있는가?

[전체 학습 목록](../../learning.html)
