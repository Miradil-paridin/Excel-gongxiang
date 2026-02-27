#!/bin/bash

# Excel共享系统快速启动脚本

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Excel共享系统 - 快速启动${NC}"
echo "=========================================="

BACKEND_PID=""
FRONTEND_PID=""
BACKEND_STARTED=0
FRONTEND_STARTED=0
OFFLINE_MODE="${OFFLINE:-0}"
SKIP_PIP_INSTALL="${SKIP_PIP_INSTALL:-0}"
SKIP_MIGRATE="${SKIP_MIGRATE:-0}"
SKIP_CREATE_TEST_USERS="${SKIP_CREATE_TEST_USERS:-0}"

cleanup() {
    trap - INT TERM EXIT
    echo ""
    echo -e "${YELLOW}正在停止服务并清理端口...${NC}"

    if [ "$FRONTEND_STARTED" -eq 1 ] && [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
        kill "$FRONTEND_PID" >/dev/null 2>&1 || true
        wait "$FRONTEND_PID" 2>/dev/null || true
    fi

    if [ "$BACKEND_STARTED" -eq 1 ] && [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
        kill "$BACKEND_PID" >/dev/null 2>&1 || true
        wait "$BACKEND_PID" 2>/dev/null || true
    fi

    # 兜底清理，避免子进程残留占用端口
    if [ "$FRONTEND_STARTED" -eq 1 ]; then
        lsof -tiTCP:3000 -sTCP:LISTEN | xargs kill >/dev/null 2>&1 || true
    fi
    if [ "$BACKEND_STARTED" -eq 1 ]; then
        lsof -tiTCP:8000 -sTCP:LISTEN | xargs kill >/dev/null 2>&1 || true
    fi

    echo -e "${GREEN}服务已停止。${NC}"
}

trap cleanup INT TERM EXIT

check_port_in_use() {
    local port=$1
    if lsof -iTCP:"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

wait_for_backend_ready() {
    local max_attempts=20
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -m 2 -w "%{http_code}" http://127.0.0.1:8000/admin/login/ | grep -Eq "200|302"; then
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    return 1
}

is_onlyoffice_ready() {
    [ "$(curl -s -m 2 http://127.0.0.1:8081/healthcheck)" = "true" ]
}

try_start_onlyoffice() {
    if is_onlyoffice_ready; then
        echo -e "${GREEN}✅ OnlyOffice 已就绪 (http://localhost:8081)${NC}"
        return 0
    fi

    echo -e "${YELLOW}⚠️  OnlyOffice 当前未就绪，在线编辑功能不可用。${NC}"

    if [ ! -f "docker/start-onlyoffice.sh" ]; then
        echo -e "${YELLOW}ℹ️  未找到 docker/start-onlyoffice.sh，跳过自动启动。${NC}"
        return 0
    fi

    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${YELLOW}ℹ️  未检测到 Docker，跳过自动启动 OnlyOffice。${NC}"
        return 0
    fi

    read -p "是否尝试自动启动 OnlyOffice? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        (cd docker && ./start-onlyoffice.sh)
        if is_onlyoffice_ready; then
            echo -e "${GREEN}✅ OnlyOffice 启动成功。${NC}"
        else
            echo -e "${YELLOW}⚠️  OnlyOffice 仍未就绪，请手动检查: cd docker && ./start-onlyoffice.sh${NC}"
        fi
    fi
}

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
echo "1. 激活虚拟环境..."
source venv/bin/activate
VENV_PYTHON="$(pwd)/venv/bin/python"

# 检查依赖
echo "2. 检查后端依赖..."
if [ "$OFFLINE_MODE" = "1" ] || [ "$SKIP_PIP_INSTALL" = "1" ]; then
    echo "   已跳过 pip 安装 (OFFLINE=$OFFLINE_MODE, SKIP_PIP_INSTALL=$SKIP_PIP_INSTALL)"
else
    "$VENV_PYTHON" -m pip install -q -r backend/requirements.txt
fi

# 检查后端端口占用
if check_port_in_use 8000; then
    echo -e "${YELLOW}⚠️  端口 8000 已被占用，请先释放该端口后再启动。${NC}"
    exit 1
fi

# 检查后端环境变量文件
if [ ! -f "backend/.env" ] && [ -f "backend/.env.example" ]; then
    echo "   检测到 backend/.env 不存在，正在从 .env.example 创建..."
    cp backend/.env.example backend/.env
fi

echo "2.5 检查 OnlyOffice 服务..."
try_start_onlyoffice

# 数据库迁移
echo "3. 数据库迁移..."
cd backend
if [ "$SKIP_MIGRATE" = "1" ]; then
    echo "   已跳过数据库迁移 (SKIP_MIGRATE=1)"
else
    "$VENV_PYTHON" manage.py migrate --run-syncdb
fi

# 创建测试用户
echo "4. 创建测试用户..."
if [ "$SKIP_CREATE_TEST_USERS" = "1" ]; then
    echo "   已跳过测试用户创建 (SKIP_CREATE_TEST_USERS=1)"
else
    "$VENV_PYTHON" create_test_users.py
fi

cd ..

# 启动后端
echo -e "${GREEN}5. 启动后端服务...${NC}"
cd backend
"$VENV_PYTHON" manage.py runserver 0.0.0.0:8000 --noreload &

BACKEND_PID=$!
BACKEND_STARTED=1
echo "后端进程ID: $BACKEND_PID"

# 等待后端启动并进行健康检查
echo "   正在检查后端健康状态..."
if ! wait_for_backend_ready; then
    echo -e "${YELLOW}⚠️  后端启动失败或健康检查超时。${NC}"
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
    wait "$BACKEND_PID" 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}✅ 后端服务已启动!${NC}"
echo -e "${GREEN}   访问: http://localhost:8000${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""

# 询问是否启动前端
read -p "是否启动前端开发服务器? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if check_port_in_use 3000; then
        echo -e "${YELLOW}⚠️  端口 3000 已被占用，请先释放该端口后再启动前端。${NC}"
        echo -e "${YELLOW}ℹ️  后端仍在运行: http://localhost:8000${NC}"
        wait $BACKEND_PID
        exit 1
    fi

    echo -e "${GREEN}6. 启动前端服务...${NC}"
    cd ../frontend

    # 检查node_modules
    if [ ! -d "node_modules" ]; then
        if [ "$OFFLINE_MODE" = "1" ]; then
            echo -e "${YELLOW}⚠️  OFFLINE=1 且 frontend/node_modules 不存在，无法在线安装依赖。${NC}"
            echo -e "${YELLOW}ℹ️  请先准备离线 node_modules 包，再重新启动前端。${NC}"
            wait $BACKEND_PID
            exit 1
        else
            echo "   安装前端依赖..."
            npm install
        fi
    fi

    npm run dev -- --host 0.0.0.0 --port 3000 &
    FRONTEND_PID=$!
    FRONTEND_STARTED=1
    echo "前端进程ID: $FRONTEND_PID"

    echo ""
    echo -e "${GREEN}==========================================${NC}"
    echo -e "${GREEN}✅ 前端服务已启动!${NC}"
    echo -e "${GREEN}   访问: http://localhost:3000${NC}"
    echo -e "${GREEN}==========================================${NC}"
    echo ""
    echo -e "${YELLOW}💡 提示:${NC}"
    echo "   管理员账号: admin / Admin@123456"
    echo "   测试用户: user1 / User1@123456"
    echo ""
    echo "   按 Ctrl+C 停止所有服务"
    echo -e "${GREEN}==========================================${NC}"

    # 等待进程
    wait $BACKEND_PID $FRONTEND_PID
else
    echo -e "${YELLOW}ℹ️  前端服务未启动，仅后端运行中${NC}"
    echo ""
    echo -e "${GREEN}==========================================${NC}"
    echo -e "${GREEN}✅ 后端服务运行中!${NC}"
    echo -e "${GREEN}   访问: http://localhost:8000${NC}"
    echo -e "${GREEN}   API: http://localhost:8000/api/${NC}"
    echo -e "${GREEN}==========================================${NC}"
    echo ""
    echo "   按 Ctrl+C 停止服务"
    echo -e "${GREEN}==========================================${NC}"

    wait $BACKEND_PID
fi
