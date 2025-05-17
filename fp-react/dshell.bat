@ECHO OFF
for /F %%A in ('docker ps -q') DO docker exec -it %%A /bin/bash
