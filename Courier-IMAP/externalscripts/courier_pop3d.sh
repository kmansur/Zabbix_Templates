#!/bin/sh

TIME="`date -j -v-1M | awk -F : '{print $1":"$2}' | awk '{print $4}'`"

grep LOGIN /var/log/maillog | grep $TIME | grep pop3d | wc -l
