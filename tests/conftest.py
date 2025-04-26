import os
import pytest
import logging
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """테스트 데이터 디렉토리"""
    return Path(__file__).parent / "test_data"

@pytest.fixture(scope="session")
def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('tests/test.log'),
            logging.StreamHandler()
        ]
    )

@pytest.fixture(autouse=True)
def setup_test_env(tmp_path):
    """테스트 환경 설정"""
    # 테스트용 임시 디렉토리 생성
    os.makedirs(tmp_path / "output", exist_ok=True)
    os.makedirs(tmp_path / "images", exist_ok=True)
    os.makedirs(tmp_path / "texts", exist_ok=True)
    os.makedirs(tmp_path / "documents", exist_ok=True)
    
    # 환경 변수 설정
    os.environ["TEST_MODE"] = "true"
    
    yield
    
    # 테스트 후 정리
    if os.path.exists("tests/test.log"):
        os.remove("tests/test.log") 