#!/bin/bash

#sudo docker container run -ti -v /root/TRANSONIC/user_data/:./user_data/ transonic

sudo docker container run -ti -v ./user_data:/root/TRANSONIC/user_data/ transonic
