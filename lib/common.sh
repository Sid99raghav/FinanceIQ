#!/usr/bin/bash
#################################################
#################################################

function die () {
    echo "FATAL ERROR":"$1"
    exit 1
}

function log_time() {
    echo "Timestamp: $(date --utc +%Z_%y%m%d_%H:%M:%S)"
}

function execute_cmd() {
    cmd=$@
    ret=`eval ${cmd} 2>&1`
    errCode=$?
}

function win2dospath()
{
    path=`/bin/cygpath -d $1`
}

function get_current_pwd_path
{
    current_path=$PWD
    # if is_windows is set to 1
    # then convert the path to windows

    if [[ "$IS_WINDOWS" == "1" ]]; then
        win2dospath $PWD
	    current_path=$path
    fi
}

function run_cmd_in_docker()
{
    cmd=$@
    if [ -z "$DOCKER_NAME" ]; then
        DOCKER_NAME=propmart
    fi
    if [ -z "$USER_NAME" ]; then
        USER_NAME=${USER}
    fi
    if [ -z "$DOCKER_PORT" ]; then
        DOCKER_PORT=8000
    fi
    ret=0
    ret=0
    log_time

    docker_option="-d"
    SUDO="sudo"
    if [[ "$IS_WINDOWS" == "1" ]]; then
        docker_option="-d"
	SUDO=""
    fi

    echo "> Building Docker image ...[${DOCKER_IMAGE}]"
    $SUDO docker build -t $DOCKER_IMAGE ./docker
    # https://stackoverflow.com/questions/71620812/uvicorn-wont-quit-with-ctrlc
    $SUDO docker rm -f $DOCKER_NAME 2> /dev/null
    log_time
    # Get current pwd, for windows windows path is required
    get_current_pwd_path
    docker_option="-it"
    if [ "$LAB_MODE" = "1" ];
    then
        DOCKER_OPT_PORT_80="-p 80:80"
    else
        DOCKER_OPT_PORT_80=""
    fi

    # run docker in disconnected mode    
    dcmd="$SUDO docker run $opt --rm \
        $docker_option \
        -v \"$current_path\":/home \
        -u $(id -u ${USER_NAME}):$(id -g ${USER_NAME}) \
        --name $DOCKER_NAME \
	    -p $DOCKER_PORT:$DOCKER_PORT\
        $DOCKER_OPT_PORT_80\
        $DOCKER_IMAGE\
        bash -c \"$cmd\""

    # Run docker web
    echo $dcmd
    out=`eval "$dcmd 2>&1"` || echo "Failed to start docker. err: $out"
}
