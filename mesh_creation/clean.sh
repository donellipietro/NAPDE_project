docker-compose down
docker rmi mesh_creation-all
yes | docker volume prune 
rm -r results
clear
echo ""
echo "-- Images --------------------------------------------------------------------------"
echo ""
docker images -a
echo ""
echo "-- Containers -----------------------------------------------------------------------"
echo ""
docker ps
echo ""
echo "-- Compose --------------------------------------------------------------------------"
echo ""
docker-compose ls
echo ""
echo "-- Volumes --------------------------------------------------------------------------"
echo ""
docker volume ls
echo ""
echo "-------------------------------------------------------------------------------------"
echo ""

