#!/usr/bin/env bash

docker rmi --force cyberchuvash/discountposter:master
docker pull cyberchuvash/discountposter:master
docker stop discount
docker rm discount
docker run -d --name discount \
--restart unless-stopped \
-e VK_LOGIN="" \
-e VK_PASS="" \
-e VK_APP_ID="" \
-e VK_GROUP_ID="" \
-e MYSQL_HOST="" \
-e MYSQL_LOGIN="" \
-e MYSQL_PASS="" \
-e MYSQL_DB="" \
-e POST_PHOTO="1" \
-e ATTACH_LINK="1" \
-e JOB_INTERVAL_SEC="10" \
-e LOG_LEVEL="INFO" \
cyberchuvash/discountposter:master
