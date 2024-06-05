

# стопаем инстанс под тем же номером, если он есть
echo 'stopping previous...'
docker stop mongo_work
echo "deleting previous..."
docker rm mongo_work


echo "running image..."

docker run -d \
-p 7007:7007 \
--name mongo_work \
mongo_work:"0.2"

#--build-arg http_proxy="${HTTP_PROXY}" \

echo "run.sh is completed successfully!"