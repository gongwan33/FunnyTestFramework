OLD_CONTAINER=$(docker ps -a | grep "gongwan33/etkaseleniumspider" | awk '{print $1;}')
if [ "$OLD_CONTAINER" != "" ]; then
    docker rm $OLD_CONTAINER
    echo $OLD_CONTAINER removed
fi
docker run --net=host -v $(pwd)/../:/root/FunnyTestFrameWork -v /dev/shm:/dev/shm -v ~/.ssh:/root/.ssh -v ~/.git:/root/.git -v ~/.gitconfig:/root/.gitconfig -it gongwan33/etkaseleniumspider:v0.4 

