import os
import pytest
import numpy as np
import cv2
from pathlib import Path
from src.content.image_extractor import ImageExtractor
from src.content.text_extractor import TextExtractor
from src.processing.deduplicator import Deduplicator
from src.processing.summarizer import TextSummarizer
from src.processing.converter import DocumentConverter

class TestIntegration:
    """통합 테스트"""
    
    @pytest.fixture
    def setup_components(self, tmp_path):
        """테스트 컴포넌트 설정"""
        # 출력 디렉토리 생성
        output_dir = tmp_path / "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 컴포넌트 초기화
        image_extractor = ImageExtractor(
            output_dir=str(output_dir / "images"),
            min_quality=0.7,
            interval=1.0
        )
        
        text_extractor = TextExtractor(
            output_dir=str(output_dir / "texts"),
            languages=['ko', 'en']
        )
        
        deduplicator = Deduplicator(
            similarity_threshold=0.95,
            method='content_hash',
            cache_size=1000
        )
        
        summarizer = TextSummarizer(
            min_sentence_length=5,
            max_sentence_length=200,
            summary_ratio=0.3,
            key_points_count=3
        )
        
        converter = DocumentConverter(
            output_path=str(output_dir / "documents")
        )
        
        return {
            'image_extractor': image_extractor,
            'text_extractor': text_extractor,
            'deduplicator': deduplicator,
            'summarizer': summarizer,
            'converter': converter,
            'output_dir': output_dir
        }
    
    @pytest.fixture
    def sample_video(self, tmp_path):
        """테스트용 샘플 비디오 생성"""
        # 간단한 비디오 생성
        video_path = tmp_path / "test_video.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(video_path), fourcc, 20.0, (640, 480))
        
        for i in range(30):  # 1.5초 분량
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, f"Frame {i}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            out.write(frame)
        
        out.release()
        return str(video_path)
    
    def test_full_pipeline(self, setup_components, sample_video):
        """전체 파이프라인 테스트"""
        components = setup_components
        
        # 1. 이미지 추출
        images = components['image_extractor'].extract_frames(
            video_path=sample_video,
            interval=1.0
        )
        assert len(images) > 0
        
        # 2. 중복 이미지 제거
        unique_images, duplicates = components['deduplicator'].deduplicate_images(images)
        assert len(unique_images) > 0
        
        # 3. 텍스트 추출
        texts = []
        for image_path in unique_images:
            text = components['text_extractor'].extract_text_from_image(image_path)
            if text:
                texts.append(text)
        assert len(texts) > 0
        
        # 4. 중복 텍스트 제거
        unique_texts, duplicates = components['deduplicator'].deduplicate_texts(texts)
        assert len(unique_texts) > 0
        
        # 5. 텍스트 요약
        summary = components['summarizer'].generate_summary(unique_texts)
        assert summary
        
        # 6. 핵심 포인트 추출
        key_points = components['summarizer'].extract_key_points(unique_texts)
        assert len(key_points) > 0
        
        # 7. 문서 생성
        success = components['converter'].create_document(
            title="테스트 문서",
            images=unique_images,
            texts=unique_texts,
            output_file="test.docx"
        )
        assert success
        
        # 8. 요약 문서 생성
        success = components['converter'].create_summary_document(
            title="테스트 요약",
            summary=summary,
            key_points=key_points,
            output_file="summary.docx"
        )
        assert success
        
        # 9. 생성된 파일 확인
        assert (components['output_dir'] / "documents" / "test.docx").exists()
        assert (components['output_dir'] / "documents" / "summary.docx").exists()
    
    def test_error_handling(self, setup_components):
        """오류 처리 테스트"""
        components = setup_components
        
        # 존재하지 않는 비디오 파일
        with pytest.raises(Exception):
            components['image_extractor'].extract_frames(
                video_path="nonexistent.mp4",
                interval=1.0
            )
        
        # 빈 이미지 리스트
        unique_images, duplicates = components['deduplicator'].deduplicate_images([])
        assert len(unique_images) == 0
        
        # 빈 텍스트 리스트
        summary = components['summarizer'].generate_summary([])
        assert summary == ""
        
        # 잘못된 문서 생성 파라미터
        success = components['converter'].create_document(
            title="",
            images=[],
            texts=[],
            output_file=""
        )
        assert not success 