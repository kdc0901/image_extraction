import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLineEdit, QPushButton, QProgressBar, QLabel,
                           QFileDialog, QMessageBox, QCheckBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPalette, QColor
import subprocess
from src.utils.config import Config
from src.main import YouTubeProcessor

class ProcessingThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, url, output_dir, keep_video=False):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.keep_video = keep_video
        self._is_cancelled = False

    def run(self):
        try:
            # 설정 파일 생성
            config = Config('youtube_config.yaml')
            config.set('output', 'directory', self.output_dir)
            config.set('processing', 'keep_video', self.keep_video)
            config.save()
            
            processor = YouTubeProcessor('youtube_config.yaml')
            processor.set_progress_callback(self.update_progress)
            if not self._is_cancelled:
                result = processor.process_video(self.url)
                if result:
                    self.finished.emit(True, "처리가 완료되었습니다.")
                else:
                    self.finished.emit(False, "처리 중 오류가 발생했습니다.")
        except Exception as e:
            self.finished.emit(False, str(e))

    def update_progress(self, progress: int, message: str) -> bool:
        if self._is_cancelled:
            return False
        self.progress.emit(progress)
        self.status.emit(message)
        return True

    def cancel(self):
        self._is_cancelled = True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.processing_thread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube 이미지 추출기')
        self.setGeometry(100, 100, 600, 400)

        # 메인 위젯과 레이아웃
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # URL 입력
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('YouTube URL을 입력하세요')
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # 출력 디렉토리 선택
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText('출력 디렉토리를 선택하세요')
        self.dir_input.setText(self.config.get('gui', 'last_output_dir', ''))
        dir_layout.addWidget(self.dir_input)
        self.dir_button = QPushButton('디렉토리 선택')
        self.dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_button)
        layout.addLayout(dir_layout)

        # 옵션 설정
        options_layout = QHBoxLayout()
        self.keep_video_checkbox = QCheckBox('영상 파일 유지')
        self.keep_video_checkbox.setChecked(self.config.get('gui', 'keep_video', False))
        options_layout.addWidget(self.keep_video_checkbox)
        options_layout.addStretch()
        layout.addLayout(options_layout)

        # 처리 버튼들
        button_layout = QHBoxLayout()
        self.extract_button = QPushButton('추출 시작')
        self.extract_button.clicked.connect(self.start_processing)
        button_layout.addWidget(self.extract_button)

        self.cancel_button = QPushButton('취소')
        self.cancel_button.clicked.connect(self.cancel_processing)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)

        self.open_output_button = QPushButton('출력 폴더 열기')
        self.open_output_button.clicked.connect(self.open_output_directory)
        self.open_output_button.setEnabled(False)
        button_layout.addWidget(self.open_output_button)
        layout.addLayout(button_layout)

        # 진행 상태 표시
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel('준비됨')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, '출력 디렉토리 선택')
        if dir_path:
            self.dir_input.setText(dir_path)
            self.config.set('gui', 'last_output_dir', dir_path)
            self.config.save()

    def start_processing(self):
        url = self.url_input.text().strip()
        output_dir = self.dir_input.text().strip()
        keep_video = self.keep_video_checkbox.isChecked()

        if not url:
            QMessageBox.warning(self, '경고', 'YouTube URL을 입력해주세요.')
            return
        if not output_dir:
            QMessageBox.warning(self, '경고', '출력 디렉토리를 선택해주세요.')
            return

        # 설정 저장
        self.config.set('gui', 'keep_video', keep_video)
        self.config.save()

        self.processing_thread = ProcessingThread(url, output_dir, keep_video)
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.status.connect(self.update_status)
        self.processing_thread.finished.connect(self.processing_finished)

        self.extract_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.open_output_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.processing_thread.start()

    def cancel_processing(self):
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.cancel()
            self.status_label.setText('취소 중...')

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, message):
        self.status_label.setText(message)

    def processing_finished(self, success, message):
        self.extract_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.open_output_button.setEnabled(True)
        
        if success:
            QMessageBox.information(self, '완료', message)
        else:
            QMessageBox.critical(self, '오류', f'처리 중 오류가 발생했습니다: {message}')

    def open_output_directory(self):
        output_dir = self.dir_input.text().strip()
        if os.path.exists(output_dir):
            if sys.platform == 'win32':
                os.startfile(output_dir)
            elif sys.platform == 'darwin':
                subprocess.run(['open', output_dir])
            else:
                subprocess.run(['xdg-open', output_dir]) 