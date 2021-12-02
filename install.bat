chcp 65001
@echo off
if exist %USERPROFILE%/miniconda3 (
    cls & echo ■■■■■ Miniconda is installed. ■■■■■ & TIMEOUT 3
) else (
    cls & echo ■■■■■ Miniconda is not installed. Will be downloaded shortly. ■■■■■ & TIMEOUT 3
    bitsadmin.exe /transfer "Downloading Miniconda"^
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe^
    %USERPROFILE%/Downloads/Miniconda3-latest-Windows-x86_64.exe
    cls & echo ■■■■■ Miniconda installation will be started. ■■■■■ & TIMEOUT 3
    %USERPROFILE%/Downloads/Miniconda3-latest-Windows-x86_64.exe /S
)
cls & echo ■■■■■ Now to create Python environment and install packages. ■■■■■ & TIMEOUT 3
call %USERPROFILE%/miniconda3/condabin/conda.bat config --add channels conda-forge
call %USERPROFILE%/miniconda3/condabin/conda.bat config --set channel_priority strict
call %USERPROFILE%/miniconda3/condabin/conda.bat create -y -n watercolorize python=3.8 --force
call %USERPROFILE%/miniconda3/condabin/conda.bat activate watercolorize
pip install opencv-python
pip install blend-modes
pip install scikit-image
pip install black
pip install flake8
pip install pep8-naming
pip install flake8-variables-names
pip install flake8-print
pip install flake8-blind-except
pip install flake8-comprehensions
pip install flake8-use-fstring
python ./resource/prepare_coding.py
if %ERRORLEVEL% == 0 (
    cls & echo ■■■■■ Everything is ready. ■■■■■ & TIMEOUT 3
) else (
    cls & echo ■■■■■ A Problem occured. ■■■■■ & TIMEOUT 3
)
pause