# 세션 상태와 핸들은 누가 소유하는가

정리일: 2026-10-11 · 소스 대조: bdb8bd8

## 질문의 출발점

session_context는 TEEC_Session과 같은 구조체여야 하며, 모든 함수에 자동으로 전달되는가?

### 이해가 바뀐 지점

CA의 세션 핸들과 TA의 사용자 정의 상태를 같은 구조로 생각했던 의문을 해소했다. 프레임워크가 전달하는 진입점 인자와 개발자가 직접 넘기는 내부 함수 인자를 구분했다.

## 정리한 이해

OpenSession에서 상태 할당 → Invoke에서 같은 상태 사용 → 내부 handler에 명시적으로 전달 → CloseSession에서 자원 해제

### 구조체 멤버를 직접 정해도 되는가?

TA의 session_state는 서비스에 필요한 카운터, 해시 연산 핸들, 승인 대기 정보 등을 담는 구조다. CA의 TEEC_Session과 메모리 배치나 멤버를 맞출 필요가 없다.

### 자동으로 전달되는 범위는 어디인가?

OpenSessionEntryPoint에서 반환한 세션 컨텍스트를 TA 실행 환경이 이후 InvokeCommandEntryPoint와 CloseSessionEntryPoint에 전달한다. handle_ping 같은 일반 C 함수에는 dispatcher가 state를 인자로 넘겨야 한다.

### Create/Destroy와 Open/Close는 어떻게 다른가?

Create/Destroy는 TA 인스턴스의 생명주기, Open/Close는 세션의 생명주기다. 두 수명의 관계는 TA 플래그에 영향을 받는다. Invoke만 CA와 연결되는 것이 아니라 세션 열기·닫기도 호출 흐름의 일부다.

### 핸들을 닫고 NULL로 만들면 키도 삭제되는가?

핸들은 객체를 다루는 불투명한 참조다. 닫기는 사용 자원을 정리하며 영속 객체 삭제와 다르다. NULL 대입만으로 자원이 해제되지 않고, 닫힌 핸들을 재사용해서도 안 된다.

### 리팩토링과 C 보조 표현은 왜 필요했는가?

main은 옵션·세션·기능 호출·정리 흐름을 보여주고 기능별 처리를 함수로 나눴다. unused 속성은 의도적으로 사용하지 않는 인자 경고를 다루며 필수 보안 기능이 아니다. static inline도 무조건 인라인된다는 보장이 아니고, 함수 분리의 보안성을 대신하지 않는다.

## 코드와 연결

개발 저장소 기준. 기존 공개 발췌와 현재 함수명이 다를 수 있다.

- ta/entry.c: TA_OpenSessionEntryPoint / TA_CloseSessionEntryPoint
- ta/entry.c: struct session_state / handle_ping

- [함수 발췌와 PING 도식](../../fundamentals.html#session)

## 근거와 확인 범위

기존 PING 시험은 같은 세션의 증가와 새 실행의 초기화를 기록한다.

## 다음에 더 확인할 질문

세션을 닫으면 카운터, 열린 키 핸들, 저장된 영속 키 중 무엇이 사라지는가?

[전체 학습 목록](../../learning.html)
