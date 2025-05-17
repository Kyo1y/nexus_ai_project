@ECHO OFF
for /F %%A in ('docker ps -q') DO docker kill %%A
