chcp 65001
@echo off
call %USERPROFILE%/miniconda3/condabin/conda.bat activate watercolorizer
python ./module/core.py
pause