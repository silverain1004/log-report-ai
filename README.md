# 로그 대신 읽어드림 — 서버 로그 주간 점검 자동화 + Claude AI 요약

매주 서버 로그를 직접 열어 보던 점검을 **월요일 아침 메일 한 통**으로 바꾼 도구입니다.
Windows(Nginx + Tomcat 2종)와 Linux 이중화(WEB 2대 + WAS 2대) 환경에서 실제로 운영 중입니다.

- **데모:** GitHub Pages `docs/index.html` (합성 로그로 만든 리포트, 로그인 없음)
- **수집 → 분류 → AI 요약 → 메일 발송**을 스케줄러(cron / 작업 스케줄러)가 사람 없이 처리
- 알려진 스캔 시그니처(FortiOS, WordPress, 정찰성)와 토큰 재발급 401은 자동으로 소음 처리
- 메일 맨 위에 Claude가 쓴 **종합 판단(정상/주의/위험) + 확인할 것 2~4줄**

## 구성

| 파일 | 역할 |
|---|---|
| `win_analyzer.py` | Windows 서버 로그 분석 (PyInstaller로 exe 빌드) |
| `linux_analyzer.py` | Linux 이중화 로그 분석 (WEB1에서 SSH로 나머지 노드 수집, L4 편차 계산) |
| `ai_summary.py` | Claude Messages API 호출 — SDK 없이 `urllib`만 사용 (서버가 Python 3.6) |
| `report_builder.py` | HTML 상세 리포트 + 메일 본문 생성 |
| `mail_sender.py` | SMTP 발송, 리포트 ZIP 첨부 |
| `demo/generate_demo.py` | 합성 로그로 `docs/` 데모 생성 |

## AI 요약의 안전장치

- 원본 로그를 통째로 보내지 않음: 집계 수치 + '미분류' 샘플 최대 15줄만 전송
- 전송 전 IP 뒤 두 자리와 이메일 마스킹 (`10.20.x.x`, `***@***`)
- 키가 없거나 API 호출이 실패해도 리포트와 메일은 기존대로 발송 (`--no-ai`로 끌 수 있음)
- API 키는 `config.json`(git 제외) 또는 환경변수 `ANTHROPIC_API_KEY`

## 실행

```bash
pip install -r requirements.txt
cp config.example.json config.json   # SMTP·AI·서버 정보 입력

python win_analyzer.py --auto weekly --test-email     # Windows, 본인에게만 테스트 발송
python linux_analyzer.py --auto weekly --no-email      # Linux, 리포트만 생성
```

스케줄 등록 예시는 `scripts/` (Windows 작업 스케줄러, Linux crontab), Linux 배포 절차는 [README-linux.md](README-linux.md).

## 데모 다시 만들기

```bash
python demo/generate_demo.py                                   # 저장된 AI 요약 사용
ANTHROPIC_API_KEY=sk-ant-... python demo/generate_demo.py --refresh-ai   # Claude로 새로 요약
python -m pytest tests
```

샘플 로그의 IP는 문서용 대역(RFC 5737)과 사설 대역만 사용하며, 실서버 로그는 포함되어 있지 않습니다.
