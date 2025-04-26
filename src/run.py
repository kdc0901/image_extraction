#!/usr/bin/env python3
"""
YouTube 동영상 처리 시스템 실행 스크립트
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui import MainWindow
from utils import setup_logger

def main():
    # 로거 설정
    logger = setup_logger(__name__, 'INFO')
    logger.info("애플리케이션 시작")
    
    # QApplication 인스턴스 생성
    app = QApplication(sys.argv)
    
    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()
    
    # 이벤트 루프 시작
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 