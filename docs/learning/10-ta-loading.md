# Linux의 .ta 파일을 왜 신뢰할 수 있는가

정리일: 2026-10-11 · 소스 대조: bdb8bd8

## 질문의 출발점

신뢰하지 않는 파일시스템의 TA를 바꿔치기하면 무엇이 실행을 막는가?

### 이해가 바뀐 지점

정상 해시와 비교하면 된다는 답변에서, 기준 해시 자체의 보호가 필요하다는 점으로 확장했다. TA 배포 서명키, 외부 승인키, TA 내부 데이터 서명키를 분리했다.

## 정리한 이해

빌드·배포 환경에서 TA 서명 → Linux 파일시스템에 UUID.ta 배포 → OP-TEE의 신뢰 공개키로 검증 → 검증된 TA 로드

### 서명 파일이 따로 하나 더 생기는가?

일반적인 배포용 UUID.ta에는 실행 코드와 서명 관련 정보가 함께 들어간다. 빌드 중 분리 산출물이 있을 수 있지만 현재 승인 도구의 request.bin과 approval.sig 배포 방식과는 구분한다.

### 서명키는 어디에 있는가?

일반 구성에서 검증용 공개키는 OP-TEE에 포함하고 개인키는 TA 배포 서명 환경에서 사용한다. 제품 개인키를 일반 소스에 넣는 대신 별도의 제한된 서명 환경을 설계한다. 기본 개발키의 사용을 제품 보안으로 주장해서는 안 된다.

### .ta를 반드시 Linux 파일시스템에서 읽는가?

현재 구성은 REE 파일시스템 TA다. Early TA처럼 OP-TEE 이미지에 포함하는 방식, Secure Storage TA, core에 포함되는 PTA 등도 구분해야 한다. PTA는 단순히 저장 위치만 다른 일반 사용자 TA가 아니다.

### 서명이 맞으면 안전한 코드인가?

허가된 키로 서명된 내용인지 검증할 뿐 취약점이 없다는 보장은 아니다. 과거에 정상 서명된 취약한 TA는 별도 버전 정책이 없으면 서명 검사만으로 차단할 수 없다.

## 코드와 연결

개발 저장소 기준. 기존 공개 발췌와 현재 함수명이 다를 수 있다.

- ta/Makefile: TA dev kit 연결
- portfolio-hello_1.0.bb: UUID.ta 설치

- [실행 구조 학습](../../learning/02-call-path.html)

## 근거와 확인 범위

기존 로컬 문서는 빌드 로그에서 default_ta.pem 경로와 --ta-version 0 사용을 확인했다고 기록한다. 이번에는 개인키 파일을 열거나 현재 보드의 검증키를 새로 확인하지 않았다.

- [OP-TEE TA 빌드와 서명](https://optee.readthedocs.io/en/4.0.0/building/trusted_applications.html#signing-of-tas)

- [TA 종류와 로딩](https://optee.readthedocs.io/en/4.0.0/architecture/trusted_applications.html)

## 다음에 더 확인할 질문

TA 서명을 검사하는 OP-TEE 자체의 출처와 버전은 누가 검증해야 하는가?

[전체 학습 목록](../../learning.html)
