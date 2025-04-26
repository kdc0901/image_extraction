from setuptools import setup, find_namespace_packages

setup(
    name="youtube-video-processor",
    version="0.1.0",
    packages=find_namespace_packages(include=['src*']),
    package_dir={'': '.'},
    install_requires=[
        'opencv-python',
        'numpy',
        'python-docx',
        'pytesseract',
        'langdetect',
    ],
    python_requires='>=3.8',
) 