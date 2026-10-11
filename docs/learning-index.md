# 기술 학습 기록

현재 대화에 남아 있는 질문·답변, 기존 개발 문서와 코드 대조를 바탕으로 다시 정리했다. 과거 모든 대화의 원문을 복구한 기록은 아니다. 날짜는 학습 발생일이 아니라 정리일이다.

정리일: 2026-10-11

[브라우저로 읽기](../learning.html) · [날짜별 학습일지](journal-index.md)

- [01 clone한 코드가 보드에서 실행되기까지](learning/01-build.md)

- [02 CA의 호출은 누가 TA까지 전달하는가](learning/02-call-path.md)

- [03 세션 상태와 핸들은 누가 소유하는가](learning/03-session.md)

- [04 버퍼의 size는 실제 메모리를 할당하지 않는다](learning/04-memory.md)

- [05 여러 번 UPDATE해도 하나의 SHA-256인 이유](learning/05-hash.md)

- [06 서명 검증은 데이터가 참이라는 증명이 아니다](learning/06-signature.md)

- [07 핸들을 닫아도 영속 키가 남는 이유](learning/07-storage.md)

- [08 CA를 신뢰하지 않고 특정 요청을 승인하기](learning/08-authorization.md)

- [09 승인한 키와 지금 삭제할 키가 같은지 확인하기](learning/09-deletion.md)

- [10 Linux의 .ta 파일을 왜 신뢰할 수 있는가](learning/10-ta-loading.md)

- [11 정상 Linux도 Secure 메모리를 직접 읽지 못한다](learning/11-trustzone.md)

- [12 Secure Boot와 롤백 방지는 어디서 시작되는가](learning/12-boot-rollback.md)

공개 원문: learning-notes.json. 수정 후 python3 scripts/build-learning.py로 HTML과 Markdown을 함께 생성한다.
