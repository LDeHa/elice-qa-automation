# Security Policy

## 저장소에 포함하지 않는 정보

- 테스트 계정 ID와 비밀번호
- Access/Refresh Token, API Key, GitLab/Jenkins Secret Token
- Discord/Slack Webhook URL
- 실제 Jenkins·GitLab·VM·DEV API 주소와 공인 IP
- SSH Key, Jenkins `credentials.xml`, `$JENKINS_HOME/secrets`, 서버 백업
- 원본 JTL, Allure 결과, Jenkins 콘솔 로그, 요청·응답 전문

## 비밀정보 주입 방식

실제 운영에서는 Jenkins Credentials 또는 로컬 환경변수를 사용합니다. 저장소에는 자격증명 ID의 일반화된 예시만 둡니다.

```text
QA_STUDENT_ACCOUNT   -> Jenkins Username/Password Credential
QA_EDUCATOR_ACCOUNT  -> Jenkins Username/Password Credential
DISCORD_WEBHOOK_URL  -> Jenkins Secret Text Credential
SCM_READ_CREDENTIAL  -> Jenkins SCM Credential
```

## 노출 의심 시

1. 해당 비밀값을 즉시 폐기·재발급합니다.
2. 파일 삭제뿐 아니라 Git 이력 전체를 확인합니다.
3. GitHub Secret Scanning 결과와 최근 접근 로그를 확인합니다.
4. 필요하면 저장소를 비공개로 전환하고 관계자에게 알립니다.
