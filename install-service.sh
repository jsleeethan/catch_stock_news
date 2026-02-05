#!/bin/bash

# Catch Stock News - systemd 서비스 설치 스크립트

set -e

SERVICE_NAME="catch-stock-news"
SERVICE_FILE="catch-stock-news.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Catch Stock News 서비스 설치 ==="

# 서비스 파일 복사
echo "서비스 파일 복사 중..."
sudo cp "$SCRIPT_DIR/$SERVICE_FILE" /etc/systemd/system/

# systemd 리로드
echo "systemd 리로드 중..."
sudo systemctl daemon-reload

# 서비스 활성화 (부팅 시 자동 시작)
echo "서비스 활성화 중..."
sudo systemctl enable $SERVICE_NAME

# 서비스 시작
echo "서비스 시작 중..."
sudo systemctl start $SERVICE_NAME

# 상태 확인
echo ""
echo "=== 서비스 상태 ==="
sudo systemctl status $SERVICE_NAME --no-pager

echo ""
echo "=== 설치 완료 ==="
echo ""
echo "유용한 명령어:"
echo "  sudo systemctl status $SERVICE_NAME   # 상태 확인"
echo "  sudo systemctl stop $SERVICE_NAME     # 중지"
echo "  sudo systemctl start $SERVICE_NAME    # 시작"
echo "  sudo systemctl restart $SERVICE_NAME  # 재시작"
echo "  sudo journalctl -u $SERVICE_NAME -f   # 로그 보기 (실시간)"
