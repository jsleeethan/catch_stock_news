# Catch Stock News

네이버 증권 실시간 뉴스를 키워드 기반으로 모니터링하고, 매칭되는 뉴스를 Slack으로 알림 보내는 시스템입니다.

## 주요 기능

- 네이버 증권 뉴스 실시간 멀티페이지 스크래핑
- 키워드 기반 뉴스 매칭 (활성/비활성 토글)
- Slack Incoming Webhook 알림
- URL 중복 + 제목 유사도 기반 중복 방지
- 알림 시간대 및 주말 알림 설정
- 웹 UI를 통한 키워드 관리 및 알림 내역 조회

## 설치 및 실행

### 1. 환경 설정

```bash
git clone <repository-url>
cd catch_stock_news

python3 -m venv venv_catch_stock_news
source venv_catch_stock_news/bin/activate
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 설정값을 수정합니다.

| 환경변수 | 설명 | 기본값 |
|---|---|---|
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL | (필수) |
| `CHECK_INTERVAL_MINUTES` | 뉴스 체크 주기 (분) | `1` |
| `NOTIFICATION_START_TIME` | 알림 시작 시간 (HH:MM) | `09:00` |
| `NOTIFICATION_END_TIME` | 알림 종료 시간 (HH:MM) | `18:00` |
| `ENABLE_WEEKEND_NOTIFICATIONS` | 주말 알림 여부 | `false` |
| `ALLOWED_NEWS_SOURCES` | 허용 언론사 (쉼표 구분) | (전체) |
| `MAX_PAGES` | 스크래핑 최대 페이지 수 | `3` |
| `TITLE_SIMILARITY_THRESHOLD` | 제목 유사도 임계값 (0.0-1.0) | `0.8` |
| `ENABLE_ERROR_NOTIFICATIONS` | 에러 알림 Slack 전송 여부 | `true` |
| `LOG_LEVEL` | 로그 레벨 | `INFO` |

### 3. 실행

```bash
python app.py
```

또는

```bash
./run.sh
```

Flask 서버가 `http://localhost:5001`에서 실행됩니다.

### 4. 시스템 서비스로 실행 (Ubuntu)

PC 부팅 시 자동 시작되도록 systemd 서비스로 등록할 수 있습니다.

```bash
# 설치 및 시작
./install-service.sh

# 서비스 관리
sudo systemctl status catch-stock-news   # 상태 확인
sudo systemctl stop catch-stock-news     # 중지
sudo systemctl start catch-stock-news    # 시작
sudo systemctl restart catch-stock-news  # 재시작
sudo journalctl -u catch-stock-news -f   # 로그 보기 (실시간)

# 제거
./uninstall-service.sh
```

## 웹 UI

`http://localhost:5001` 접속 시 다음 기능을 사용할 수 있습니다:

- 모니터링 키워드 추가/삭제/활성화/비활성화
- 실시간 시스템 상태 확인
- 알림 내역 조회 및 삭제
- 수동 뉴스 확인 실행

## API 엔드포인트

| Method | Path | 설명 |
|---|---|---|
| `GET` | `/` | 웹 UI |
| `GET` | `/status` | 시스템 상태 조회 |
| `GET` | `/keywords` | 키워드 목록 조회 |
| `POST` | `/keywords` | 키워드 추가 |
| `DELETE` | `/keywords/<id>` | 키워드 삭제 |
| `POST` | `/keywords/<id>/toggle` | 키워드 활성/비활성 토글 |
| `POST` | `/check-now` | 수동 뉴스 확인 |
| `GET` | `/alerts` | 알림 내역 조회 |
| `DELETE` | `/alerts` | 알림 내역 전체 삭제 |

## 프로젝트 구조

```
app.py                          # 진입점
catch_stock_news/               # 메인 패키지
├── config.py                   # 환경변수 로딩
├── logging_setup.py            # 로깅 설정
├── models.py                   # NewsItem dataclass
├── database.py                 # SQLite DB 관리
├── scraper.py                  # 네이버 증권 뉴스 스크래핑
├── notifier.py                 # Slack 알림
├── scheduler.py                # APScheduler 초기화
├── services/
│   └── news_checker.py         # 뉴스 체크 비즈니스 로직
└── web/
    ├── __init__.py             # Flask app factory
    ├── routes.py               # Flask Blueprint 라우트
    └── templates/
        └── index.html          # 웹 UI
tests/
├── conftest.py                 # pytest fixtures
```

## 동작 흐름

1. APScheduler가 설정된 주기(기본 1분)마다 `check_news_job()` 실행
2. 네이버 증권 뉴스 페이지를 멀티페이지 스크래핑
3. 활성화된 키워드와 매칭되는 뉴스 필터링
4. URL 중복 + 제목 유사도 체크 후 새 뉴스만 처리
5. 알림 시간대 내이면 Slack 전송, DB에 기록
