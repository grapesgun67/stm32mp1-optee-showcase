# 정상 Linux도 Secure 메모리를 직접 읽지 못한다

정리일: 2026-10-11 · 소스 대조: bdb8bd8

## 질문의 출발점

정상 Linux는 제한을 통과하고 탈취된 Linux만 차단되는 것인가?

### 이해가 바뀐 지점

하드웨어가 정상·악성 커널을 판별한다는 혼동을 해소했다. 둘 다 직접 접근은 제한되고, SMC를 통해 정해진 Secure 코드에 작업을 요청한다는 구조로 이해를 수정했다.

## 정리한 이해

정상·악성 Linux: Non-secure → 직접 Secure 메모리 접근: 차단 → SMC: 정해진 Secure 코드 실행 → TA: 요청 형식·권한 판단

### Linux root가 왜 칩 전체의 최고 권한이 아닌가?

root는 Linux의 사용자 권한이다. 커널을 장악해도 Non-secure 실행 상태에서의 권한이며 Secure 상태를 임의로 얻는 것은 아니다. Cortex-A7에서는 Monitor가 World 전환을 중개한다.

### 보호를 코드로 구현해야 하는가?

TF-A·OP-TEE 같은 보안 펌웨어가 보호 영역을 설정하고, 이후 메모리 접근은 하드웨어가 강제한다. TA가 매 접근마다 if문으로 Linux 읽기를 막는 것이 아니다. 올바른 설정과 보호된 설정 변경 권한이 전제다.

### TZC가 악성 SMC를 판별하는가?

TZC는 DDR 주소·읽기/쓰기·보안 속성 등의 접근 조건을 확인한다. SMC의 업무 명령이나 승인 서명을 이해하지 않는다. Linux의 페이지 테이블만 바꿔도 이 하드웨어 조건은 사라지지 않는다.

### SMC를 보내면 Linux가 Secure 권한을 얻는가?

Linux 코드는 중단되고 정해진 Monitor·OP-TEE 코드가 실행된다. 호출 인자는 그 코드가 검증할 입력이다. 승인된 서비스 호출과 요청자가 마음대로 Secure 코드를 실행하는 것은 다르다.

### 그렇다면 시큐어 코딩은 왜 필요한가?

하드웨어는 직접 접근을 막는다. 하지만 TA가 악성 입력에 속아 개인키를 복사하거나 승인 없이 서명하면 서비스 경로로 악용된다. 격리와 입력·권한 검사는 서로 다른 공격 경로를 막는다.

## 코드와 연결

개발 저장소 기준. 기존 공개 발췌와 현재 함수명이 다를 수 있다.

- ta/entry.c: TA_InvokeCommandEntryPoint의 명령 분기
- ta/entry.c: handle_sign_with_approval의 승인 검사

- [요청 인가 학습](../../learning/08-authorization.html)

- [서비스 구조](../../index.html#architecture)

## 근거와 확인 범위

이번 내용은 공식 아키텍처와 프로젝트 요청 검사를 연결한 이론 정리다. 실제 보드의 TZC 레지스터·DMA·디버그 보호를 공격 시험으로 검증했다는 의미는 아니다.

- [OP-TEE의 World 전환](https://optee.readthedocs.io/en/4.0.0/architecture/core.html)

- [STM32MP1 TZC](https://wiki.st.com/stm32mpu/wiki/TZC_internal_peripheral)

- [STM32MP1 ETZPC](https://wiki.st.com/stm32mpu/wiki/ETZPC_internal_peripheral)

## 다음에 더 확인할 질문

개인키를 직접 읽는 공격과 키를 이용해 서명받는 공격의 방어를 각각 설명할 수 있는가?

[전체 학습 목록](../../learning.html)
