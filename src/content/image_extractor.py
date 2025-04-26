"""
Image extraction module.
"""

import os
import cv2
import numpy as np
from typing import List, Optional, Tuple
from PIL import Image
import logging
from tqdm import tqdm
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class ImageExtractor:
    """이미지 추출 클래스"""
    
    def __init__(self, output_dir: str, frame_interval: int = 1, slide_threshold: float = 0.95):
        """
        초기화
        
        Args:
            output_dir: 이미지 저장 디렉토리
            frame_interval: 프레임 추출 간격 (초)
            slide_threshold: 슬라이드 변경 감지 임계값
        """
        self.output_dir = Path(output_dir)
        self.frame_interval = frame_interval
        self.slide_threshold = slide_threshold
        self.logger = logging.getLogger(__name__)
        
        # 출력 디렉토리 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_frames(self, video_path: str) -> Optional[List[str]]:
        """
        비디오에서 프레임 추출
        
        Args:
            video_path: 비디오 파일 경로
            
        Returns:
            추출된 이미지 파일 경로 목록 또는 None
        """
        try:
            self.logger.info(f"비디오 파일에서 프레임 추출 시작: {video_path}")
            
            if not os.path.exists(video_path):
                self.logger.error(f"비디오 파일이 존재하지 않습니다: {video_path}")
                return None

            # 비디오 캡처 객체 생성
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                self.logger.error(f"비디오 파일을 열 수 없습니다: {video_path}")
                return None

            # 비디오 정보
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_interval_count = int(fps * self.frame_interval)

            extracted_images = []
            prev_frame = None
            frame_count = 0
            
            # 진행률 표시
            with tqdm(total=total_frames, desc="프레임 추출") as pbar:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # 프레임 간격마다 처리
                    if frame_count % frame_interval_count == 0:
                        try:
                            # 이전 프레임과 비교
                            if prev_frame is not None:
                                similarity = self._compare_frames(prev_frame, frame)
                                if similarity > self.slide_threshold:
                                    frame_count += 1
                                    pbar.update(1)
                                    continue

                            # 이미지 저장
                            image_path = self.output_dir / f"image_{frame_count}.jpg"
                            cv2.imwrite(str(image_path), frame)
                            extracted_images.append(str(image_path))
                            prev_frame = frame.copy()

                        except Exception as e:
                            self.logger.warning(f"프레임 {frame_count} 처리 중 오류 발생: {str(e)}")

                    frame_count += 1
                    pbar.update(1)

            cap.release()
            
            if not extracted_images:
                self.logger.warning("추출된 이미지가 없습니다.")
                return None

            self.logger.info(f"프레임 추출 완료. 총 {len(extracted_images)}개의 이미지 추출됨")
            return extracted_images

        except Exception as e:
            self.logger.error(f"프레임 추출 중 오류 발생: {str(e)}")
            return None
            
    def _compare_frames(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        두 프레임의 유사도 비교
        
        Args:
            frame1: 첫 번째 프레임
            frame2: 두 번째 프레임
            
        Returns:
            유사도 (0~1)
        """
        try:
            # 그레이스케일 변환
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # 히스토그램 계산
            hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
            
            # 히스토그램 정규화
            cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
            cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)
            
            # 히스토그램 비교
            similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            return similarity
            
        except Exception as e:
            self.logger.error(f"프레임 비교 중 오류 발생: {str(e)}")
            return 0.0
            
    def extract_slides(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        프레임에서 슬라이드 추출
        
        Args:
            frames: 프레임 목록
            
        Returns:
            추출된 슬라이드 목록
        """
        try:
            if not frames:
                return []
            
            slides = []
            prev_frame = None
            min_frame_gap = 10  # 최소 프레임 간격
            frame_counter = 0
            
            for frame in frames:
                if prev_frame is None:
                    # 첫 프레임은 항상 포함
                    slides.append(frame)
                    prev_frame = frame
                    continue
                
                frame_counter += 1
                
                # 최소 프레임 간격을 넘었을 때만 유사도 검사
                if frame_counter >= min_frame_gap:
                    # 이전 프레임과 유사도 계산
                    similarity = self.calculate_similarity(prev_frame, frame)
                    
                    # 품질 검사
                    quality = self.calculate_quality(frame)
                    
                    # 유사도가 임계값보다 낮고 품질이 기준 이상이면 새로운 슬라이드로 판단
                    if similarity < self.slide_threshold and quality > 0.2:
                        # 이전 슬라이드와 충분히 다른지 추가 검사
                        is_unique = True
                        for existing_slide in slides[-3:]:  # 최근 3개 슬라이드와 비교
                            if self.calculate_similarity(existing_slide, frame) > 0.85:
                                is_unique = False
                                break
                        
                        if is_unique:
                            slides.append(frame)
                            prev_frame = frame
                            frame_counter = 0
                
            self.logger.info(f"총 프레임 수: {len(frames)}, 추출된 슬라이드 수: {len(slides)}")
            return slides
            
        except Exception as e:
            self.logger.error(f"슬라이드 추출 중 오류 발생: {e}")
            return []
            
    def calculate_similarity(self, frame1: np.ndarray,
                           frame2: np.ndarray) -> float:
        """
        프레임 간 유사도 계산
        
        Args:
            frame1: 첫 번째 프레임
            frame2: 두 번째 프레임
            
        Returns:
            구조적 유사도
        """
        try:
            # 그레이스케일 변환
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # 구조적 유사도 계산
            similarity = cv2.matchTemplate(
                gray1, gray2, cv2.TM_CCOEFF_NORMED
            )[0][0]
            
            return float(similarity)
            
        except Exception as e:
            self.logger.error(f"유사도 계산 중 오류 발생: {e}")
            return 0.0
            
    def calculate_quality(self, image: np.ndarray) -> float:
        """
        이미지 품질 계산
        
        Args:
            image: OpenCV 이미지
            
        Returns:
            품질 점수 (0.0 ~ 1.0)
        """
        try:
            # 그레이스케일 변환
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 라플라시안 필터 적용
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            
            # 분산 계산
            variance = laplacian.var()
            
            # 정규화 (0.0 ~ 1.0)
            quality = min(1.0, variance / 1000.0)
            
            return quality
            
        except Exception as e:
            self.logger.error(f"품질 계산 중 오류 발생: {e}")
            return 0.0
            
    def save_image(self, image: np.ndarray,
                  output_file: Optional[str] = None) -> str:
        """
        이미지 저장
        
        Args:
            image: OpenCV 이미지
            output_file: 출력 파일 경로 (선택)
            
        Returns:
            저장된 파일 경로
        """
        try:
            # 출력 파일 경로 설정
            if output_file is None:
                output_file = self.output_dir / f"image_{len(os.listdir(self.output_dir))}.jpg"
            
            # 이미지 저장
            cv2.imwrite(str(output_file), image)
            
            self.logger.info(f"이미지 저장 완료: {output_file}")
            return str(output_file)
            
        except Exception as e:
            self.logger.error(f"이미지 저장 중 오류 발생: {e}")
            raise 