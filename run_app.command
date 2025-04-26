#!/bin/zsh

# 스크립트 파일이 위치한 디렉토리로 이동
cd "$(dirname "$0")"

# Python 가상 환경 경로 (상황에 맞게 수정 필요)
VENV_PYTHON="venv311_new/bin/python"

# PYTHONPATH 설정
export PYTHONPATH=src

# GUI 애플리케이션 실행
echo "애플리케이션을 실행합니다..."
"$VENV_PYTHON" src/run.py

# 스크립트 종료 후 터미널 창 유지 (선택 사항)
# exec $SHELL 