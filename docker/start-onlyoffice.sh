#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  OnlyOffice Document Server 部署脚本"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
echo "🔍 检查 Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    echo "请先安装 Docker: https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo "✅ Docker 已安装: $(docker --version)"

# 检查 Docker Compose 是否安装
echo "🔍 检查 Docker Compose..."
if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
    echo "✅ Docker Compose 已安装: $(docker compose version)"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD=(docker-compose)
    echo "✅ Docker Compose 已安装: $(docker-compose --version)"
else
    echo "❌ Docker Compose 未安装"
    echo "请先安装 Docker Compose"
    exit 1
fi
echo ""

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p onlyoffice/data
mkdir -p onlyoffice/logs
mkdir -p onlyoffice/fonts
echo "✅ 目录创建完成"
echo ""

# 启动 OnlyOffice
echo "🚀 启动 OnlyOffice Document Server..."
"${COMPOSE_CMD[@]}" up -d

if [ $? -ne 0 ]; then
    echo "❌ 启动失败，请查看日志: ${COMPOSE_CMD[*]} logs"
    exit 1
fi
echo "✅ 启动命令已执行"
echo ""

# 等待服务启动
echo "⏳ 等待服务启动 (首次启动需要 2-3 分钟)..."
sleep 10

# 检查容器状态
echo "🔍 检查容器状态..."
"${COMPOSE_CMD[@]}" ps
echo ""

# 检查健康状态
echo "🔍 检查健康状态..."
MAX_ATTEMPTS=18
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    HEALTH=$(curl -s -m 3 http://localhost:8081/healthcheck)

    if [ "$HEALTH" = "true" ]; then
        echo "✅ OnlyOffice 服务已就绪"
        echo ""
        echo "=========================================="
        echo "  OnlyOffice 部署成功！"
        echo "=========================================="
        echo ""
        echo "📋 服务信息:"
        echo "  地址: http://localhost:8081"
        echo "  健康检查: http://localhost:8081/healthcheck"
        echo ""
        echo "📝 下一步:"
        echo "  1. 修改 backend/docshare/settings.py"
        echo "     ONLYOFFICE_API_URL = 'http://localhost:8081/'"
        echo ""
        echo "  2. 迁移数据库"
        echo "     cd backend && python manage.py migrate"
        echo ""
        echo "  3. 启动后端服务"
        echo "     cd backend && python manage.py runserver"
        echo ""
        echo "  4. 访问前端测试"
        echo "     http://localhost:3000"
        echo ""
        echo "=========================================="
        exit 0
    fi

    ATTEMPT=$((ATTEMPT + 1))
    echo "⏳ 服务启动中... ($ATTEMPT/$MAX_ATTEMPTS)"
    sleep 10
done

echo "❌ 服务启动超时，请检查日志: ${COMPOSE_CMD[*]} logs"
exit 1
