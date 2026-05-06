#!/bin/sh

MAILLOG="${COURIER_MAILLOG:-/var/log/maillog}"
TIME="$(date -j -v-1M '+%H:%M')"

grep 'LOGIN' "$MAILLOG" | grep "$TIME" | grep 'imapd' | grep -v 'imapd-ssl' | wc -l
