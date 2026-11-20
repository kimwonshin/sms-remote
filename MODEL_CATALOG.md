# 원격 테스트 모델 20개 — 2026-11-20

기존 75개 중 10개와 새 통합 CTC 캠페인 10개만 활성화한다. 과거 30fps 3개와 나머지 65개는 원격 목록에서 제외한다. 학습 원본 체크포인트와 과거 결과는 보존한다.

기존 후보: REAL08 문장 WER의 MediaPipe/DWPose 평균으로 TCN 상위 4개·BiLSTM 상위 3개·ST-GCN 상위 2개를 선정하고, 이전 연동 TCN 1개를 비교 기준으로 보존했다. W63의 모호한 WORDID가 포함된 과거 모델은 제외했다. Test 점수는 선정 기준으로 사용하지 않았다.

기본값 `release`: **u98-md-bilstm-wordx4-seed2026**. 비합성 BiLSTM 계열은 seed 3개로 비교했다. 결합10% 모델은 seed 1개인 탐색 후보다.

| 구분 | 모델 ID | 구조 | Seed | 출력 어휘 |
|---|---|---|---:|---|
| 기존 | `md-joint-e50-tcn-seed2026` | tcn | 2026 | S50 (50 + blank) |
| 기존 | `md-sentence-all-tcn-seed123` | tcn | 123 | S50 (50 + blank) |
| 기존 | `md-sentence-tcn-seed2026` | tcn | 2026 | S50 (50 + blank) |
| 기존 | `md-sentence-unknown-tcn-seed123` | tcn | 123 | S50 (50 + blank) |
| 기존 | `md-joint-e50-bilstm-seed123` | bilstm | 123 | S50 (50 + blank) |
| 기존 | `md-sentence-all-bilstm-seed123` | bilstm | 123 | S50 (50 + blank) |
| 기존 | `md-joint-e50-bilstm-seed2026` | bilstm | 2026 | S50 (50 + blank) |
| 기존 | `md-sentence-all-stgcn-seed2026` | stgcn | 2026 | S50 (50 + blank) |
| 기존 | `md-joint-e50-stgcn-seed2026` | stgcn | 2026 | S50 (50 + blank) |
| 기존 | `priority12-tcn-md-j100-all-seed123` | tcn | 123 | S50 (50 + blank) |
| 신규 | `u98-md-tcn-wordx4-seed42` | tcn | 42 | U98 (98 + blank) |
| 신규 | `u98-md-tcn-wordx4-seed123` | tcn | 123 | U98 (98 + blank) |
| 신규 | `u98-md-tcn-wordx4-seed2026` | tcn | 2026 | U98 (98 + blank) |
| 신규 | `u98-md-tcn-wordx1-seed42` | tcn | 42 | U98 (98 + blank) |
| 신규 | `e50-md-tcn-wordx4-seed42` | tcn | 42 | E50 (50 + blank) |
| 신규 | `u98-md-bilstm-wordx4-seed42` | bilstm | 42 | U98 (98 + blank) |
| 신규 | `u98-md-stgcn-wordx4-seed42` | stgcn | 42 | U98 (98 + blank) |
| 신규 | `u98-md-bilstm-wordx4-synth10-seed42` | bilstm | 42 | U98 (98 + blank) |
| 신규 | `u98-md-bilstm-wordx4-seed123` | bilstm | 123 | U98 (98 + blank) |
| 신규 | `u98-md-bilstm-wordx4-seed2026` | bilstm | 2026 | U98 (98 + blank) |

- **S50**: 문장 50라벨 CTC. 단어 보조 헤드가 있어도 원격 Gloss는 문장 50어휘만 출력한다.
- **U98**: 문장50 ∪ 응급50 = 98라벨, blank 포함 99출력. 단어·문장 모두 같은 CTC를 사용한다.
- **E50**: 응급 단어 전용 50라벨, blank 포함 51출력. 문장 번역용이 아닌 대조군이다.

공통 입력은 MediaPipe/DWPose 직접 15fps, canonical74 → 465특징이다. RTMW/hybrid/30fps 입력은 이 20개에 연결하지 않는다.

`benchmark.csv`는 REAL17 문장 3015편·응급 단어 335편 기준이다. S50은 문장 지표만 제공하고 E50의 문장 행은 N/A다. 기존 후보의 p95는 이번 변경에서 다시 측정하지 않아 `not_remeasured`로 표시했다. 신규 p95는 특징 입력 이후 모델·CTC decode 구간이며 영상 추출·전송·LLM은 포함하지 않는다.

이 결과는 전시장 다인 환경이나 새로운 응급 단어가 포함된 자연스러운 연속 문장에 대한 성능을 보장하지 않는다. Confidence는 REAL06 기준 보정이다.

실제 서버 경로와 가중치는 Git에 넣지 않는다. `model_selection.json`은 재현 가능한 고정 ID 목록이며 서버 `build_registry.py`가 결과·체크포인트·추출기별 보정 해시를 검증해 로컬 등록한다.
