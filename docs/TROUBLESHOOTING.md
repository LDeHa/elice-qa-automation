# 주요 트러블슈팅

## 1. GitLab Webhook이 Jenkins에 도달하지 못함

**현상**
브라우저에서는 Jenkins가 열리지만 GitLab Webhook 요청은 Jenkins에 도달하지 못했습니다.

**원인**
Jenkins가 Loopback 인터페이스에만 바인딩되어 외부 네트워크 요청을 받지 못하는 상태였습니다.

**해결**
서비스 Listen Address를 필요한 인터페이스에서 수신하도록 변경하고 Jenkins를 재시작했습니다. 실제 적용에서는 `0.0.0.0` 바인딩만으로 끝내지 않고 방화벽, 인증, 접근 허용 범위를 함께 점검해야 합니다.

**검증**
GitLab에서 Webhook Test를 실행해 Jenkins가 HTTP 응답을 반환하는 것을 확인했습니다.

## 2. Webhook HTTP 403 - No valid crumb

**현상**
GitLab 요청이 Jenkins까지 도착했지만 403과 `No valid crumb` 메시지를 반환했습니다.

**원인**
일반 Jenkins Job URL로 POST하여 CSRF 보호 대상 요청이 되었습니다.

**해결**
GitLab Plugin이 제공하는 `/project/{job-name}` Webhook Endpoint를 사용하고 Job의 GitLab Trigger를 활성화했습니다.

## 3. Webhook HTTP 401 - Invalid token

**현상**
Endpoint는 맞지만 401 `Invalid token`이 발생했습니다.

**원인**
GitLab Webhook Secret Token과 Jenkins Job의 Secret Token이 일치하지 않았습니다.

**해결 및 검증**
두 설정의 토큰을 동일하게 다시 등록한 뒤 Test 요청에서 HTTP 200을 확인했습니다. 실제 토큰은 문서나 저장소에 기록하지 않았습니다.

## 4. Jenkins의 Webhook URL이 localhost로 표시됨

**현상**
Job 설정 화면에 표시되는 Webhook URL이 `localhost` 기반이었습니다.

**원인**
Jenkins System URL이 외부 접근 주소로 설정되지 않았습니다.

**해결**
Jenkins Location의 Root URL을 실제 사용자가 접근 가능한 주소로 설정했습니다. 포트폴리오에는 실제 주소 대신 예시 도메인만 사용합니다.

## 5. 로컬 알림과 Jenkins 알림이 중복될 가능성

**현상**
팀원이 만든 로컬 pytest 알림과 Jenkins 전용 결과 알림의 역할이 겹쳐 한 번의 테스트에서 메시지가 중복될 수 있었습니다.

**해결**
로컬 알림은 `pytest --notifier discord`처럼 명시적으로 요청할 때만 실행하고, Jenkins에서는 파이프라인 `post` 단계의 전용 스크립트만 실행하도록 경로를 분리했습니다. 팀원의 기능은 삭제하지 않고 실행 책임만 분리했습니다.

## 6. HTTP 200인데 API 테스트가 실패해야 하는 경우

**현상**
필수 기관 헤더를 제거했는데도 DEV API가 HTTP 200을 반환했습니다.

**판단**
자동화 코드의 오류로 숨기거나 성공으로 처리하지 않고 API 명세와 실제 동작의 불일치로 분류했습니다.

**해결**
해당 TC를 `pytest.xfail`로 선언해 알려진 결함을 결과에 남겼고, 불필요한 오류 전문이 콘솔에 중복 출력되지 않도록 로그 순서를 조정했습니다.
