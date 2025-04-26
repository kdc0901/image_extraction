"""
설정 파일 관리 모듈
"""

import os
import yaml
from typing import Any, Dict, Optional

class Config:
    """설정 파일 관리 클래스"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        초기화 함수
        
        Args:
            config_path (str): 설정 파일 경로
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """설정 파일 로드"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            else:
                self.config = {}
        except Exception as e:
            print(f"설정 파일 로드 중 오류 발생: {e}")
            self.config = {}
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        설정값 조회
        
        Args:
            section (str): 섹션 이름
            key (str): 키 이름
            default (Any): 기본값
            
        Returns:
            Any: 설정값
        """
        try:
            return self.config.get(section, {}).get(key, default)
        except Exception:
            return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        설정값 저장
        
        Args:
            section (str): 섹션 이름
            key (str): 키 이름
            value (Any): 설정값
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def save(self) -> bool:
        """
        설정 파일 저장
        
        Returns:
            bool: 성공 여부
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True)
            return True
        except Exception as e:
            print(f"설정 파일 저장 중 오류 발생: {e}")
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        섹션 전체 설정 조회
        
        Args:
            section (str): 섹션 이름
            
        Returns:
            Dict[str, Any]: 섹션 설정
        """
        return self.config.get(section, {})
    
    def set_section(self, section: str, values: Dict[str, Any]) -> None:
        """
        섹션 전체 설정 저장
        
        Args:
            section (str): 섹션 이름
            values (Dict[str, Any]): 섹션 설정
        """
        self.config[section] = values 