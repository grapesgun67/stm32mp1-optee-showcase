# 승인된 데이터만 서명하기: TA 코드로 보는 설계와 검토

기능 구현 → 커밋 → AI 검토 → diff 확인 → 선택 반영.

## CA의 실행 순서만으로 승인을 강제할 수 있을까?

CA는 전달자다. 다른 CA는 준비 단계를 생략하거나 입력을 바꿀 수 있다. 따라서 TA가 승인 대기 상태를 확인하고, 승인된 요청과 실제 서명할 데이터를 연결해야 한다. 챌린지는 CA나 사람의 신원 증명이 아니라 특정 요청의 승인 재사용을 막기 위한 값이다.

![승인 흐름](../assets/diagrams/sequence.svg)

## 입력 계약과 상태를 먼저 확인한다

아래 expected는 INPUT, OUTPUT, NONE, NONE 조합이며 approval은 256바이트 배열이다. 입력 서명은 정확히 256바이트, 출력 공간은 최소 256바이트여야 한다. 작은 출력 공간에는 필요한 크기를 반환한다. NULL/size 검사만으로 CA의 실제 할당 크기를 알아내는 것은 아니다. 전달 메모리 범위의 런타임 검사와 TA 명령 계약 검사는 구분한다.

entry.c 364–376행 · 함수 원형 + 본문 발췌

```c
static TEE_Result handle_sign_authorized(struct session_state *state,
                                         uint32_t types, TEE_Param params[4]);

/* 본문 일부: 앞뒤 코드는 생략 */
if (types != expected)
    return TEE_ERROR_BAD_PARAMETERS;
if (state == NULL || state->approval_phase != APPROVAL_PENDING ||
    state->signing_key == TEE_HANDLE_NULL)
    return TEE_ERROR_BAD_STATE;
if (params[0].memref.size != sizeof(approval) || params[0].memref.buffer == NULL)
    return TEE_ERROR_BAD_PARAMETERS;
if (params[1].memref.size < TA_PORTFOLIO_RSA_BYTES) {
    params[1].memref.size = TA_PORTFOLIO_RSA_BYTES;
    return TEE_ERROR_SHORT_BUFFER;
}
if (params[1].memref.buffer == NULL)
    return TEE_ERROR_BAD_PARAMETERS;
```

## 검증할 바이트와 서명할 해시를 고정한다

승인 서명을 TA 로컬 배열에 복사하여 이후 검증이 공유 버퍼를 반복해서 읽지 않게 한다. 이것만으로 복사 자체의 원자성을 보장하는 것은 아니다. 데이터 해시는 마지막 CA 입력이 아니라 처음 세션에 보관한 값을 사용한다. build_pending_request는 세션의 키·챌린지·해시로 요청을 재구성한다.

entry.c 379–381행 · 함수 원형 + 본문 발췌

```c
static TEE_Result handle_sign_authorized(struct session_state *state,
                                         uint32_t types, TEE_Param params[4]);

/* 본문 일부: 앞뒤 코드는 생략 */
TEE_MemMove(approval, params[0].memref.buffer, sizeof(approval));
TEE_MemMove(message_digest, state->pending_digest, sizeof(message_digest));
result = build_pending_request(state, request);
```

## 요청을 소비하고, 승인 성공 후에만 서명한다

clear_approval은 승인 상태를 IDLE로 바꾸고 챌린지와 보관 해시를 지운다. 이미 로컬에 복사한 해시를 검증 성공 후 서명한다. 사전 입력 검사 실패는 요청을 유지하지만, 그 이후의 처리 시도는 승인 실패나 내부 오류여도 소비한다. cleanup에서 로컬 해시와 승인 서명 배열을 지운다.

entry.c 384–401행 · 함수 원형 + 본문 발췌

```c
static TEE_Result handle_sign_authorized(struct session_state *state,
                                         uint32_t types, TEE_Param params[4]);

/* 본문 일부: 앞뒤 코드는 생략 */
    clear_approval(state);
    params[1].memref.size = 0;
    if (result != TEE_SUCCESS)
        goto cleanup;
    result = sha256_buffer(request, sizeof(request), request_digest);
    if (result != TEE_SUCCESS)
        goto cleanup;
    result = verify_approval(request_digest, approval);
    if (result != TEE_SUCCESS)
        goto cleanup;
    output_size = TA_PORTFOLIO_RSA_BYTES;
    result = sign_stored_digest(state, message_digest, params[1].memref.buffer, &output_size);
    if (result == TEE_SUCCESS)
        params[1].memref.size = output_size;
cleanup:
    TEE_MemFill(message_digest, 0, sizeof(message_digest));
    TEE_MemFill(approval, 0, sizeof(approval));
    return result;
```

## 왜 같은 세션인가? 왜 해시를 저장하는가?

2026-10-04 회고 대화에서 사용자는 세션이 바뀌면 이전 요청과의 연결을 보장할 수 없고, 마지막에 다른 해시를 받으면 바꿔치기를 탐지할 수 없다고 설명했다. 함께 정리한 핵심은 “CA 인증”이 아닌 “특정 요청의 승인 검증”이다. 세션 종료 시 승인 상태가 사라지고, 새 준비 요청은 새 챌린지를 사용한다. 이는 현재 이해에 대한 기록이며 최초 설계 당시의 동기로 소급하지 않는다.

## Git에서 확인되는 기능 변화

dd41a4a에는 요청 내보내기와 승인 준비 기능이 있고, c942118에는 handle_sign_authorized와 요청 재구성·소비가 추가되어 있다. 직접 서명 명령은 후자에서 ACCESS_DENIED로 바뀌었다. 이 비교는 기능 변화의 근거다. 사용자 초안과 AI 수정안을 일대일로 구분하는 증거로 사용하지 않는다.

## 기능별 코드 위치

개발 저장소의 portfolio-hello/files 기준. 전체 소스는 비공개이며 승인 처리 일부만 공개한다.

| 기능 | CA | TA |
|---|---|---|
| 세션 상태 | host/main.c: run_ping | ta/entry.c: TA_OpenSessionEntryPoint, handle_ping, TA_CloseSessionEntryPoint |
| 버퍼 전달 | host/main.c: run_echo | ta/entry.c: handle_echo |
| 분할 해시 | host/main.c: run_hash | ta/entry.c: handle_hash_begin/update/final |
| 영속 키 | host/main.c: run_sign_key_create | ta/entry.c: handle_key_create, open_signing_key |
| 승인과 서명 | host/main.c: run_prepare_sign, send_sign_authorized | ta/entry.c: handle_get_sign_challenge, handle_sign_authorized |

## 개발 방식과 확인 범위

초기 구현·커밋 → AI 검토 → diff 확인 → 선택 반영 방식으로 진행했습니다. TA 입력 검사 보완에 AI 도움을 받았습니다. 정상 승인·변조·다른 승인키·새 요청에 과거 승인 재사용은 확인했고, 같은 세션 재제출·직접 명령 우회·모든 파라미터 오류는 미시험입니다.


## 근거와 공개 범위

발췌 기준: 84cddb849933e09749711aa1e8e498a1ea67c6c9
meta-portfolio/recipes-security/portfolio-hello/files/ta/entry.c
파일 SHA-256: d1c25d57ef1614b0282e9eaa1bd41307377259b9c45bf9f59f741800505dbcee

[발췌 코드 라이선스](../assets/code/LICENSE) · [실제 시험 결과](../evidence/p0-20261002T115454Z/report.md)

