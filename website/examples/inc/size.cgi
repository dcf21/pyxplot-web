#!/bin/bash

# Get the size of a file

/bin/echo "content-type: text/html"
/bin/echo

/bin/ls -lh $REDIRECT_file | awk '{print $5;}'
