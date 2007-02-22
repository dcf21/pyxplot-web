#!/bin/bash

export TRAC_ENV="/societies/pyxplot/projectenv"
if [[ -z $REMOTE_USER && -n $REDIRECT_REMOTE_USER ]] 
	then export REMOTE_USER=$REDIRECT_REMOTE_USER
fi
exec /usr/share/trac/cgi-bin/trac.cgi
