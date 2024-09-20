#!/bin/bash

TRANSONIC_PATH=~/spades/TRANSONIC

sudo docker container run -ti -v ${TRANSONIC_PATH}/user_data:/root/TRANSONIC/user_data/ -v "${HOME}/.Xauthority":"/root/.Xauthority:ro" -e "DISPLAY=$DISPLAY" --network host transonic
