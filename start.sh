#!/bin/bash

# Excel共享系统快速启动脚本

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Excel共享系统 - 快速启动${NC}"
echo "=========================================="

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
echo "1. 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
echo "2. 检查后端依赖..."
pip install -q django djangorestframework django-cors-headers djangorestframework-simplejwt

# 数据库迁移
echo "3. 数据库迁移..."
cd backend
python manage.py migrate --run-syncdb

# 创建测试用户
echo "4. 创建测试用户..."
python create_test_users.py

cd ..

# 启动后端
echo -e "${GREEN}5. 启动后端服务...${NC}"
cd backend
python manage.py runserver 0.0.0.0:8000 &

BACKEND_PID=$!
echo "后端进程ID: $BACKEND_PID"

# 等待后端启动
sleep 3

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
    echo -e "${GREEN}6. 启动前端服务...${NC}"
    cd ../frontend

    # 检查node_modules
    if [ ! -d "node_modules" ]; then
        echo "   安装前端依赖..."
        npm install
    fi

    npm run dev -- --host 0.0.0.0 --port 3000 &
    FRONTEND_PID=$!
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
