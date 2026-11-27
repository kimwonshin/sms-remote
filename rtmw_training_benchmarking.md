# RTMW 포함 학습·벤치마킹

상태: 학습·벤치마크 완료, 원격 등록 별도 확인 · 2026-11-27T03:31:27.220521+00:00

응급 E49는 전부 실제 양성 학습 자료를 유지한다. 신체 다리는 유효한 정답 자료가 없어 미학습이며 교량 WORD1599를 사용하지 않는다. U97=지원되는 S50∪E49, U74=E49+Train 빈도 상위 문장 전용25라벨(방법 포함). 선택 라벨은 모두 하나의 lexical CTC로 출력하며 별도 단어 분류 헤드는 없다.
RTX2080Ti·기존Torch 환경·FP32·batch8·AdamW3e-4·16epoch·epoch당41924노출을 고정한다. 매 epoch 실제 문장70%·E49단어20%·결합10%; 라벨별 단어 균형 및 결합 순서/농인/각도 균형. 원본 MP/DW/RTMW의 같은 UID는 시퀀스 전체를 순환해 선택하며 독립 표본3개로 과대계산하지 않는다.
R0=RTMW실제+RTMW결합, R1=3추출기 실제+RTMW결합, R2=3추출기 실제+DW/RTMW결합, R3=R2+공유 보조localCTC0.1, R4=R2의U74 응급 집중 조건, R5=R2의TCN. 나머지는BiLSTM. 이전 ST-GCN 성능을 근거로 이번 유력 후보에서 제외했다. 초기6조건 후 REAL08/예약dev로 고른 전체어휘 후보를 seed123·2026으로 재확인한다.
REAL06 보정, REAL08 모델/조건 선택, 동일 REAL17 Test3330건(문장3015·단어315)을 추출기별 평가한다. REAL18 단어는 공통 Test에서 제외한다. 합성은 두 추출기가 공통 지원하는 예약 순서만 비교하고 지원하지 않는8개 예약 순서를 Train으로 옮기지 않는다. Train 조각을 재사용한 합성 진단과 실제 Test는 구분한다.
선택 점수=.35 REAL08 문장WER+.25 E49단어오류+.40 양 추출기 공통 합성devWER. Test는 선정에 사용하지 않는다. 축소 어휘의 전체 Test OOV도 오류에 포함하고 지원 어휘만의 점수는 별도 표시한다. 전체어휘 잠정후보와 축소어휘 응급 특화 조건을 혼동하지 않는다.
UNKNOWN은 기존 MP/DW와 비교 조건을 맞추기 위해 RTMW sentence weak gap 라벨을 명시적으로 opt-in했다. 자동 gap은 검수된 의미 없는 동작 정답이 아니다. 단어/합성 UNKNOWN은 -1, 질문 라벨은 원본 유효분만 사용한다. confidence는 detector score와 구분하며 매 체크포인트·추출기 자체 REAL06으로 재보정한다. quality=mean(clip(detector_score)*mask).
서비스 기본 모델을 유지하고 완료·검증 모델을 별도 후보 목록에 추가한다. 새로운 실제 카메라 미학습 순서 검증은 제공되지 않아 잠정 후보로 표기한다.

| 모델 | 상태 | 완료epoch | 학습분 |
|---|---|---:|---:|
| rtmw-data-r0-bilstm-u97-seed42 | 완료 | 16 | 23.1 |
| rtmw-data-r1-bilstm-u97-seed42 | 완료 | 16 | 23.1 |
| rtmw-data-r2-bilstm-u97-seed42 | 완료 | 16 | 23.7 |
| rtmw-data-r3-bilstm-u97-seed42 | 완료 | 16 | 36.6 |
| rtmw-data-r4-bilstm-u74-seed42 | 완료 | 16 | 23.8 |
| rtmw-data-r5-tcn-u97-seed42 | 완료 | 16 | 18.0 |
| rtmw-data-r3-bilstm-u97-seed123 | 완료 | 16 | 37.8 |
| rtmw-data-r3-bilstm-u97-seed2026 | 완료 | 16 | 37.7 |

## 공통 Test 및 예약 순서 진단

| 모델 | 범위 / 추출기 / 과제 | n | 완전일치 | WER | MacroF1 | p95ms |
|---|---|---:|---:|---:|---:|---:|---:|
| rtmw-data-r0-bilstm-u97-seed42 | actual_REAL17_full/mediapipe/sentence | 3015 | 0.91874 | 0.02946 | 0.98003 | 3.91671 |
| rtmw-data-r0-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/mediapipe/sentence | 3015 | 0.91874 | 0.02946 | 0.98003 | 3.91671 |
| rtmw-data-r0-bilstm-u97-seed42 | actual_REAL17_full/mediapipe/emergency_word | 315 | 0.81270 | 0.19365 | 0.85462 | 2.88535 |
| rtmw-data-r0-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/mediapipe/emergency_word | 315 | 0.81270 | 0.19365 | 0.85462 | 2.88535 |
| rtmw-data-r0-bilstm-u97-seed42 | actual_REAL17_full/dwpose/sentence | 3015 | 0.92239 | 0.02564 | 0.96929 | 3.95257 |
| rtmw-data-r0-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/dwpose/sentence | 3015 | 0.92239 | 0.02564 | 0.96929 | 3.95257 |
| rtmw-data-r0-bilstm-u97-seed42 | actual_REAL17_full/dwpose/emergency_word | 315 | 0.90794 | 0.09206 | 0.91463 | 2.91385 |
| rtmw-data-r0-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/dwpose/emergency_word | 315 | 0.90794 | 0.09206 | 0.91463 | 2.91385 |
| rtmw-data-r0-bilstm-u97-seed42 | actual_REAL17_full/rtmw/sentence | 3015 | 0.97944 | 0.00654 | 0.99388 | 3.88836 |
| rtmw-data-r0-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/rtmw/sentence | 3015 | 0.97944 | 0.00654 | 0.99388 | 3.88836 |
| rtmw-data-r0-bilstm-u97-seed42 | actual_REAL17_full/rtmw/emergency_word | 315 | 0.96190 | 0.03810 | 0.96557 | 2.88195 |
| rtmw-data-r0-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/rtmw/emergency_word | 315 | 0.96190 | 0.03810 | 0.96557 | 2.88195 |
| rtmw-data-r0-bilstm-u97-seed42 | synthetic_diagnostic_dev/dwpose/composed_order | 86 | 0.90698 | 0.03279 | 0.98051 | 4.44334 |
| rtmw-data-r0-bilstm-u97-seed42 | synthetic_diagnostic_dev/rtmw/composed_order | 85 | 0.95294 | 0.01325 | 0.98656 | 4.40567 |
| rtmw-data-r0-bilstm-u97-seed42 | synthetic_diagnostic_test/dwpose/composed_order | 74 | 0.93243 | 0.02308 | 0.98886 | 4.53793 |
| rtmw-data-r0-bilstm-u97-seed42 | synthetic_diagnostic_test/rtmw/composed_order | 76 | 0.98684 | 0.00373 | 0.99940 | 4.51633 |
| rtmw-data-r1-bilstm-u97-seed42 | actual_REAL17_full/mediapipe/sentence | 3015 | 0.96617 | 0.01086 | 0.99184 | 3.99642 |
| rtmw-data-r1-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/mediapipe/sentence | 3015 | 0.96617 | 0.01086 | 0.99184 | 3.99642 |
| rtmw-data-r1-bilstm-u97-seed42 | actual_REAL17_full/mediapipe/emergency_word | 315 | 0.95238 | 0.05079 | 0.95159 | 2.94366 |
| rtmw-data-r1-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/mediapipe/emergency_word | 315 | 0.95238 | 0.05079 | 0.95159 | 2.94366 |
| rtmw-data-r1-bilstm-u97-seed42 | actual_REAL17_full/dwpose/sentence | 3015 | 0.95323 | 0.01528 | 0.98539 | 4.01907 |
| rtmw-data-r1-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/dwpose/sentence | 3015 | 0.95323 | 0.01528 | 0.98539 | 4.01907 |
| rtmw-data-r1-bilstm-u97-seed42 | actual_REAL17_full/dwpose/emergency_word | 315 | 0.94921 | 0.05397 | 0.95466 | 2.92446 |
| rtmw-data-r1-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/dwpose/emergency_word | 315 | 0.94921 | 0.05397 | 0.95466 | 2.92446 |
| rtmw-data-r1-bilstm-u97-seed42 | actual_REAL17_full/rtmw/sentence | 3015 | 0.97479 | 0.00804 | 0.99454 | 3.99925 |
| rtmw-data-r1-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/rtmw/sentence | 3015 | 0.97479 | 0.00804 | 0.99454 | 3.99925 |
| rtmw-data-r1-bilstm-u97-seed42 | actual_REAL17_full/rtmw/emergency_word | 315 | 0.95556 | 0.04444 | 0.96290 | 2.92270 |
| rtmw-data-r1-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/rtmw/emergency_word | 315 | 0.95556 | 0.04444 | 0.96290 | 2.92270 |
| rtmw-data-r1-bilstm-u97-seed42 | synthetic_diagnostic_dev/dwpose/composed_order | 86 | 0.93023 | 0.02295 | 0.99126 | 4.50301 |
| rtmw-data-r1-bilstm-u97-seed42 | synthetic_diagnostic_dev/rtmw/composed_order | 85 | 0.95294 | 0.01325 | 0.98093 | 4.34953 |
| rtmw-data-r1-bilstm-u97-seed42 | synthetic_diagnostic_test/dwpose/composed_order | 74 | 0.91892 | 0.02308 | 0.99112 | 4.60301 |
| rtmw-data-r1-bilstm-u97-seed42 | synthetic_diagnostic_test/rtmw/composed_order | 76 | 0.97368 | 0.00746 | 0.99703 | 4.55569 |
| rtmw-data-r2-bilstm-u97-seed42 | actual_REAL17_full/mediapipe/sentence | 3015 | 0.97645 | 0.00814 | 0.99289 | 3.97859 |
| rtmw-data-r2-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/mediapipe/sentence | 3015 | 0.97645 | 0.00814 | 0.99289 | 3.97859 |
| rtmw-data-r2-bilstm-u97-seed42 | actual_REAL17_full/mediapipe/emergency_word | 315 | 0.97143 | 0.02857 | 0.97351 | 2.93311 |
| rtmw-data-r2-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/mediapipe/emergency_word | 315 | 0.97143 | 0.02857 | 0.97351 | 2.93311 |
| rtmw-data-r2-bilstm-u97-seed42 | actual_REAL17_full/dwpose/sentence | 3015 | 0.95920 | 0.01448 | 0.98944 | 4.00425 |
| rtmw-data-r2-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/dwpose/sentence | 3015 | 0.95920 | 0.01448 | 0.98944 | 4.00425 |
| rtmw-data-r2-bilstm-u97-seed42 | actual_REAL17_full/dwpose/emergency_word | 315 | 0.98095 | 0.01905 | 0.98080 | 2.94821 |
| rtmw-data-r2-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/dwpose/emergency_word | 315 | 0.98095 | 0.01905 | 0.98080 | 2.94821 |
| rtmw-data-r2-bilstm-u97-seed42 | actual_REAL17_full/rtmw/sentence | 3015 | 0.97645 | 0.00845 | 0.99382 | 3.92137 |
| rtmw-data-r2-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/rtmw/sentence | 3015 | 0.97645 | 0.00845 | 0.99382 | 3.92137 |
| rtmw-data-r2-bilstm-u97-seed42 | actual_REAL17_full/rtmw/emergency_word | 315 | 0.98730 | 0.01270 | 0.98744 | 2.90006 |
| rtmw-data-r2-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/rtmw/emergency_word | 315 | 0.98730 | 0.01270 | 0.98744 | 2.90006 |
| rtmw-data-r2-bilstm-u97-seed42 | synthetic_diagnostic_dev/dwpose/composed_order | 86 | 0.86047 | 0.04262 | 0.96961 | 4.52036 |
| rtmw-data-r2-bilstm-u97-seed42 | synthetic_diagnostic_dev/rtmw/composed_order | 85 | 0.89412 | 0.02980 | 0.97543 | 4.28957 |
| rtmw-data-r2-bilstm-u97-seed42 | synthetic_diagnostic_test/dwpose/composed_order | 74 | 0.95946 | 0.01154 | 0.99527 | 4.55904 |
| rtmw-data-r2-bilstm-u97-seed42 | synthetic_diagnostic_test/rtmw/composed_order | 76 | 0.96053 | 0.01119 | 0.99627 | 4.50006 |
| rtmw-data-r3-bilstm-u97-seed42 | actual_REAL17_full/mediapipe/sentence | 3015 | 0.98408 | 0.00503 | 0.99506 | 4.00046 |
| rtmw-data-r3-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/mediapipe/sentence | 3015 | 0.98408 | 0.00503 | 0.99506 | 4.00046 |
| rtmw-data-r3-bilstm-u97-seed42 | actual_REAL17_full/mediapipe/emergency_word | 315 | 0.97460 | 0.02540 | 0.98566 | 2.90841 |
| rtmw-data-r3-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/mediapipe/emergency_word | 315 | 0.97460 | 0.02540 | 0.98566 | 2.90841 |
| rtmw-data-r3-bilstm-u97-seed42 | actual_REAL17_full/dwpose/sentence | 3015 | 0.96318 | 0.01166 | 0.98561 | 3.93995 |
| rtmw-data-r3-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/dwpose/sentence | 3015 | 0.96318 | 0.01166 | 0.98561 | 3.93995 |
| rtmw-data-r3-bilstm-u97-seed42 | actual_REAL17_full/dwpose/emergency_word | 315 | 0.97460 | 0.02540 | 0.97707 | 2.89533 |
| rtmw-data-r3-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/dwpose/emergency_word | 315 | 0.97460 | 0.02540 | 0.97707 | 2.89533 |
| rtmw-data-r3-bilstm-u97-seed42 | actual_REAL17_full/rtmw/sentence | 3015 | 0.98375 | 0.00503 | 0.99445 | 3.98032 |
| rtmw-data-r3-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/rtmw/sentence | 3015 | 0.98375 | 0.00503 | 0.99445 | 3.98032 |
| rtmw-data-r3-bilstm-u97-seed42 | actual_REAL17_full/rtmw/emergency_word | 315 | 0.98413 | 0.01587 | 0.98734 | 2.93141 |
| rtmw-data-r3-bilstm-u97-seed42 | actual_REAL17_vocabulary_covered/rtmw/emergency_word | 315 | 0.98413 | 0.01587 | 0.98734 | 2.93141 |
| rtmw-data-r3-bilstm-u97-seed42 | synthetic_diagnostic_dev/dwpose/composed_order | 86 | 0.95349 | 0.01311 | 0.98525 | 4.50786 |
| rtmw-data-r3-bilstm-u97-seed42 | synthetic_diagnostic_dev/rtmw/composed_order | 85 | 0.98824 | 0.00662 | 0.99052 | 4.35637 |
| rtmw-data-r3-bilstm-u97-seed42 | synthetic_diagnostic_test/dwpose/composed_order | 74 | 0.97297 | 0.00769 | 0.99564 | 4.57164 |
| rtmw-data-r3-bilstm-u97-seed42 | synthetic_diagnostic_test/rtmw/composed_order | 76 | 0.98684 | 0.00373 | 0.99580 | 4.62067 |
| rtmw-data-r4-bilstm-u74-seed42 | actual_REAL17_full/mediapipe/sentence | 3015 | 0.55290 | 0.20895 | 0.86056 | 3.93638 |
| rtmw-data-r4-bilstm-u74-seed42 | actual_REAL17_vocabulary_covered/mediapipe/sentence | 1710 | 0.97485 | 0.00732 | 0.98988 | 4.00593 |
| rtmw-data-r4-bilstm-u74-seed42 | actual_REAL17_full/mediapipe/emergency_word | 315 | 0.95238 | 0.04762 | 0.95971 | 2.88508 |
| rtmw-data-r4-bilstm-u74-seed42 | actual_REAL17_vocabulary_covered/mediapipe/emergency_word | 315 | 0.95238 | 0.04762 | 0.95971 | 2.88508 |
| rtmw-data-r4-bilstm-u74-seed42 | actual_REAL17_full/dwpose/sentence | 3015 | 0.54129 | 0.22584 | 0.84446 | 3.94080 |
| rtmw-data-r4-bilstm-u74-seed42 | actual_REAL17_vocabulary_covered/dwpose/sentence | 1710 | 0.95439 | 0.01396 | 0.98105 | 4.03306 |
| rtmw-data-r4-bilstm-u74-seed42 | actual_REAL17_full/dwpose/emergency_word | 315 | 0.97778 | 0.02222 | 0.98292 | 3.03542 |
| rtmw-data-r4-bilstm-u74-seed42 | actual_REAL17_vocabulary_covered/dwpose/emergency_word | 315 | 0.97778 | 0.02222 | 0.98292 | 3.03542 |
| rtmw-data-r4-bilstm-u74-seed42 | actual_REAL17_full/rtmw/sentence | 3015 | 0.55622 | 0.21237 | 0.86188 | 3.90629 |
| rtmw-data-r4-bilstm-u74-seed42 | actual_REAL17_vocabulary_covered/rtmw/sentence | 1710 | 0.98070 | 0.00562 | 0.99329 | 3.96784 |
| rtmw-data-r4-bilstm-u74-seed42 | actual_REAL17_full/rtmw/emergency_word | 315 | 0.97778 | 0.02222 | 0.98757 | 2.91900 |
| rtmw-data-r4-bilstm-u74-seed42 | actual_REAL17_vocabulary_covered/rtmw/emergency_word | 315 | 0.97778 | 0.02222 | 0.98757 | 2.91900 |
| rtmw-data-r4-bilstm-u74-seed42 | synthetic_diagnostic_dev/dwpose/composed_order | 86 | 0.97674 | 0.00656 | 0.99845 | 4.55195 |
| rtmw-data-r4-bilstm-u74-seed42 | synthetic_diagnostic_dev/rtmw/composed_order | 85 | 1.00000 | 0.00000 | 1.00000 | 4.35456 |
| rtmw-data-r4-bilstm-u74-seed42 | synthetic_diagnostic_test/dwpose/composed_order | 74 | 0.97297 | 0.00769 | 0.98366 | 4.59638 |
| rtmw-data-r4-bilstm-u74-seed42 | synthetic_diagnostic_test/rtmw/composed_order | 76 | 0.98684 | 0.00746 | 0.99737 | 4.68241 |
| rtmw-data-r5-tcn-u97-seed42 | actual_REAL17_full/mediapipe/sentence | 3015 | 0.98541 | 0.00442 | 0.99592 | 2.25013 |
| rtmw-data-r5-tcn-u97-seed42 | actual_REAL17_vocabulary_covered/mediapipe/sentence | 3015 | 0.98541 | 0.00442 | 0.99592 | 2.25013 |
| rtmw-data-r5-tcn-u97-seed42 | actual_REAL17_full/mediapipe/emergency_word | 315 | 0.86984 | 0.13016 | 0.90550 | 2.06245 |
| rtmw-data-r5-tcn-u97-seed42 | actual_REAL17_vocabulary_covered/mediapipe/emergency_word | 315 | 0.86984 | 0.13016 | 0.90550 | 2.06245 |
| rtmw-data-r5-tcn-u97-seed42 | actual_REAL17_full/dwpose/sentence | 3015 | 0.96650 | 0.01016 | 0.99216 | 2.05142 |
| rtmw-data-r5-tcn-u97-seed42 | actual_REAL17_vocabulary_covered/dwpose/sentence | 3015 | 0.96650 | 0.01016 | 0.99216 | 2.05142 |
| rtmw-data-r5-tcn-u97-seed42 | actual_REAL17_full/dwpose/emergency_word | 315 | 0.88571 | 0.11746 | 0.91850 | 1.99615 |
| rtmw-data-r5-tcn-u97-seed42 | actual_REAL17_vocabulary_covered/dwpose/emergency_word | 315 | 0.88571 | 0.11746 | 0.91850 | 1.99615 |
| rtmw-data-r5-tcn-u97-seed42 | actual_REAL17_full/rtmw/sentence | 3015 | 0.98839 | 0.00352 | 0.99626 | 2.06917 |
| rtmw-data-r5-tcn-u97-seed42 | actual_REAL17_vocabulary_covered/rtmw/sentence | 3015 | 0.98839 | 0.00352 | 0.99626 | 2.06917 |
| rtmw-data-r5-tcn-u97-seed42 | actual_REAL17_full/rtmw/emergency_word | 315 | 0.91111 | 0.08889 | 0.93238 | 1.98275 |
| rtmw-data-r5-tcn-u97-seed42 | actual_REAL17_vocabulary_covered/rtmw/emergency_word | 315 | 0.91111 | 0.08889 | 0.93238 | 1.98275 |
| rtmw-data-r5-tcn-u97-seed42 | synthetic_diagnostic_dev/dwpose/composed_order | 86 | 0.95349 | 0.01311 | 0.99569 | 4.45092 |
| rtmw-data-r5-tcn-u97-seed42 | synthetic_diagnostic_dev/rtmw/composed_order | 85 | 0.96471 | 0.00993 | 0.99763 | 4.03038 |
| rtmw-data-r5-tcn-u97-seed42 | synthetic_diagnostic_test/dwpose/composed_order | 74 | 0.98649 | 0.00385 | 1.00000 | 2.21096 |
| rtmw-data-r5-tcn-u97-seed42 | synthetic_diagnostic_test/rtmw/composed_order | 76 | 1.00000 | 0.00000 | 1.00000 | 2.02929 |
| rtmw-data-r3-bilstm-u97-seed123 | actual_REAL17_full/mediapipe/sentence | 3015 | 0.97114 | 0.00965 | 0.99443 | 4.03395 |
| rtmw-data-r3-bilstm-u97-seed123 | actual_REAL17_vocabulary_covered/mediapipe/sentence | 3015 | 0.97114 | 0.00965 | 0.99443 | 4.03395 |
| rtmw-data-r3-bilstm-u97-seed123 | actual_REAL17_full/mediapipe/emergency_word | 315 | 0.97460 | 0.02540 | 0.97518 | 3.03542 |
| rtmw-data-r3-bilstm-u97-seed123 | actual_REAL17_vocabulary_covered/mediapipe/emergency_word | 315 | 0.97460 | 0.02540 | 0.97518 | 3.03542 |
| rtmw-data-r3-bilstm-u97-seed123 | actual_REAL17_full/dwpose/sentence | 3015 | 0.94527 | 0.01750 | 0.98487 | 3.97171 |
| rtmw-data-r3-bilstm-u97-seed123 | actual_REAL17_vocabulary_covered/dwpose/sentence | 3015 | 0.94527 | 0.01750 | 0.98487 | 3.97171 |
| rtmw-data-r3-bilstm-u97-seed123 | actual_REAL17_full/dwpose/emergency_word | 315 | 0.96825 | 0.03175 | 0.96936 | 2.94061 |
| rtmw-data-r3-bilstm-u97-seed123 | actual_REAL17_vocabulary_covered/dwpose/emergency_word | 315 | 0.96825 | 0.03175 | 0.96936 | 2.94061 |
| rtmw-data-r3-bilstm-u97-seed123 | actual_REAL17_full/rtmw/sentence | 3015 | 0.96982 | 0.00995 | 0.99126 | 3.99691 |
| rtmw-data-r3-bilstm-u97-seed123 | actual_REAL17_vocabulary_covered/rtmw/sentence | 3015 | 0.96982 | 0.00995 | 0.99126 | 3.99691 |
| rtmw-data-r3-bilstm-u97-seed123 | actual_REAL17_full/rtmw/emergency_word | 315 | 0.97460 | 0.02540 | 0.97416 | 3.18404 |
| rtmw-data-r3-bilstm-u97-seed123 | actual_REAL17_vocabulary_covered/rtmw/emergency_word | 315 | 0.97460 | 0.02540 | 0.97416 | 3.18404 |
| rtmw-data-r3-bilstm-u97-seed123 | synthetic_diagnostic_dev/dwpose/composed_order | 86 | 0.98837 | 0.00328 | 0.98889 | 4.57936 |
| rtmw-data-r3-bilstm-u97-seed123 | synthetic_diagnostic_dev/rtmw/composed_order | 85 | 0.97647 | 0.00662 | 0.98559 | 4.37507 |
| rtmw-data-r3-bilstm-u97-seed123 | synthetic_diagnostic_test/dwpose/composed_order | 74 | 0.95946 | 0.01538 | 0.98669 | 4.63191 |
| rtmw-data-r3-bilstm-u97-seed123 | synthetic_diagnostic_test/rtmw/composed_order | 76 | 0.97368 | 0.00746 | 0.98817 | 4.69236 |
| rtmw-data-r3-bilstm-u97-seed2026 | actual_REAL17_full/mediapipe/sentence | 3015 | 0.97413 | 0.00875 | 0.99468 | 4.02995 |
| rtmw-data-r3-bilstm-u97-seed2026 | actual_REAL17_vocabulary_covered/mediapipe/sentence | 3015 | 0.97413 | 0.00875 | 0.99468 | 4.02995 |
| rtmw-data-r3-bilstm-u97-seed2026 | actual_REAL17_full/mediapipe/emergency_word | 315 | 0.94921 | 0.05079 | 0.95363 | 3.12028 |
| rtmw-data-r3-bilstm-u97-seed2026 | actual_REAL17_vocabulary_covered/mediapipe/emergency_word | 315 | 0.94921 | 0.05079 | 0.95363 | 3.12028 |
| rtmw-data-r3-bilstm-u97-seed2026 | actual_REAL17_full/dwpose/sentence | 3015 | 0.94992 | 0.01689 | 0.98779 | 4.09198 |
| rtmw-data-r3-bilstm-u97-seed2026 | actual_REAL17_vocabulary_covered/dwpose/sentence | 3015 | 0.94992 | 0.01689 | 0.98779 | 4.09198 |
| rtmw-data-r3-bilstm-u97-seed2026 | actual_REAL17_full/dwpose/emergency_word | 315 | 0.97460 | 0.02540 | 0.97606 | 3.09408 |
| rtmw-data-r3-bilstm-u97-seed2026 | actual_REAL17_vocabulary_covered/dwpose/emergency_word | 315 | 0.97460 | 0.02540 | 0.97606 | 3.09408 |
| rtmw-data-r3-bilstm-u97-seed2026 | actual_REAL17_full/rtmw/sentence | 3015 | 0.97081 | 0.00965 | 0.99310 | 4.03184 |
| rtmw-data-r3-bilstm-u97-seed2026 | actual_REAL17_vocabulary_covered/rtmw/sentence | 3015 | 0.97081 | 0.00965 | 0.99310 | 4.03184 |
| rtmw-data-r3-bilstm-u97-seed2026 | actual_REAL17_full/rtmw/emergency_word | 315 | 0.97460 | 0.02540 | 0.96800 | 2.95307 |
| rtmw-data-r3-bilstm-u97-seed2026 | actual_REAL17_vocabulary_covered/rtmw/emergency_word | 315 | 0.97460 | 0.02540 | 0.96800 | 2.95307 |
| rtmw-data-r3-bilstm-u97-seed2026 | synthetic_diagnostic_dev/dwpose/composed_order | 86 | 1.00000 | 0.00000 | 1.00000 | 4.54581 |
| rtmw-data-r3-bilstm-u97-seed2026 | synthetic_diagnostic_dev/rtmw/composed_order | 85 | 0.97647 | 0.00662 | 0.99671 | 4.44178 |
| rtmw-data-r3-bilstm-u97-seed2026 | synthetic_diagnostic_test/dwpose/composed_order | 74 | 0.95946 | 0.01154 | 0.96919 | 4.66600 |
| rtmw-data-r3-bilstm-u97-seed2026 | synthetic_diagnostic_test/rtmw/composed_order | 76 | 0.96053 | 0.01119 | 0.96931 | 4.56744 |

지연은 동일 GPU의 batch1 특징 입력→모델→greedy decode이며 원본 추출/네트워크/LLM 시간을 제외한다. MacroF1은 해당 평가 참조에 등장하는 라벨 기준이며 전체 E49 학습 지원은 input-audit.json에서 별도 검증한다. 개별 예측·라벨별/위치별 재현율·REAL06 보정 지표·시드별 결과를 저장한다.

## 이전 모델과 비교

기존 standing C1 BiLSTM seed42를 사전 기준으로 사용한다. 기존 모델의 U98에는 감독0건 다리가 포함되고 새 전체어휘 U97에는 이를 제외했지만, 동일 REAL17 실제 정답 라벨은 같다. 예전 모델의 RTMW confidence는 미보정이므로 새 자체 보정 결과와 혼동하지 않는다.

| 이전 기준 | 입력 | 문장WER | E49단어WER |
|---|---|---:|---:|
| 기존 C1 BiLSTM seed42 | mediapipe | 0.00573 | 0.06667 |
| 기존 C1 BiLSTM seed42 | dwpose | 0.01086 | 0.05397 |

## 시드 재확인

- R3/mediapipe/sentence Test WER: 0.781% ± 0.245%p (3seed).
- R3/mediapipe/emergency_word Test WER: 3.386% ± 1.466%p (3seed).
- R3/dwpose/sentence Test WER: 1.535% ± 0.321%p (3seed).
- R3/dwpose/emergency_word Test WER: 2.751% ± 0.367%p (3seed).
- R3/rtmw/sentence Test WER: 0.821% ± 0.276%p (3seed).
- R3/rtmw/emergency_word Test WER: 2.222% ± 0.550%p (3seed).

## 원격 등록

새 후보 8개를 기존40개에 추가했다. `rtmw-candidates`=전체 새 후보, `rtmw-candidate`=REAL08/예약dev로 고른 잠정 후보 `rtmw-data-r3-bilstm-u97-seed42`. 서비스 `release`는 유지한다. RTMW는 새 모델별 실제 RTMW REAL06 보정 및 REAL08 임계값을 사용하며 hybrid는 미보정으로 남긴다. 기존40모델/프로필은 변경하지 않는다.

서버26개·클라이언트7개 검사와 32개 모델·추출기 strict load/Gloss 배열, 576개 SDK/고정 평가 일치 검사를 통과했다. 체크포인트는 GPU 서버 학습 폴더에 저장하고 Git에는 넣지 않는다. 입력 단어/문장은 같은 CTC에서 Gloss 배열을 출력한다. 신체 다리는 미학습이다.

원자료 분리·E49 양성 지원·설정 및 학습곡선은 rtmw_experiments.json, 라벨/위치별·보정·전체/지원어휘 점수는 rtmw_metrics.json, 표는 rtmw_benchmark.csv, 원격 검증은 validation-rtmw.json에 있다.
