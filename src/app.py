import os
import sys
import logging
import argparse
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from tqdm import tqdm

from content import ImageExtractor, TextExtractor
from processing import Deduplicator, DocumentConverter, TextSummarizer

class YouTubeProcessor:
    """YouTube 비디오 처리 애플리케이션"""
    
    def __init__(
        self,
        output_dir: str,
        config: Optional[Dict] = None
    ):
        self.output_dir = Path(output_dir)
        self.config = config or {}
        
        # 로깅 설정
        self._setup_logging()
        
        # 출력 디렉토리 생성
        self._setup_directories()
        
        # 모듈 초기화
        self._init_modules()
    
    def _setup_logging(self) -> None:
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_directories(self) -> None:
        """디렉토리 구조 설정"""
        self.video_dir = self.output_dir / 'videos'
        self.image_dir = self.output_dir / 'images'
        self.text_dir = self.output_dir / 'texts'
        self.doc_dir = self.output_dir / 'documents'
        
        for directory in [self.video_dir, self.image_dir, self.text_dir, self.doc_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _init_modules(self) -> None:
        """모듈 초기화"""
        # 이미지 추출기
        self.image_extractor = ImageExtractor(
            output_dir=str(self.image_dir),
            quality_threshold=self.config.get('quality_threshold', 0.7),
            interval=self.config.get('interval', 1)
        )
        
        # 텍스트 추출기
        self.text_extractor = TextExtractor(
            output_dir=str(self.text_dir),
            languages=self.config.get('languages', ['ko', 'en'])
        )
        
        # 중복 제거기
        self.deduplicator = Deduplicator(
            similarity_threshold=self.config.get('similarity_threshold', 0.95),
            method=self.config.get('deduplication_method', 'content_hash'),
            cache_size=self.config.get('cache_size', 1000)
        )
        
        # 문서 변환기
        self.document_converter = DocumentConverter(
            output_path=str(self.doc_dir),
            template_path=self.config.get('template_path')
        )
        
        # 텍스트 요약기
        self.text_summarizer = TextSummarizer(
            min_sentence_length=self.config.get('min_sentence_length', 10),
            max_sentence_length=self.config.get('max_sentence_length', 100),
            summary_ratio=self.config.get('summary_ratio', 0.3),
            key_points_count=self.config.get('key_points_count', 5)
        )
    
    def process_video(
        self,
        video_path: str,
        title: str,
        generate_summary: bool = False
    ) -> bool:
        """비디오 처리"""
        try:
            self.logger.info(f"비디오 처리 시작: {video_path}")
            
            # 1. 이미지 추출
            self.logger.info("이미지 추출 중...")
            extracted_images = self.image_extractor.extract_frames(video_path)
            
            # 2. 중복 이미지 제거
            self.logger.info("중복 이미지 제거 중...")
            unique_images, duplicates = self.deduplicator.deduplicate_images(extracted_images)
            
            # 3. 텍스트 추출
            self.logger.info("텍스트 추출 중...")
            extracted_texts = self.text_extractor.extract_text_from_images(unique_images)
            
            # 4. 중복 텍스트 제거
            self.logger.info("중복 텍스트 제거 중...")
            unique_texts, text_duplicates = self.deduplicator.deduplicate_texts(extracted_texts)
            
            # 5. 문서 생성
            self.logger.info("문서 생성 중...")
            doc_success = self.document_converter.create_document(
                title=title,
                images=unique_images,
                texts=unique_texts,
                output_file=f"{title}.docx"
            )
            
            # 6. 요약 문서 생성 (선택 사항)
            if generate_summary and doc_success:
                self.logger.info("요약 문서 생성 중...")
                summary = self.text_summarizer.generate_summary(unique_texts)
                key_points = self.text_summarizer.extract_key_points(unique_texts)
                
                summary_success = self.document_converter.create_summary_document(
                    title=f"{title} - 요약",
                    summary=summary,
                    key_points=key_points,
                    output_file=f"{title}_summary.docx"
                )
            
            self.logger.info("비디오 처리 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"비디오 처리 중 오류 발생: {str(e)}")
            return False

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='YouTube 비디오 처리 애플리케이션')
    parser.add_argument('video_path', help='처리할 비디오 파일 경로')
    parser.add_argument('--output', '-o', default='output', help='출력 디렉토리')
    parser.add_argument('--title', '-t', required=True, help='문서 제목')
    parser.add_argument('--summary', '-s', action='store_true', help='요약 문서 생성')
    
    args = parser.parse_args()
    
    # 애플리케이션 초기화
    processor = YouTubeProcessor(output_dir=args.output)
    
    # 비디오 처리
    success = processor.process_video(
        video_path=args.video_path,
        title=args.title,
        generate_summary=args.summary
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 