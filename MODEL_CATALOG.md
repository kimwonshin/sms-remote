# 원격 테스트 모델 32개 — 2026-11-21

이전 후보 20개를 유지하고 새 응급 결합 CTC 학습 12개를 추가했다. 현재 활성 목록은 총32개다. 고정 ID·선정 근거는 model_selection.json, 실제 등록은 서버의 model-registry.json이 기준이다.

기본 `release`: **domain-u98-bilstm-paired-m4-s10-w20-seed42**. 실제 S50 문장70%·실제 의미 정정 E49 단어20%·M4 결합10%, MediaPipe/DWPose 교대 입력으로 학습했다. REAL08 두 추출기의 문장 WER와 응급 단어 정확도 오류를 균등 반영하여 선정했고, 최상위 조건은 seed42·123·2026을 확인했다. Test는 선정에 사용하지 않았다.

| 묶음 | 모델 ID | 구조 | Seed | Gloss/CTC 출력 |
|---|---|---|---:|---:|
| previous10 | `md-joint-e50-tcn-seed2026` | tcn | 2026 | 50/51 |
| previous10 | `md-sentence-all-tcn-seed123` | tcn | 123 | 50/51 |
| previous10 | `md-sentence-tcn-seed2026` | tcn | 2026 | 50/51 |
| previous10 | `md-sentence-unknown-tcn-seed123` | tcn | 123 | 50/51 |
| previous10 | `md-joint-e50-bilstm-seed123` | bilstm | 123 | 50/51 |
| previous10 | `md-sentence-all-bilstm-seed123` | bilstm | 123 | 50/51 |
| previous10 | `md-joint-e50-bilstm-seed2026` | bilstm | 2026 | 50/51 |
| previous10 | `md-sentence-all-stgcn-seed2026` | stgcn | 2026 | 50/51 |
| previous10 | `md-joint-e50-stgcn-seed2026` | stgcn | 2026 | 50/51 |
| previous10 | `priority12-tcn-md-j100-all-seed123` | tcn | 123 | 50/51 |
| new10 | `u98-md-tcn-wordx4-seed42` | tcn | 42 | 98/99 |
| new10 | `u98-md-tcn-wordx4-seed123` | tcn | 123 | 98/99 |
| new10 | `u98-md-tcn-wordx4-seed2026` | tcn | 2026 | 98/99 |
| new10 | `u98-md-tcn-wordx1-seed42` | tcn | 42 | 98/99 |
| new10 | `e50-md-tcn-wordx4-seed42` | tcn | 42 | 50/51 |
| new10 | `u98-md-bilstm-wordx4-seed42` | bilstm | 42 | 98/99 |
| new10 | `u98-md-stgcn-wordx4-seed42` | stgcn | 42 | 98/99 |
| new10 | `u98-md-bilstm-wordx4-synth10-seed42` | bilstm | 42 | 98/99 |
| new10 | `u98-md-bilstm-wordx4-seed123` | bilstm | 123 | 98/99 |
| new10 | `u98-md-bilstm-wordx4-seed2026` | bilstm | 2026 | 98/99 |
| domain12 | `domain-u98-bilstm-paired-real-s00-w20-seed42` | bilstm | 42 | 98/99 |
| domain12 | `domain-u98-bilstm-paired-m2-s05-w20-seed42` | bilstm | 42 | 98/99 |
| domain12 | `domain-u98-bilstm-paired-m4-s05-w20-seed42` | bilstm | 42 | 98/99 |
| domain12 | `domain-u98-bilstm-paired-m5-s05-w20-seed42` | bilstm | 42 | 98/99 |
| domain12 | `domain-u98-bilstm-dwpose-m5-s05-w20-seed42` | bilstm | 42 | 98/99 |
| domain12 | `domain-u97-bilstm-paired-m5-s05-w20-seed42` | bilstm | 42 | 97/98 |
| domain12 | `domain-utop25-bilstm-paired-m5-s05-w20-seed42` | bilstm | 42 | 74/75 |
| domain12 | `domain-u98-tcn-paired-m5-s05-w20-seed42` | tcn | 42 | 98/99 |
| domain12 | `domain-u98-bilstm-paired-m5-s05-w30-seed42` | bilstm | 42 | 98/99 |
| domain12 | `domain-u98-bilstm-paired-m4-s10-w20-seed42` | bilstm | 42 | 98/99 |
| domain12 | `domain-u98-bilstm-paired-m4-s10-w20-seed123` | bilstm | 123 | 98/99 |
| domain12 | `domain-u98-bilstm-paired-m4-s10-w20-seed2026` | bilstm | 2026 | 98/99 |

## 출력 범위와 의미 정책

- `previous10`: 문장 S50, 50글로스/blank 포함51출력. 단어 보조 헤드가 있어도 원격 Gloss는 문장 어휘만 출력한다.
- `new10`: 이전 통합 U98 9개(98/99), 응급 단어 전용 E50 대조군1개(50/51). E50은 문장 번역용이 아니다.
- `domain12`: 의미 정정 E49로 학습한 U98 10개(98/99), U97 1개(97/98), S50+Train 빈출 응급Top25인 U74 1개(74/75). 저장된 설정 ID `Utop25`는 U74다.
- 새 결합 U98의 신체 **다리**는 의미가 확인된 원본이 없어 감독0건인 예비 클래스다. 모델의 `unsupported_training_glosses`에 표시한다. U97/U74에는 해당 클래스가 없다.
- 새 결합 데이터는 DWPose만 존재한다. 두 추출기 혼합 모델도 합성 부분은 DWPose이며, DWPose 단독 학습 모델은 학습 출처가 `dwpose`로 표시된다. 모두 실제 두 추출기 입력으로 평가했으며 해당 모델·추출기의 원래 보정 profile을 사용한다.

## 모델 묶음과 평가

`old10`/`new10`은 이전 각10개, `native20`은 이전20개, `domain12`는 새12개, `native32`/`all`은32개, `release`는 추천 새 결합 BiLSTM1개다. 과거 native75·legacy와 제외된 모델은 계속 요청에서 거부한다. 가중치·원본 학습 결과는 보존하며 Git에는 올리지 않는다.

`benchmark.csv`는 이전20개 결과와 새12개 결과를 함께 제공한다. **이전 응급 E50는335편, 새 의미 정정 E49는315편**이므로 정확도 증감으로 직접 비교하거나 평균을 합치지 않는다. 실제 문장은 공통 REAL17 3015편이다. 새12개는 `full_scope`와 `covered_only`를 분리하고, U74도 전체 E49 분모의 OOV를 숨기지 않는다. `target_coverage`도 확인한다. CSV에서 full_scope만 선택해야 두 평가 범위를 중복 집계하지 않는다.

기존 후보의 p95는 이번 등록에서 재측정하지 않아 not_remeasured다. 새 모델의 p95는 특징 입력 이후 모델·CTC decode이며 영상 추출·전송·LLM/TTS를 포함하지 않는다. Confidence는 REAL06 보정이고 전시장 다인 환경과 자연스러운 응급 연속 문장 정확도는 별도 검증 대상이다.

새 결합 방식 비교는 동일한654개 원본·각도 표본/225그룹을 사용했다. M2/M4/M5와 합성5%/10%, 실제 단어20%/30%, DW단독/혼합, U98/U97/U74 및 TCN/BiLSTM 조합을 포함한다. 모든 실제 후보는 고정16epoch를 완료했다. 합성 자연스러움의 사람 검수는 pending인 실험 자료다.
