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
        
    def extract_text(self, image_path: str) -> str:
        """
        이미지에서 텍스트 추출
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            추출된 텍스트
        """
        try:
            # 이미지 로드
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"이미지를 로드할 수 없음: {image_path}")
                return ""
            
            # 이미지 전처리
            processed = self.preprocess_image(image)
            
            # OCR 수행
            text = pytesseract.image_to_string(processed)
            
            # 언어 감지
            try:
                lang = detect(text)
                if lang not in ['ko', 'en']:
                    self.logger.warning(f"지원되지 않는 언어 감지: {lang}")
            except:
                self.logger.warning("언어 감지 실패")
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"텍스트 추출 중 오류 발생: {e}")
            return ""
            
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