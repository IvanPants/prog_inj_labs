#!/bin/bash
HOST=ifconfig.me
PORT=80
CONTEXTPATH=/
exec 3<>/dev/tcp/${HOST}/${PORT}
echo -e "GET ${CONTEXTPATH} HTTP/1.1\r\nHost: ${HOST}:${PORT}\r\nConnection: close\r\n\r\n" >&3
cat <&3
