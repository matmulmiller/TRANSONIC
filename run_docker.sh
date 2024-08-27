#!/bin/bash

sudo docker container run -ti --rm -v ./user_data/ -w /root/TRANSONIC/user_data/ transonic
