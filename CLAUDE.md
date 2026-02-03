# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run

```bash
# Setup
cp .env.example .env          # Copy and edit environment variables
source venv_catch_stock_news/bin/activate
pip install -r requirements.txt

# Run
python app.py                  # Starts Flask server on port 5001

# Alternative
./run.sh
```

## Architecture

네이버 증권 실시간 뉴스를 키워드 기반으로 모니터링하고 Slack으로 알림을 보내는 시스템.

### Project Structure

```
app.py                          # 진입점 (thin entry point)
catch_stock_news/               # 메인 패키지
├── config.py                   # get_config() - 환경변수 로딩
├── logging_setup.py            # setup_logging() - 로깅 설정
├── models.py                   # NewsItem dataclass
├── database.py                 # SQLite DB 관리 (keywords, sent_news, alerts)
├── scraper.py                  # 네이버 증권 뉴스 스크래핑 (멀티페이지)
├── notifier.py                 # Slack Incoming Webhook 알림
├── scheduler.py                # APScheduler 초기화
├── services/
│   └── news_checker.py         # check_news_job() + is_notification_time()
└── web/
    ├── __init__.py             # create_app() 팩토리
    ├── routes.py               # Flask Blueprint 라우트
    └── templates/
        └── index.html          # 웹 UI
tests/
├── conftest.py                 # pytest fixtures (app, client)
```

### Key Modules

- `app.py` - 진입점. dotenv 로드 → 로깅 설정 → DB 초기화 → 스케줄러 시작 → Flask 서버 실행.
- `catch_stock_news/config.py` - 환경변수에서 설정값 로딩.
- `catch_stock_news/scraper.py` - 네이버 증권 뉴스 스크래핑. `news_read.naver` URL을 `n.news.naver.com` 직접 링크로 변환.
- `catch_stock_news/notifier.py` - Slack Incoming Webhook으로 뉴스 알림 및 에러 알림 전송.
- `catch_stock_news/database.py` - SQLite DB 관리. keywords(활성/비활성 토글), sent_news(URL+제목 유사도 중복 체크), alerts 테이블.
- `catch_stock_news/services/news_checker.py` - 핵심 비즈니스 로직. 뉴스 체크 + 알림 시간 판단.
- `catch_stock_news/web/routes.py` - Flask Blueprint. 모든 HTTP 엔드포인트.

### Data Flow

1. APScheduler가 `check_news_job()`을 주기적으로 실행 (기본 1분)
2. `scraper.py`가 네이버 증권 뉴스 페이지를 멀티페이지 스크래핑
3. 활성화된 키워드와 매칭되는 뉴스 필터링
4. URL 중복 + 제목 유사도 체크 후 새 뉴스만 처리
5. 알림 시간대 내이면 Slack 전송, DB에 기록

### Import Dependencies (no cycles)

```
app.py (entry point)
  → config.py          (외부 의존성 없음)
  → logging_setup.py   (외부 의존성 없음)
  → models.py          (외부 의존성 없음)
  → database.py        (외부 의존성 없음)
  → scraper.py         → models.py
  → notifier.py        (외부 의존성 없음)
  → services/news_checker.py → config, database, scraper, notifier
  → web/routes.py      → config, database, notifier, news_checker, scheduler
  → scheduler.py       → config
```

### Configuration (.env)

주요 환경변수: `SLACK_WEBHOOK_URL`, `CHECK_INTERVAL_MINUTES`, `NOTIFICATION_START_TIME`, `NOTIFICATION_END_TIME`, `ENABLE_WEEKEND_NOTIFICATIONS`, `ALLOWED_NEWS_SOURCES`, `MAX_PAGES`, `TITLE_SIMILARITY_THRESHOLD`, `LOG_LEVEL`.
