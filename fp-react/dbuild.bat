@echo off
IF "%~1" == "cache" (
echo Using Docker Cache
docker build -t chatquote:latest --pull --target server .
) ELSE (
echo Not using Docker Cache
docker build --no-cache -t chatquote:latest --pull --target server .
)
