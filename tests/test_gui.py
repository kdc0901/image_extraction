import sys
import os
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow

@pytest.fixture
def app():
    app = QApplication(sys.argv)
    yield app
    app.quit()

@pytest.fixture
def window(app):
    window = MainWindow()
    yield window
    window.close()

def test_initial_state(window):
    """초기 상태 테스트"""
    assert window.url_input.text() == ""
    assert window.extract_button.isEnabled()
    assert not window.cancel_button.isEnabled()
    assert not window.open_output_button.isEnabled()
    assert window.progress_bar.value() == 0
    assert window.status_label.text() == "준비됨"

def test_url_validation(window):
    """URL 입력 검증 테스트"""
    window.url_input.setText("")
    window.dir_input.setText("/test/dir")
    QTest.mouseClick(window.extract_button, Qt.MouseButton.LeftButton)
    assert window.extract_button.isEnabled()  # 에러 메시지 표시 후 버튼 활성화 상태 유지

def test_directory_validation(window):
    """디렉토리 입력 검증 테스트"""
    window.url_input.setText("https://youtube.com/watch?v=test")
    window.dir_input.setText("")
    QTest.mouseClick(window.extract_button, Qt.MouseButton.LeftButton)
    assert window.extract_button.isEnabled()  # 에러 메시지 표시 후 버튼 활성화 상태 유지

def test_processing_state(window):
    """처리 중 상태 테스트"""
    window.url_input.setText("https://youtube.com/watch?v=test")
    window.dir_input.setText("/test/dir")
    QTest.mouseClick(window.extract_button, Qt.MouseButton.LeftButton)
    
    assert not window.extract_button.isEnabled()
    assert window.cancel_button.isEnabled()
    assert not window.open_output_button.isEnabled()

def test_cancel_processing(window):
    """처리 취소 테스트"""
    window.url_input.setText("https://youtube.com/watch?v=test")
    window.dir_input.setText("/test/dir")
    QTest.mouseClick(window.extract_button, Qt.MouseButton.LeftButton)
    QTest.mouseClick(window.cancel_button, Qt.MouseButton.LeftButton)
    
    assert window.status_label.text() == "취소 중..." 