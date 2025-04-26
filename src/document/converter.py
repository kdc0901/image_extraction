"""
문서 변환 모듈
"""

import os
from pathlib import Path
from typing import List, Optional
import logging
from docx import Document
from docx.shared import Inches, Pt

class DocumentConverter:
    """문서 변환 클래스"""
    
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
        
    def create_document(self, text: str, output_file: Optional[str] = None) -> bool:
        """
        텍스트로 문서 생성
        
        Args:
            text: 문서에 포함할 텍스트
            output_file: 출력 파일 경로 (선택)
            
        Returns:
            성공 여부
        """
        try:
            # 문서 객체 생성
            doc = Document()
            
            # 제목 추가
            doc.add_heading('추출된 텍스트', 0)
            
            # 텍스트 추가
            doc.add_paragraph(text)
            
            # 출력 파일 경로 설정
            if output_file is None:
                output_file = self.output_dir / 'extracted_text.docx'
            
            # 문서 저장
            doc.save(str(output_file))
            
            self.logger.info(f"문서 생성 완료: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"문서 생성 중 오류 발생: {str(e)}")
            return False 