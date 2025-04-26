"""
텍스트 추출 모듈
"""

import os
from pathlib import Path
from typing import List, Optional
import logging
import cv2
import pytesseract
from langdetect import detect

class TextExtractor:
    """텍스트 추출 클래스"""
    
    def __init__(self, output_dir: str):
        """
        초기화
        
        Args:
            output_dir: 출력 디렉토리
        """
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        
        # 출력 디렉토리 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def preprocess_image(self, image):
        """
        이미지 전처리
        
        Args:
            image: OpenCV 이미지
            
        Returns:
            전처리된 이미지
        """
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 노이즈 제거
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # 이진화
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
        
    def extract_text(self, video_path: str) -> Optional[List[str]]:
        """
        비디오에서 텍스트 추출
        
        Args:
            video_path: 비디오 파일 경로
            
        Returns:
            추출된 텍스트 목록 또는 None
        """
        try:
            self.logger.info(f"비디오 파일에서 텍스트 추출 시작: {video_path}")
            
            if not os.path.exists(video_path):
                self.logger.error(f"비디오 파일이 존재하지 않습니다: {video_path}")
                return None

            # 비디오 캡처 객체 생성
            cap = cv2.VideoCapture(str(video_path))  # 문자열로 변환하여 전달
            if not cap.isOpened():
                self.logger.error(f"비디오 파일을 열 수 없습니다: {video_path}")
                return None

            extracted_texts = []
            frame_count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # 5프레임마다 텍스트 추출 (성능 최적화)
                if frame_count % 5 == 0:
                    try:
                        # 프레임 전처리
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        # 노이즈 제거
                        denoised = cv2.fastNlMeansDenoising(gray)
                        # 이진화
                        _, binary = cv2.threshold(denoised, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                        
                        # OCR 수행
                        text = pytesseract.image_to_string(binary, lang='kor+eng')
                        if text.strip():  # 빈 텍스트가 아닌 경우만 저장
                            extracted_texts.append(text.strip())
                            
                            # 텍스트 파일로 저장
                            text_file = self.output_dir / f"text_{frame_count}.txt"
                            with open(text_file, "w", encoding="utf-8") as f:
                                f.write(text)
                    except Exception as e:
                        self.logger.warning(f"프레임 {frame_count} 처리 중 오류 발생: {str(e)}")
                        continue

                frame_count += 1

            cap.release()
            
            if not extracted_texts:
                self.logger.warning("추출된 텍스트가 없습니다.")
                return None

            self.logger.info(f"텍스트 추출 완료. 총 {len(extracted_texts)}개의 텍스트 추출됨")
            return extracted_texts

        except Exception as e:
            self.logger.error(f"텍스트 추출 중 오류 발생: {str(e)}")
            return None
            
    def extract_texts(self, image_paths: List[str]) -> List[str]:
        """
        여러 이미지에서 텍스트 추출
        
        Args:
            image_paths: 이미지 파일 경로 목록
            
        Returns:
            추출된 텍스트 목록
        """
        texts = []
        for image_path in image_paths:
            text = self.extract_text(image_path)
            texts.append(text)
        return texts
        
    def save_text(self, text: str, output_file: Optional[str] = None) -> str:
        """
        텍스트 저장
        
        Args:
            text: 저장할 텍스트
            output_file: 출력 파일 경로 (선택)
            
        Returns:
            저장된 파일 경로
        """
        try:
            # 출력 파일 경로 설정
            if output_file is None:
                output_file = self.output_dir / f"text_{len(os.listdir(self.output_dir))}.txt"
            
            # 텍스트 저장
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
                
            self.logger.info(f"텍스트 저장 완료: {output_file}")
            return str(output_file)
            
        except Exception as e:
            self.logger.error(f"텍스트 저장 중 오류 발생: {e}")
            raise 