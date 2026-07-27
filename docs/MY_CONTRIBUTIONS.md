# 내 기여 범위

## 1. 클래스 홈 API 자동화

클래스 홈과 일정 API를 대상으로 정상, 잘못된 식별자, 필수 헤더 누락, 비인증, 기관 간 접근, 역할별 수정 권한, count 경계값을 검증했습니다.

주요 구현 내용:

- API 호출을 테스트 본문과 분리한 `HomeAPI` 객체 설계
- 학생·교육자·비인증 클라이언트를 fixture로 분리
- 반복되는 잘못된 입력을 `pytest.mark.parametrize`로 통합
- `smoke`, `student`, `educator`, `positive`, `negative`, `boundary` 마커 적용
- Allure 제목에 TC 식별자와 검증 의도를 표시
- 서버 명세 불일치를 `XFail`로 관리해 정상 통과와 구분

대표 샘플:

- [`examples/class_home/home_api.py`](../examples/class_home/home_api.py)
- [`examples/class_home/test_home_sample.py`](../examples/class_home/test_home_sample.py)

## 2. Jenkins CI/CD

기존의 주기적 Poll SCM 방식에서 Push Webhook 기반으로 자동화 흐름을 정리했습니다.

- `main`, `develop` Push만 빌드하도록 Webhook/Trigger 정규식 제한
- Webhook이 전달한 브랜치를 Jenkins Checkout 대상에 반영
- Checkout → 환경 구성 → pytest → JUnit/Allure → Discord 알림 단계 구성
- 테스트 계정, SCM 인증, Discord Webhook을 Jenkins Credentials로 관리
- Jenkins 접속 바인딩과 Webhook의 403 crumb/401 token 문제 해결
- 팀원이 재사용할 수 있도록 VM/Jenkins 운영 안내와 장애 확인 순서 작성

파이프라인 예시는 [`ci/Jenkinsfile.example`](../ci/Jenkinsfile.example), 구조 설명은 [`CI_CD.md`](CI_CD.md)에 정리했습니다.

## 3. 테스트 결과 알림

Jenkins가 만든 JUnit XML과 Allure 결과를 파싱해 Discord에 전달하는 모듈을 구성했습니다.

- Passed, Failed, Error, Skipped, XFail 분리 집계
- 기술적인 pytest 노드명 대신 Allure 제목 우선 표시
- 브랜치, 트리거, 커밋, 실행자, 소요 시간, 빌드·Allure 링크 포함
- Discord 2,000자 제한을 고려해 실패 목록을 제한하고 긴 메시지를 안전하게 축약
- 네트워크 실패가 발생해도 원인을 표준 오류로 남기도록 처리
- 실제 Discord 호출 없이 파서와 POST payload를 검증하는 단위 테스트 작성

## 4. 부하 테스트 관찰

JMeter 실행 담당자와 분리하여 부하 생성 VM의 `htop`을 관찰했습니다. 이 역할의 목적은 응답 지연이 DEV 서버 문제인지, JMeter 클라이언트 자원 한계인지 구분하는 것이었습니다.

- 5→10→20→30명 단계별 CPU·메모리 캡처
- 단일 코어/스레드 순간 피크와 8 vCPU 전체 포화 상태를 구분
- 메모리 증가가 지속되는지와 Swap 사용 여부 확인
- 서버·DB 지표 접근 권한이 없다는 한계를 결과 보고서에 명시

자세한 해석은 [`LOAD_TEST.md`](LOAD_TEST.md)에 기록했습니다.

## 5. 협업 기여

- 공통 알림 코드와 Jenkins 전용 알림의 역할이 겹치지 않도록 실행 경로 분리
- 팀 공통 파일을 최소한으로 변경하는 리팩터링 원칙 적용
- VM/Jenkins 사용 방법을 화면 공유로 설명하고 운영 지식 전달
- 발표 자료의 자동화 흐름·문제 해결 파트를 도식화하고 피드백 반영

## 기여 범위 해석 시 유의점

이 프로젝트는 4인 팀 작업입니다. 게시판, 학습 과목, 수업 일정 등 다른 메뉴의 테스트와 공통 프레임워크 일부는 팀원의 기여이며, 이 저장소에서는 제 담당 영역만 대표 샘플로 제공합니다.
