@echo off
PATH = %PATH%;%USERPROFILE%\Miniconda3\Scripts
call activate question-dependence

IF ["%~1"] == [""] (
  cmd /k
) ELSE (
  IF NOT ["%~1"] == ["setenv"] (
    start "" "%~1"
  )
)
