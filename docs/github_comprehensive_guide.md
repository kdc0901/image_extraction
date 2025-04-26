# GitHub 종합 가이드

## 1. SSH 키 설정

### 1.1 SSH 키 생성
- 컴퓨터당 한 번만 설정 (모든 프로젝트에서 사용 가능)
```bash
# SSH 키 생성
ssh-keygen -t ed25519 -C "your_email@example.com"
# 기본 저장 위치: ~/.ssh/id_ed25519 (private key)
#                 ~/.ssh/id_ed25519.pub (public key)
```

### 1.2 GitHub에 SSH 키 등록
1. 공개키 복사
```bash
cat ~/.ssh/id_ed25519.pub
# 출력된 내용 복사
```
2. GitHub 설정
- GitHub.com → Settings → SSH and GPG keys → New SSH key
- 복사한 공개키 내용 붙여넣기

### 1.3 SSH 연결 테스트
```bash
ssh -T git@github.com
# "Hi username! You've successfully authenticated" 메시지 확인
```

## 2. Git 초기 설정

### 2.1 전역 설정 (컴퓨터당 한 번)
```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

### 2.2 프로젝트별 설정 (필요한 경우)
```bash
cd your_project
git config user.name "Your Name"
git config user.email "your_email@example.com"
```

## 3. GitHub 저장소 생성 및 초기화

### 3.1 새 저장소 생성
1. GitHub.com에서 생성
- New repository
- 저장소 이름 설정
- Public/Private 선택
- README 초기화 체크 해제

2. 로컬에서 생성
```bash
mkdir project_name
cd project_name
git init
```

### 3.2 원격 저장소 연결
```bash
# SSH 방식 (권장)
git remote add origin git@github.com:username/repository.git
# HTTPS 방식
git remote add origin https://github.com/username/repository.git
```

## 4. 브랜치 관리

### 4.1 기본 브랜치 설정
```bash
# main 브랜치로 이름 변경 (최초 1회)
git branch -M main
# 원격 저장소에 푸시
git push -u origin main
```

### 4.2 브랜치 작업
```bash
# 새 브랜치 생성
git checkout -b feature/new-feature
# 브랜치 목록 확인
git branch
# 브랜치 전환
git checkout branch-name
# 브랜치 삭제
git branch -d branch-name
```

## 5. 일상적인 Git 명령어

### 5.1 기본 작업 흐름
```bash
# 변경사항 확인
git status
# 파일 스테이징
git add filename
git add .  # 모든 변경사항
# 커밋
git commit -m "커밋 메시지"
# 원격 저장소에 푸시
git push origin main
```

### 5.2 변경사항 가져오기
```bash
# 원격 저장소의 변경사항 가져오기
git pull origin main
# 특정 브랜치의 변경사항 가져오기
git pull origin branch-name
```

## 6. Git 용어 설명

### 6.1 주요 용어
- **origin**: 원격 저장소의 기본 이름
- **main**: 주 브랜치 (이전의 'master')
- **HEAD**: 현재 작업 중인 브랜치의 최신 커밋
- **staging area**: 커밋 대기 영역
- **remote**: 원격 저장소

### 6.2 자주 사용되는 개념
- **fork**: 다른 사용자의 저장소를 복사
- **clone**: 원격 저장소를 로컬에 복사
- **pull request**: 변경사항 병합 요청
- **merge**: 브랜치 병합

## 7. 프로젝트별 설정

### 7.1 새 프로젝트마다 필요한 설정
1. 저장소 생성 (GitHub.com)
2. 로컬 저장소 초기화
3. 원격 저장소 연결
4. 초기 파일 커밋

### 7.2 재사용 가능한 설정
- SSH 키 (컴퓨터당 1회)
- Git 전역 설정 (컴퓨터당 1회)
- .gitignore 템플릿

## 8. 보안 및 모범 사례

### 8.1 보안 관련
- SSH 키 private key 절대 공유하지 않기
- 민감한 정보 커밋하지 않기
- .gitignore 파일 잘 관리하기

### 8.2 커밋 관련
```bash
# 좋은 커밋 메시지 예시
git commit -m "Add user authentication feature
- Implement login functionality
- Add password encryption
- Create user session management"
```

## 9. 문제 해결

### 9.1 일반적인 문제
```bash
# 원격 저장소 URL 확인
git remote -v
# 원격 저장소 변경
git remote set-url origin new-url
# 마지막 커밋 수정
git commit --amend
```

### 9.2 충돌 해결
```bash
# 충돌 발생 시
git status  # 충돌 파일 확인
# 충돌 부분 수동 수정
git add .
git commit -m "Resolve merge conflicts"
```

## 10. GitHub CLI

### 10.1 설치 및 설정
```bash
# macOS
brew install gh
# 로그인
gh auth login
```

### 10.2 주요 명령어
```bash
# 저장소 생성
gh repo create
# PR 생성
gh pr create
# 이슈 생성
gh issue create
``` 