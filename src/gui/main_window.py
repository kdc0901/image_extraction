import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLineEdit, QPushButton, QProgressBar, QLabel,
                           QFileDialog, QMessageBox, QCheckBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPalette, QColor
import subprocess
from utils.config import Config
from main import YouTubeProcessor

class ProcessingThread(QThread):
    """동영상 처리 스레드"""
    progress = pyqtSignal(int, str)  # 진행률, 상태 메시지
    finished = pyqtSignal(bool)      # 성공 여부
    
    def __init__(self, url: str, output_dir: str, keep_video: bool):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.keep_video = keep_video
        self._is_cancelled = False
        
    def run(self):
        """스레드 실행"""
        try:
            # 설정 파일 경로
            config_path = 'youtube_config.yaml'
            
            # YouTubeProcessor 인스턴스 생성
            processor = YouTubeProcessor(config_path)
            
            # 진행 상태 콜백 설정
            processor.set_progress_callback(self._update_progress)
            
            # 설정 업데이트
            processor.config.set('output', 'directory', self.output_dir)
            processor.config.set('processing', 'keep_video', self.keep_video)
            processor.config.save()
            
            # 동영상 처리 실행
            result = processor.process_video(self.url)
            
            # 완료 시그널 발생
            self.finished.emit(result)
            
        except Exception as e:
            print(f"처리 중 오류 발생: {str(e)}")
            self.finished.emit(False)
    
    def _update_progress(self, progress: int, message: str) -> bool:
        """진행 상태 업데이트"""
        if self._is_cancelled:
            return False
        self.progress.emit(progress, message)
        return True
        
    def requestInterruption(self):
        """처리 중단 요청"""
        self._is_cancelled = True
        super().requestInterruption()

class MainWindow(QMainWindow):
    """메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # 설정 로드
        self.config = Config('youtube_config.yaml')
        
        # 마지막으로 사용한 디렉토리 복원
        last_dir = self.config.get('output', 'directory', '.')
        self.output_dir_input.setText(last_dir)
        
        # 영상 파일 유지 옵션 복원
        keep_video = self.config.get('processing', 'keep_video', False)
        self.keep_video_checkbox.setChecked(keep_video)
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle('YouTube 동영상 처리')
        self.setGeometry(100, 100, 600, 200)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # URL 입력
        url_layout = QHBoxLayout()
        url_label = QLabel('YouTube URL:')
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # 출력 디렉토리 선택
        dir_layout = QHBoxLayout()
        dir_label = QLabel('저장 위치:')
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setReadOnly(True)
        dir_button = QPushButton('선택...')
        dir_button.clicked.connect(self.select_output_dir)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.output_dir_input)
        dir_layout.addWidget(dir_button)
        layout.addLayout(dir_layout)
        
        # 영상 파일 유지 옵션
        self.keep_video_checkbox = QCheckBox('영상 파일 유지')
        layout.addWidget(self.keep_video_checkbox)
        
        # 추출 버튼과 중단/닫기 버튼을 위한 레이아웃
        button_layout = QHBoxLayout()
        
        # 추출 버튼
        self.extract_button = QPushButton('추출')
        self.extract_button.clicked.connect(self.start_processing)
        button_layout.addWidget(self.extract_button)
        
        # 중단 버튼
        self.stop_button = QPushButton('중단')
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setEnabled(False)  # 초기에는 비활성화
        button_layout.addWidget(self.stop_button)
        
        # 닫기 버튼
        self.close_button = QPushButton('닫기')
        self.close_button.clicked.connect(self.close)
        self.close_button.setEnabled(False)  # 초기에는 비활성화
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # 진행 상태 표시
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel('대기 중...')
        layout.addWidget(self.status_label)
        
    def select_output_dir(self):
        """출력 디렉토리 선택"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            '저장 위치 선택',
            self.output_dir_input.text()
        )
        if dir_path:
            self.output_dir_input.setText(dir_path)
            
    def stop_processing(self):
        """처리 중단"""
        if hasattr(self, 'processing_thread') and self.processing_thread.isRunning():
            # 중단 요청
            self.processing_thread.requestInterruption()
            self.stop_button.setEnabled(False)
            self.status_label.setText('중단 중...')
            
            # UI 활성화
            self.extract_button.setEnabled(True)
            self.url_input.setEnabled(True)
            self.keep_video_checkbox.setEnabled(True)
            self.close_button.setEnabled(True)

    def start_processing(self):
        """처리 시작"""
        # 입력 검증
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText('YouTube URL을 입력하세요.')
            return
            
        output_dir = self.output_dir_input.text()
        if not output_dir:
            self.status_label.setText('저장 위치를 선택하세요.')
            return
            
        # UI 비활성화
        self.extract_button.setEnabled(False)
        self.url_input.setEnabled(False)
        self.keep_video_checkbox.setEnabled(False)
        self.close_button.setEnabled(False)
        
        # 진행 상태 초기화
        self.progress_bar.setValue(0)
        
        # 중단 버튼 활성화
        self.stop_button.setEnabled(True)
        
        # 처리 스레드 시작
        self.processing_thread = ProcessingThread(
            url=url,
            output_dir=output_dir,
            keep_video=self.keep_video_checkbox.isChecked()
        )
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.finished.connect(self.processing_finished)
        self.processing_thread.start()
        
    def update_progress(self, progress: int, message: str):
        """진행 상태 업데이트"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
        
    def processing_finished(self, success: bool):
        """처리 완료"""
        # UI 활성화
        self.extract_button.setEnabled(True)
        self.url_input.setEnabled(True)
        self.keep_video_checkbox.setEnabled(True)
        self.close_button.setEnabled(True)
        
        # 중단 버튼 비활성화
        self.stop_button.setEnabled(False)
        
        if success:
            self.status_label.setText('처리가 완료되었습니다.')
            self.progress_bar.setValue(100)
        else:
            if hasattr(self, 'processing_thread') and self.processing_thread._is_cancelled:
                self.status_label.setText('처리가 중단되었습니다.')
            else:
                self.status_label.setText('처리 중 오류가 발생했습니다.')

    def check_directory_permissions(self, dir_path: str) -> bool:
        """
        디렉토리의 쓰기 권한을 확인합니다.
        
        Args:
            dir_path: 확인할 디렉토리 경로
            
        Returns:
            쓰기 권한이 있으면 True, 없으면 False
        """
        try:
            test_file = os.path.join(dir_path, '.test_write_permission')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except (IOError, OSError):
            return False

    def create_required_directories(self, base_dir: str) -> bool:
        """
        필요한 하위 디렉토리들을 생성합니다.
        
        Args:
            base_dir: 기본 디렉토리 경로
            
        Returns:
            생성 성공 시 True, 실패 시 False
        """
        required_dirs = ['downmovie', 'images', 'texts', 'documents']
        try:
            for dir_name in required_dirs:
                dir_path = os.path.join(base_dir, dir_name)
                os.makedirs(dir_path, exist_ok=True)
            return True
        except OSError as e:
            QMessageBox.critical(self, '오류', f'디렉토리 생성 중 오류가 발생했습니다: {str(e)}')
            return False

    def open_output_directory(self):
        output_dir = self.output_dir_input.text().strip()
        if os.path.exists(output_dir):
            if sys.platform == 'win32':
                os.startfile(output_dir)
            elif sys.platform == 'darwin':
                subprocess.run(['open', output_dir])
            else:
                subprocess.run(['xdg-open', output_dir]) 