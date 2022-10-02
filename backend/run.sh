#!/bin/sh

flask run -p443 -h0.0.0.0 --cert=cert.pem --key=key.pem
