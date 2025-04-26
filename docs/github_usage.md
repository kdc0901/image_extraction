# GitHub 사용 가이드

## 1. GitHub 기본 설정

### 1.1 로컬 Git 설정
```bash
# 사용자 정보 설정
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 기본 에디터 설정
git config --global core.editor "code --wait"  # VS Code 사용시
```

### 1.2 SSH 키 설정
```bash
# SSH 키 생성
ssh-keygen -t ed25519 -C "your.email@example.com"

# SSH 키 확인 및 복사
cat ~/.ssh/id_ed25519.pub
```

## 2. GitHub 저장소 관리

### 2.1 저장소 생성 및 연결
```bash
# 로컬 저장소 초기화
git init

# 원격 저장소 연결
git remote add origin https://github.com/username/repository.git

# 또는 SSH로 연결
git remote add origin git@github.com:username/repository.git
```

### 2.2 기본 작업 흐름
```bash
# 변경사항 확인
git status

# 변경사항 스테이징
git add .

# 변경사항 커밋
git commit -m "커밋 메시지"

# 원격 저장소에 푸시
git push origin main
```

## 3. 브랜치 관리

### 3.1 브랜치 작업
```bash
# 브랜치 생성
git branch feature-branch

# 브랜치 전환
git checkout feature-branch

# 브랜치 생성 및 전환 (한 번에)
git checkout -b feature-branch

# 브랜치 목록 확인
git branch
```

### 3.2 병합 및 리베이스
```bash
# 병합
git merge feature-branch

# 리베이스
git rebase main
```

## 4. 협업 작업

### 4.1 Pull Request (PR) 작업 흐름
1. 새로운 기능 브랜치 생성
2. 변경사항 커밋
3. 원격 저장소에 푸시
4. GitHub에서 PR 생성
5. 코드 리뷰 진행
6. 변경사항 수정 (필요시)
7. PR 승인 및 병합

### 4.2 충돌 해결
```bash
# 최신 변경사항 가져오기
git fetch origin
git merge origin/main

# 충돌 해결 후
git add .
git commit -m "충돌 해결"
git push origin feature-branch
```

## 5. GitHub 기능 활용

### 5.1 Issues
- 작업 항목 추적
- 버그 리포트
- 기능 요청
- 프로젝트 관리

### 5.2 Projects
- 칸반 보드
- 작업 진행 상황 추적
- 마일스톤 관리

### 5.3 Actions
- CI/CD 파이프라인
- 자동화된 테스트
- 배포 자동화

## 6. 보안 및 권한 관리

### 6.1 저장소 보안
- 브랜치 보호 규칙 설정
- 코드 리뷰 요구사항 설정
- 상태 체크 요구사항 설정

### 6.2 협업자 관리
- 팀 멤버 초대
- 권한 레벨 설정
- 코드 리뷰어 지정

## 7. 모범 사례

### 7.1 커밋 메시지
- 명확하고 간결하게 작성
- 현재형 사용
- 관련 이슈 번호 포함

### 7.2 브랜치 네이밍
- feature/기능명
- bugfix/버그명
- hotfix/긴급수정사항

### 7.3 코드 리뷰
- 명확한 리뷰 코멘트
- 건설적인 피드백
- 코드 품질 유지 