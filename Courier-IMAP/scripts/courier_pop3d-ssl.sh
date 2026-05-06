#!/bin/sh

MAILLOG="${COURIER_MAILLOG:-/var/log/maillog}"
TIME="$(date -j -v-1M '+%H:%M')"

grep 'LOGIN' "$MAILLOG" | grep "$TIME" | grep 'pop3d-ssl' | wc -l
