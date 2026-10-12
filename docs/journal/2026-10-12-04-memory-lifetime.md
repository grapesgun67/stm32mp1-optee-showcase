# 포인터를 비우는 것과 자원을 해제하는 것은 다르다

기록일: 2026-10-12

포인터 별칭과 데이터 복사에서 시작해, 해제 후 접근·소유권·실패 경로 정리·TA 세션 진입점을 실제 코드와 연결했다.

## 공부를 시작한 질문

세션 데이터를 가리키는 포인터와 별도 배열로 복사한 데이터는 원본 초기화·해제 후 각각 어떻게 되는가?

### 처음 이해했던 내용

원본을 0으로 지우면 포인터로 보는 값도 바뀌고, 복사한 배열은 유지된다고 답했다. 다만 해제 후 접근은 반드시 segmentation fault가 발생한다고 생각했고, 메모리 해제와 파일·객체 핸들 닫기를 혼동했다.

## 질의응답에서 수정한 이해

- 포인터 복사는 같은 메모리를 가리키는 별칭을 만든다. 데이터 복사는 별도 저장 공간에 값을 남긴다.
- 해제 후 접근은 정의되지 않은 동작이다. 즉시 오류가 날 수도 있지만 예전 값처럼 보이거나 다른 데이터를 읽을 수도 있다.
- NULL 대입은 포인터 변수 하나를 바꿀 뿐이다. 자원을 해제하지 않으며 다른 별칭도 자동으로 NULL이 되지 않는다.
- 자원을 획득한 뒤 누가 정리할지 계약을 정한다. 성공뿐 아니라 중간 실패에도 그때까지 획득한 자원을 정리해야 한다.
- 정정: 임시 객체에 TEE_CloseObject를 사용할 수 없다는 앞선 설명은 잘못이었다. 규격상 임시 객체에서는 TEE_FreeTransientObject와 동등하다.

## 같은 주소를 기억한 경우와 데이터를 복사한 경우

saved = state->pending_delete_key_fingerprint_sha256는 배열 데이터를 복사하지 않는다. saved는 세션 안의 배열을 가리킨다. 반면 별도 copied 배열에 TEE_MemMove로 복사하면 새로운 저장 공간에 지문 바이트가 남는다.

clear_pending_approval이 원본 배열을 0으로 채우면 saved로 읽는 내용도 0이다. saved에 저장된 주소 자체가 0으로 바뀌는 것은 아니다. copied는 자기 수명이 유지되는 동안 이전 지문을 보관한다.

TEE_Free(state) 이후 saved로 읽으면 해제 후 접근이다. 크래시가 나지 않아도 안전한 코드가 아니다. state = NULL을 실행해도 saved에는 이전 주소가 남으므로 별칭의 사용 가능 기간까지 관리해야 한다.

## NULL·메모리 해제·핸들 닫기는 서로 다른 동작

state = NULL만 실행하면 할당된 구조체는 해제되지 않는다. 마지막 참조를 잃으면 메모리 누수가 생길 수 있다. 반대로 TEE_Free(state)는 구조체 메모리를 해제하지만 state 변수에 자동으로 NULL을 대입하지 않는다.

구조체 안에 핸들이 있다고 해서 구조체 해제 시 그 핸들의 자원이 재귀적으로 정리되지는 않는다. malloc/free는 메모리, open/close는 파일 디스크립터처럼 자원의 종류에 맞는 API를 사용한다.

이미 정리한 자원을 공통 cleanup에서 다시 정리하면 이중 해제가 될 수 있다. 하나의 소유자와 정리 경로를 정하고, 계속 살아 있는 핸들 변수는 정리 후 TEE_HANDLE_NULL로 갱신한다. NULL 대입만으로 모든 별칭의 문제가 해결되지는 않는다.

## 호출자가 정리할지 함수가 정리할지는 소유권 계약

호출자가 소유한 키 핸들을 inspect_key에 빌려주는 설계라면 조회 함수는 핸들을 닫지 않는다. 함수 이름만으로 결정되는 규칙은 아니며, 인자로 받은 자원을 빌리는지 소유권을 받는지 명시해야 한다.

create_state가 성공 시 *out_state에 새 구조체를 전달한다면 소유권을 호출자에게 넘길 수 있다. 전달 직후 함수 안에서 해제하면 호출자는 이미 해제된 메모리를 받는다.

반대로 생성 도중 실패했다면 함수가 그때까지 확보한 자원을 정리하고 오류를 반환한다. 출력 포인터를 처음에 NULL로 설정하면 실패 시 유효한 객체가 반환되었다고 오해하는 것을 줄일 수 있다.

## CA가 호출하는 API와 TA의 진입점

CA는 libteec의 TEEC_OpenSession·TEEC_InvokeCommand·TEEC_CloseSession을 호출한다. 통신 경로를 거쳐 OP-TEE가 TA 실행을 진행하고, TA 실행 환경이 TA_OpenSessionEntryPoint·TA_InvokeCommandEntryPoint·TA_CloseSessionEntryPoint를 호출한다. CA가 TA의 C 함수를 직접 호출하는 구조는 아니다.

TA_OpenSessionEntryPoint에서 session_context 출력으로 넘긴 세션 상태는 이후 해당 세션의 Invoke·Close 진입점에 전달된다. CA의 TEEC_Session과 동일한 구조체가 아니며, TA 내부 포인터를 CA가 받는 것도 아니다.

자동 전달은 정해진 진입점 호출에 대한 이야기다. 개발자가 만든 내부 함수 handle_xxx에 state가 필요하면 dispatcher에서 handle_xxx(state, ...)처럼 직접 넘겨야 한다.

OpenSession이 중간에 실패한 경우의 자원은 그 실패 경로에서 정리한다. 나중에 CloseSession 진입점이 호출되어 정리해 줄 것이라고 전제하면 안 된다.

## 현재 TA는 안쪽 자원을 정리한 뒤 구조체를 해제한다

현재 TA_CloseSessionEntryPoint(void *session_context)는 release_hash_operation(state) → clear_pending_approval(state) → 서명 키 핸들 TEE_CloseObject → TEE_Free(state) 순서로 정리한다.

hash_op는 TEE_AllocateOperation으로 얻는 암호 연산 핸들이다. signing_key_handle은 키 객체 핸들이다. 둘 다 OpenPersistentObject로 연 핸들이라는 설명은 맞지 않는다.

state부터 해제하면 이후 state->hash_op나 state->signing_key_handle을 읽는 것부터 해제 후 접근이 된다. 자원 핸들을 잃어 정리를 놓칠 수도 있다. 구조체를 먼저 없애지 않는 이유는 누수와 잘못된 접근을 함께 피하기 위해서다.

영속 키 핸들을 닫는 것은 저장된 키를 삭제하는 것이 아니다. 세션 RAM과 열린 핸들은 정리하지만, 영속 객체의 삭제는 별도 삭제 API와 인가 절차로 수행한다.

## 중간 실패 예제와 정리 API의 정확한 대응

임시 키 할당 성공 후 연산 할당이 실패했다면 임시 키를 정리한다. 둘 다 성공한 뒤 검증에 실패했다면 TEE_FreeOperation(operation), TEE_FreeTransientObject(key)처럼 두 자원을 모두 정리한다. 초기 핸들을 TEE_HANDLE_NULL로 두고 획득 성공 여부에 따라 cleanup을 실행한다.

대표적인 대응은 TEE_Malloc → TEE_Free, TEE_AllocateOperation → TEE_FreeOperation, TEE_AllocateTransientObject → TEE_FreeTransientObject, TEE_OpenPersistentObject → TEE_CloseObject다.

앞선 질의응답에서 임시 키에 TEE_CloseObject를 제안한 답을 틀렸다고 설명했지만, GlobalPlatform 규격은 임시 객체에서 TEE_CloseObject와 TEE_FreeTransientObject가 동등하다고 명시한다. 임시 객체라는 의도를 드러내기 위해 후자를 선택할 수 있으나 전자를 무조건 오류라고 할 수 없다.

이 대응을 암기하는 것에 더해, 각 분기에서 어떤 자원을 실제로 확보했는지와 누가 최종 정리를 책임지는지를 추적하는 것이 핵심이다.

## 내 구현과 연결한 부분

승인 대상 지문을 별도 배열에 복사하는 이유와 세션 요청을 소비하는 이유를 구분한 뒤, 복사본 자체의 수명과 세션이 소유한 자원의 정리까지 연결했다. 현재 TA_CloseSessionEntryPoint와 release_hash_operation을 확인해 설명 순서를 실제 코드와 맞췄다.

- ta/entry.c: TA_OpenSessionEntryPoint — 세션 상태 생성과 전달
- ta/entry.c: TA_CloseSessionEntryPoint — 안쪽 자원 정리 후 세션 메모리 해제
- ta/entry.c: release_hash_operation — 연산 해제와 핸들 초기화
- ta/entry.c: clear_pending_approval — 대기 요청 상태와 데이터 초기화

- [앞선 내부 복사·요청 소비 기록](../../journal/2026-10-12-03-copy-consume.html)

- [메모리 주제별 정리](../../learning/04-memory.html)

## 다음에 확인할 것

- 다음 주제는 암호·키 관리: TA 데이터 서명용 개인키와 노트북 승인용 개인키가 각각 무엇을 서명하며, 유출 시 무엇이 가능한지 설명하기.
- 실패 분기마다 남은 자원과 정리 주체를 직접 표시해 보는 연습으로 이어가기.

## 확인한 자료와 기록 범위

2026-10-12 질의응답과 현재 로컬 소스를 기준으로 정리했다. 해제 후 접근·중간 할당 실패는 설명용 사례이며 새 보드 시험 결과가 아니다. 임시 객체 닫기 API의 설명은 GlobalPlatform 규격을 확인해 정정했다.

- [GlobalPlatform TEE Internal Core API v1.3.1 — 객체와 연산 API](https://globalplatform.org/wp-content/uploads/2021/03/GPD_TEE_Internal_Core_API_Specification_v1.3.1_PublicRelease_CC.pdf)

- [OP-TEE TA 설명](https://optee.readthedocs.io/en/4.0.0/architecture/trusted_applications.html)

[날짜별 목록](../journal-index.md)
