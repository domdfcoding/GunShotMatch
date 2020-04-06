#!/bin/bash

# Perform cleanup after non-graceful shutdown

kill -9 "$(cat /home/$USER/.config/GunShotMatch/.pid/GunShotMatch.pid)"
rm /home/$USER/.config/GunShotMatch/.pid/GunShotMatch.pid

kill -9 "$(cat /home/$USER/.config/GunShotMatch/.pid/DataViewer.pid)"
rm /home/$USER/.config/GunShotMatch/.pid/DataViewer.pid


docker stop pyms-nist-server
docker container rm pyms-nist-server
docker system prune