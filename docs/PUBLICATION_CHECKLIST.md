# GitHub 공개 전 체크리스트

현재 저장소는 먼저 **Private**으로 생성하는 것을 기준으로 합니다. 아래 항목을 모두 확인한 뒤 Public 전환을 결정합니다.

## 권한과 저작권

- [ ] 팀원에게 공동 산출물의 공개 범위를 확인함
- [ ] 교육기관·서비스의 프로젝트 공개 정책을 확인함
- [ ] 팀원 코드를 내가 작성한 것처럼 설명하지 않음
- [ ] 외부 라이브러리·이미지·폰트의 라이선스를 확인함

## 비밀정보와 개인정보

- [ ] 실제 계정 ID·비밀번호가 없음
- [ ] Access/Refresh Token, API Key, Webhook, Jenkins/GitLab Secret이 없음
- [ ] VM·Jenkins·GitLab·DEV API의 실제 주소와 IP가 없음
- [ ] 이메일, 실명, 사번, 내부 사용자명이 불필요하게 포함되지 않음
- [ ] 스크린샷의 주소창, 알림 작성자, 커밋 정보, 토큰을 가림

## 테스트 산출물

- [ ] JTL에 요청 URL·파라미터·응답 본문이 남지 않았는지 확인함
- [ ] Allure/JUnit에 계정, URL, Header, 응답 전문이 남지 않았는지 확인함
- [ ] Jenkins 콘솔 로그와 Workspace를 업로드하지 않음
- [ ] 영상·htop 캡처의 사용자명과 실행 경로를 제거함

## Git과 자동 점검

- [ ] 원본 Git 이력을 가져오지 않고 새 이력으로 시작함
- [ ] `git grep`, GitHub Secret Scanning으로 재점검함
- [ ] `.gitignore`가 `.env`, 자격증명, 리포트와 서버 백업을 차단함
- [ ] GitHub Actions/외부 서비스가 비밀값 없이 동작하는지 확인함
- [ ] 공개 직전 저장소를 새로 Clone해 전체 파일을 다시 검토함

## Jenkins 공개 원칙

- [ ] `Jenkinsfile.example`에는 일반화된 Credential ID와 예시 URL만 사용함
- [ ] `$JENKINS_HOME`, `credentials.xml`, `secrets/`, SSH Key가 없음
- [ ] Job XML과 Plugin 설정 원본 대신 설정 절차만 설명함
- [ ] Jenkins Build/Allure 링크는 실제 주소가 아닌 예시로 표시함
