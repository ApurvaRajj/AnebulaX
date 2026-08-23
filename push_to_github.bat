@echo off
set REPO_NAME=%1
if "%REPO_NAME%"=="" set REPO_NAME=nebula-v9

echo Configuring remote for https://github.com/ApurvaRajj/%REPO_NAME%.git ...
git remote remove origin 2>nul
git remote add origin https://github.com/ApurvaRajj/%REPO_NAME%.git
git branch -M main

echo Pushing to GitHub...
git push -u origin main

echo Done!
