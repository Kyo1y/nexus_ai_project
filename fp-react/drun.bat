@echo off
IF "%~1" == "shell" (
echo Starting command shell
docker run --rm -it --entrypoint bash chatquote
) ELSE (
docker run -p 3000:3000 -e DEMO_SECRET_PASSWORD=1234 chatquote
)
