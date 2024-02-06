
#!/usr/bin/bash

ROOT_DIR=$(pwd)
ENV_NAME="data_collector_env" 
ENV_PYTHON="$ROOT_DIR/$ENV_NAME/bin/python3"
ENV_PIP="$ROOT_DIR/$ENV_NAME/bin/pip3"

function str_format(){
    printf $*
    #cont=$(str_format "format_str{str:%s,int:%d}" "abcdefg" 99)
}

#-e filename 如果 filename存在，则为真
#-d filename 如果 filename为目录，则为真
#-f filename 如果 filename为常规文件，则为真
#-L filename 如果 filename为符号链接，则为真
#-r filename 如果 filename可读，则为真
#-w filename 如果 filename可写，则为真
#-x filename 如果 filename可执行，则为真
#-s filename 如果文件长度不为0，则为真
#-h filename 如果文件是软链接，则为真

# $# 	传递到脚本或函数的参数个数
# $* 	以一个单字符串显示所有向脚本传递的参数
# $$ 	脚本运行的当前进程ID号
# $! 	后台运行的最后一个进程的ID号
# $@ 	与$*相同，但是使用时加引号，并在引号中返回每个参数。
# $- 	显示Shell使用的当前选项，与set命令功能相同。
# $? 	显示最后命令的退出状态。0表示没有错误，其他任何值表明有错误。

function build() {
    if [[ -d $ENV_NAME ]]
    then
        echo "virtual env has built"
        return 
    fi

    python3 -m venv "$ENV_NAME"
}

function add_lib() {
    $ENV_PIP install "$@"
}
function del_lib(){
    $ENV_PIP uninstall "$@"
}


function execute() {
    $ENV_PYTHON "$@"
}

case $1 in
"build")
    build
    ;;
"add_lib")
    add_lib "${@:2}"
    ;;
"del_lib")
    del_lib "${@:2}"
    ;;
"exec")
    execute "${@:2}"
    ;;
*)
    echo "build_venv.sh build|add_lib|execute"
    ;;
esac