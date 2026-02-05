#!/bin/bash

# Catch Stock News - systemd 서비스 제거 스크립트

set -e

SERVICE_NAME="catch-stock-news"

echo "=== Catch Stock News 서비스 제거 ==="

# 서비스 중지
echo "서비스 중지 중..."
sudo systemctl stop $SERVICE_NAME 2>/dev/null || true

# 서비스 비활성화
echo "서비스 비활성화 중..."
sudo systemctl disable $SERVICE_NAME 2>/dev/null || true

# 서비스 파일 삭제
echo "서비스 파일 삭제 중..."
sudo rm -f /etc/systemd/system/$SERVICE_NAME.service

# systemd 리로드
echo "systemd 리로드 중..."
sudo systemctl daemon-reload

echo ""
echo "=== 제거 완료 ==="
