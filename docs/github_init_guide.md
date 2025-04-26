# GitHub 프로젝트 초기 설정 가이드

## 1. GitHub 저장소 생성 시점
- 프로젝트 계획이 확정되고 기본 구조가 결정된 직후
- 실제 코드 작성 전, 프로젝트 구조 설계가 완료된 시점

## 2. 초기 설정 순서

### 2.1 GitHub에서 수행
1. GitHub에서 새 저장소 생성
   - 저장소 이름 설정
   - 공개/비공개 설정
   - README 초기화 하지 않음 (체크 해제)
   - .gitignore, 라이센스 추가하지 않음 (나중에 로컬에서 추가)

### 2.2 로컬에서 수행
1. 프로젝트 기본 구조 생성
   ```bash
   mkdir project_name
   cd project_name
   ```

2. Git 초기화 및 원격 저장소 연결
   ```bash
   git init
   git remote add origin git@github.com:username/repository.git
   ```

3. 최소한의 필수 파일 생성
   - `.gitignore`
   - `README.md`
   - 프로젝트 설정 파일 (예: requirements.txt)
   - 기본 프로젝트 구조 (디렉토리들)

## 3. 첫 커밋 시점
다음 항목들이 준비된 후 첫 커밋을 수행:

### 3.1 필수 포함 항목
1. 프로젝트 기본 구조
   - 주요 디렉토리 구조
   - 빈 `__init__.py` 파일들
   - 메인 실행 파일

2. 프로젝트 문서
   - `README.md` (프로젝트 설명)
   - 기술 문서 (예: 설계 문서)

3. 개발 환경 설정 파일
   - `.gitignore`
   - 의존성 파일 (예: requirements.txt)
   - 환경 설정 파일

### 3.2 첫 커밋 및 푸시
```bash
git add .
git commit -m "Initial commit: Project structure and basic setup
- Add project directory structure
- Add basic documentation
- Add development environment configuration"
git branch -M main
git push -u origin main
```

## 4. 주의사항
- 가상환경 디렉토리는 반드시 `.gitignore`에 포함
- 민감한 정보(API 키 등)는 커밋하지 않음
- 빌드 결과물, 캐시 파일 등은 `.gitignore`에 포함

## 5. 다음 단계
초기 설정 완료 후:
1. 이슈 템플릿 설정 (필요한 경우)
2. GitHub Actions 설정 (CI/CD가 필요한 경우)
3. 브랜치 보호 규칙 설정
4. 협업자 초대 (팀 프로젝트인 경우)

이 가이드를 프로젝트 시작 시 참고하시면 체계적으로 GitHub 저장소를 설정할 수 있습니다. 