docker-compose up -d --build --force-recreate
echo ""
echo "-----------------------------------"
echo ""
docker images -a
docker ps
docker volume ls
echo ""
echo "-----------------------------------"
echo ""
docker exec -it $(docker ps -l -q) sh copy.sh
docker exec -it $(docker ps -l -q) sh /bin/bash