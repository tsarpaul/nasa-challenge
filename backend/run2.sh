#!/bin/sh

flask run -p5000 -h0.0.0.0 --cert=cert.pem --key=key.pem
