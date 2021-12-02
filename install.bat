chcp 65001
@echo off
if exist %USERPROFILE%/miniconda3 (
    cls & echo ■■■■■ Miniconda가 설치되어 있습니다. ■■■■■ & TIMEOUT 3
) else (
    cls & echo ■■■■■ Miniconda가 설치되어 있지 않습니다. 지금 다운로드하겠습니다. ■■■■■ & TIMEOUT 3
    bitsadmin.exe /transfer "Miniconda 다운로드"^
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe^
    %USERPROFILE%/Downloads/Miniconda3-latest-Windows-x86_64.exe
    cls & echo ■■■■■ 이제 Miniconda를 설치하겠습니다. ■■■■■ & TIMEOUT 3
    %USERPROFILE%/Downloads/Miniconda3-latest-Windows-x86_64.exe /S
)
cls & echo ■■■■■ 이제 파이썬 환경을 생성하고 패키지를 설치하겠습니다. ■■■■■ & TIMEOUT 3
call %USERPROFILE%/miniconda3/condabin/conda.bat config --add channels conda-forge
call %USERPROFILE%/miniconda3/condabin/conda.bat config --set channel_priority strict
call %USERPROFILE%/miniconda3/condabin/conda.bat create -y -n watercolorize python=3.8 --force
call %USERPROFILE%/miniconda3/condabin/conda.bat activate watercolorize
pip install opencv-python
pip install black
pip install flake8
pip install pep8-naming
pip install flake8-builtins
pip install flake8-blind-except
python ./prepare_coding.py
if %ERRORLEVEL% == 0 (
    cls & echo ■■■■■ 모든 준비가 끝났습니다. 이제 앱을 사용할 수 있습니다. ■■■■■ & TIMEOUT 3
) else (
    cls & echo ■■■■■ 준비 과정에서 문제가 발생했습니다. ■■■■■ & TIMEOUT 3
)
pause