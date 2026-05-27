# CLAUDE.md — Brain Storming을 위한 산업 분석 바탕 가설 분석 Tool

## 프로젝트 개요

전략 컨설팅의 Upfront 리서치 단계(초반 4~5주, 약 40시간)를 30분 이내로 자동화하는 멀티에이전트 파이프라인.
사용자가 **산업 · 기업 · 핵심 질문** 세 가지를 입력하면, KSF/가설 설계 → 이중 검증 → 이원화 So What까지
자동으로 실행되고, 세션 기반으로 회차가 쌓이며 분석이 고도화된다.

---

## 디렉토리 구조

```
src/
├── agents/          # LangGraph 에이전트 정의
│   ├── market_size.py      # 시장규모 에이전트
│   ├── competitor.py       # 경쟁사 에이전트
│   ├── regulation.py       # 규제 에이전트
│   ├── trend.py            # 트렌드 에이전트
│   └── supervisor.py       # Claude Supervisor (KSF·가설 설계)
├── pipeline/        # 파이프라인 조립 및 실행
│   ├── orchestrator.py     # 전체 파이프라인 LangGraph 그래프
│   ├── verifier.py         # 가설 검증 + 루프백 구조 (최대 2회)
│   ├── synthesizer.py      # 이원화 So What 생성 (Claude Synthesizer)
│   └── drift_guard.py      # 드리프트 방지 레이어
├── storage/         # 데이터 저장
│   ├── db.py               # SQLite 연결 및 스키마 초기화
│   ├── compressed_layer.py # 압축 레이어 읽기/쓰기
│   └── raw_layer.py        # 원문 레이어 읽기/쓰기
├── tools/           # 외부 API 연동 도구
│   ├── web_search.py       # Claude 웹서치 + 신뢰 소스 필터
│   ├── dart_api.py         # DART Open API 연동
│   ├── url_fetcher.py      # URL fetch + 본문 추출
│   └── source_filter.py    # 신뢰 소스 필터 도메인 리스트
├── config/          # 설정
│   ├── settings.py         # 환경변수 로드, 전역 상수
│   └── trusted_sources.py  # 신뢰 소스 도메인 정의
└── ui/              # Streamlit 인터페이스
    ├── app.py              # 메인 앱 진입점
    ├── components.py       # 재사용 UI 컴포넌트
    └── pages/              # 멀티페이지 구성 (필요 시)

tests/               # 유닛 테스트
docs/                # 설계 문서
```

---

## 파이프라인 흐름 (5 Steps)

```
[사용자 입력] 산업 · 기업 · 핵심 질문
        ↓
[Step 1] 선행 조사 — 4개 에이전트 병렬 실행
         시장규모 / 경쟁사 / 규제 / 트렌드
         └─ 국내 상장사: DART API / 해외 기업: Claude 웹서치
         └─ URL fetch 본문 검증 → 수치 존재 강제 재확인
        ↓
[Step 2] 분석 축 설계 — Claude Supervisor
         Key Driver 3개 + KSF 3개 동적 정의
         → 가설 3개 자동 수립 (KSF별)
        ↓
[Step 3] 가설 검증 — 본 조사
         가설별 서브쿼리 → 웹서치 + URL fetch
         → 지지 / 반박 / 불충분 태깅
         → 신뢰도 점수 0~100 산출
         → 불충분 시 루프백 (최대 2회)
        ↓
[Step 4] 이원화 So What — Claude Synthesizer
         드리프트 방지 체크 → 두 시각 카드 생성
         사용자 방향 선택 → 2회차 질문 자동 고도화
        ↓
[Step 5] 세션 누적 저장 — SQLite 2레이어
         압축 레이어 (다음 회차 자동 주입)
         원문 레이어 (선택적 호출)
```

---

## 핵심 설계 원칙

### 1. 이중 검증 구조 (할루시네이션 방지)
- **정량 수치**: DART API 직접 연동 + URL fetch 본문 대조
- **정성 트렌드**: Claude 웹서치 + 신뢰 소스 필터
- Claude가 수치 인용 시 → 시스템 프롬프트에서 "본문 존재 여부" 강제 재확인

### 2. 이원화 So What (확증편향 방지)
- 1회차: 긍정 시각 카드 vs 부정 시각 카드 동시 제시
- 사용자 선택 후 2회차부터 단일 트랙 Deep Dive

### 3. 세션 기반 누적 (컨텍스트 팽창 방지)
- 압축 레이어만 매 회차 자동 주입
- 원문 레이어는 필요 시 선택적 호출
- 2~3회차: 불충분 가설에만 핀포인트 웹서치

### 4. 드리프트 방지 레이어
- 매 회차 시작 시 현재 질문 ↔ 최초 핵심 질문 연결성 자동 체크

### 5. 루프백 제한
- 불충분 판정 → 재조사 최대 2회
- 2회 초과 시 판단보류 처리 (파이프라인 중단 방지)

---

## 신뢰 소스 필터 (Trusted Sources)

> **원칙**: URL fetch 본문 추출 가능한 무료 공개 소스만 포함. 유료 페이월 제외.
> 제외 목록: bloomberg.com / ft.com / wsj.com / economist.com / gartner.com / idc.com

### 국내
- 한경 컨센서스 (`consensus.hankyung.com`)
- 네이버 금융 (`finance.naver.com`)
- 미래에셋 리서치 (`securities.miraeasset.com`)
- 매일경제 (`mk.co.kr`)
- 한국경제 (`hankyung.com`)
- 서울경제 (`sedaily.com`)
- 조선비즈 (`biz.chosun.com`)
- 머니투데이 (`news.mt.co.kr`)
- DART 금융감독원 (`dart.fss.or.kr`)
- KRX 전자공시 (`kind.krx.co.kr`)
- 통계청 (`kostat.go.kr`)
- 산업연구원 KIET (`kiet.re.kr`)
- KDI 한국개발연구원 (`kdi.re.kr`)
- 대외경제정책연구원 (`kiep.go.kr`)

### 해외
- Reuters (`reuters.com`) — 로이터 통신, 전면 무료
- AP News (`apnews.com`) — AP 통신, 전면 무료
- CNBC (`cnbc.com`) — 경제방송, 전면 무료
- MarketWatch (`marketwatch.com`) — 전면 무료
- TechCrunch (`techcrunch.com`) — 테크·스타트업
- CoinDesk (`coindesk.com`) — 블록체인·핀테크
- The Verge (`theverge.com`) — 테크·소비자전자
- VentureBeat (`venturebeat.com`) — AI·테크 트렌드
- WEF (`weforum.org`) — 세계경제포럼, 전면 무료
- OECD (`oecd.org`) — 정책·통계 리포트, 전면 무료
- IMF (`imf.org`) — 거시경제 리포트, 전면 무료
- World Bank (`worldbank.org`) — 전면 무료
- McKinsey Insights (`mckinsey.com`) — 무료 공개
- BCG Insights (`bcg.com`) — 무료 공개
- Deloitte Insights (`deloitte.com`) — 전면 무료
- PwC Research (`pwc.com`) — 전면 무료

---

## 환경 변수 (.env)

```
ANTHROPIC_API_KEY=         # Anthropic Claude API 키
DART_API_KEY=              # 금융감독원 DART Open API 키
```

---

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| AI 추론 | Anthropic Claude API (`claude-haiku-4-5`) |
| 멀티에이전트 오케스트레이션 | LangGraph |
| 데이터 수집 | Claude 웹서치 API, DART Open API, httpx |
| 저장소 | SQLite (sqlite-utils) |
| UI | Streamlit |
| 백엔드 | Python 3.11 |

---

## 개발 규칙

1. **모든 수치 인용에는 출처 URL 필수 부착**
2. **신뢰도 점수 없는 가설 결과 출력 금지**
3. **루프백은 가설별 최대 2회로 엄격 제한**
4. **2회차부터 선행조사(Step 1) 재실행 금지** — 압축 레이어에서 로드
5. **드리프트 체크 통과 후에만 So What 생성 진행**
6. **환경변수는 반드시 `.env`에서 로드 (하드코딩 금지)**
7. **Anthropic API 호출 모델은 반드시 `claude-haiku-4-5`만 사용**
   - Sonnet / Opus / 이전 Haiku / Claude-3 계열 절대 금지
   - `src/config/settings.py`의 `CLAUDE_MODEL = "claude-haiku-4-5"` 단일 상수로 관리
   - 직접 `from anthropic import Anthropic` 사용 시에도 `model="claude-haiku-4-5"` 필수
   - CI (`.github/workflows/model-check.yml`) 가 push마다 자동 검증 — 코드/문서 어디든 `claude-*` 문자열이 `claude-haiku-4-5`가 아니면 빌드 실패