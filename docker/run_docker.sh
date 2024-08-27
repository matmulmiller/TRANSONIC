#!/bin/bash

TRANSONIC_PATH=~/spades/TRANSONIC

sudo docker container run -ti -v ${TRANSONIC_PATH}/user_data:/root/TRANSONIC/user_data/ transonic
