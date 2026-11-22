# standing_and_data_benchmarking

상태: 완료 · 2026-11-22T12:30:31.625616+00:00

data.md·keypoint_standing_result.md의 새 자료를 실제 학습에 연결한다. U98은98글로스+blank=99출력이며 신체 다리는 감독0건인 예비 클래스다. 단어와 문장은 같은 CTC를 사용한다.
새 초기 가중치·FP32·batch8·AdamW3e-4·고정16epoch·epoch당41924노출(5241 step)을 맞춘다. S0/C0/C1/C2의 BiLSTM seed42 초기값은 같고, TCN은 구조 비교다. 실제 MP/DW는 전체 시퀀스를 교대하고 합성은 DW만 존재한다.
S0=같은601개의 기존 시작/끝 미복원, C0=차렷 복원601, C1=새1000순서2030표본, C2=C1+동일 인코더/CTC를 짧은 창에 공유하는0.1 보조CTC. 보조 경로는 추론에 필요 없다.
기본 실제 문장70%·E49 고립단어20%·합성10%다. 유력 조건에 합성15%를 추가하고 최상위 새 조건에 seed123/2026을 확인해 최대8회로 제한한다. ST-GCN은 이전 결과를 바탕으로 이번 후보에서 제외했다.
REAL06 보정·REAL08 실제 유지 검증·기존REAL17 Test를 사용한다. 체크포인트는0.35×REAL08 문장WER+0.25×E49 단어오류+0.40×예약 diagnostic-dev WER로 선택한다. 가중치는 이번 실험의 고정 가설이다.
조건 선택은 C0 대비 각 추출기 REAL08 문장WER+0.3%p 가드와 diagnostic-dev를 우선한다. REAL17·diagnostic-test·기존 사용자 영상은 설정/체크포인트 선정에 쓰지 않는다. 합성 진단은 Train 조각을 재사용하므로 실제 카메라 일반화 성능이 아니다.
기존 예약33순서와 새100순서를 Train에서 제외했다. 별도 실제 camera-dev/test 수집이 없어 실제 미학습 응급 연속 문장 점수는N/A이며 등록 모델은provisional이다. 현재 서비스 기본 모델은 자동 교체하지 않는다.
새 합성은 순서별1~2명·최대2각도로 제한돼 모든 순서에14명×5각도가 있는 자료는 아니다. 전체 Train14명·5각도를 포함하며 양끝 차렷은 자동 후보, 의미/자연스러움은 사람 검수pending이다. 합성 오른쪽 라벨은 빠지지만 실제 E49 재생에는 유지한다. 보간 기하 경고는 데이터 보고서를 따른다.
quality는mean(clip(detector_score,0,1)*mask)로 학습·평가·원격추론을 맞춘다. detector score를 인식 confidence로 사용하지 않는다. confidence는 새 모델별REAL06으로 다시 보정한다. hybrid/RTMW는 미보정 비교용 입력이다.

| 실행 | 상태 | 완료/최선epoch | 학습분 | C0 가드 |
|---|---|---:|---:|---|
| standing-data-s0-bilstm-s10-fullctc-u98-seed42 | 완료 | 16/10 | 20.4 | True |
| standing-data-c0-bilstm-s10-fullctc-u98-seed42 | 완료 | 16/15 | 20.8 | True |
| standing-data-c1-bilstm-s10-fullctc-u98-seed42 | 완료 | 16/16 | 21.4 | True |
| standing-data-c2-bilstm-s10-localctc-u98-seed42 | 완료 | 16/15 | 33.5 | True |
| standing-data-c1-tcn-s10-fullctc-u98-seed42 | 완료 | 16/14 | 17.1 | False |
| standing-data-c1-bilstm-s15-fullctc-u98-seed42 | 완료 | 16/14 | 22.5 | True |
| standing-data-c1-bilstm-s10-fullctc-u98-seed123 | 완료 | 16/14 | 22.3 | True |
| standing-data-c1-bilstm-s10-fullctc-u98-seed2026 | 완료 | 16/16 | 22.3 | False |

## 실제 Test와 합성 진단 결과

| 모델 | 범위·입력·과제 | n | 완전일치 | WER | MacroF1 | p95 ms |
|---|---|---:|---:|---:|---:|---:|
| standing-data-s0-bilstm-s10-fullctc-u98-seed42 | actual_REAL17/mediapipe/sentence | 3015 | 0.96352 | 0.01116 | 0.98944 | 3.96554 |
| standing-data-s0-bilstm-s10-fullctc-u98-seed42 | actual_REAL17/mediapipe/emergency_word | 315 | 0.90794 | 0.09524 | 0.92858 | 2.91077 |
| standing-data-s0-bilstm-s10-fullctc-u98-seed42 | actual_REAL17/dwpose/sentence | 3015 | 0.95456 | 0.01388 | 0.98574 | 3.98024 |
| standing-data-s0-bilstm-s10-fullctc-u98-seed42 | actual_REAL17/dwpose/emergency_word | 315 | 0.93333 | 0.07619 | 0.94345 | 2.92266 |
| standing-data-s0-bilstm-s10-fullctc-u98-seed42 | synthetic_diagnostic_dev/dwpose/composed_order | 91 | 0.00000 | 0.80495 | 0.26703 | 4.72670 |
| standing-data-s0-bilstm-s10-fullctc-u98-seed42 | synthetic_diagnostic_test/dwpose/composed_order | 78 | 0.00000 | 0.81091 | 0.26845 | 4.74289 |
| standing-data-c0-bilstm-s10-fullctc-u98-seed42 | actual_REAL17/mediapipe/sentence | 3015 | 0.96119 | 0.01217 | 0.98988 | 3.89714 |
| standing-data-c0-bilstm-s10-fullctc-u98-seed42 | actual_REAL17/mediapipe/emergency_word | 315 | 0.94603 | 0.05397 | 0.94638 | 2.87540 |
| standing-data-c0-bilstm-s10-fullctc-u98-seed42 | actual_REAL17/dwpose/sentence | 3015 | 0.95290 | 0.01468 | 0.98908 | 3.88700 |
| standing-data-c0-bilstm-s10-fullctc-u98-seed42 | actual_REAL17/dwpose/emergency_word | 315 | 0.95556 | 0.04444 | 0.95975 | 2.90493 |
| standing-data-c0-bilstm-s10-fullctc-u98-seed42 | synthetic_diagnostic_dev/dwpose/composed_order | 91 | 0.08791 | 0.49226 | 0.59603 | 4.53293 |
| standing-data-c0-bilstm-s10-fullctc-u98-seed42 | synthetic_diagnostic_test/dwpose/composed_order | 78 | 0.11538 | 0.42182 | 0.66421 | 4.74125 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed42 | actual_REAL17/mediapipe/sentence | 3015 | 0.98209 | 0.00573 | 0.99526 | 3.90203 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed42 | actual_REAL17/mediapipe/emergency_word | 315 | 0.93333 | 0.06667 | 0.94171 | 2.89914 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed42 | actual_REAL17/dwpose/sentence | 3015 | 0.96584 | 0.01086 | 0.99055 | 3.90837 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed42 | actual_REAL17/dwpose/emergency_word | 315 | 0.94603 | 0.05397 | 0.95786 | 2.89133 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed42 | synthetic_diagnostic_dev/dwpose/composed_order | 91 | 0.98901 | 0.00310 | 0.98710 | 4.56152 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed42 | synthetic_diagnostic_test/dwpose/composed_order | 78 | 0.98718 | 0.00364 | 0.99833 | 4.50890 |
| standing-data-c2-bilstm-s10-localctc-u98-seed42 | actual_REAL17/mediapipe/sentence | 3015 | 0.97645 | 0.00754 | 0.99266 | 3.90317 |
| standing-data-c2-bilstm-s10-localctc-u98-seed42 | actual_REAL17/mediapipe/emergency_word | 315 | 0.97143 | 0.02857 | 0.98035 | 2.91356 |
| standing-data-c2-bilstm-s10-localctc-u98-seed42 | actual_REAL17/dwpose/sentence | 3015 | 0.95721 | 0.01357 | 0.98799 | 3.88471 |
| standing-data-c2-bilstm-s10-localctc-u98-seed42 | actual_REAL17/dwpose/emergency_word | 315 | 0.96508 | 0.03492 | 0.97069 | 2.89105 |
| standing-data-c2-bilstm-s10-localctc-u98-seed42 | synthetic_diagnostic_dev/dwpose/composed_order | 91 | 0.97802 | 0.00619 | 0.99645 | 4.57908 |
| standing-data-c2-bilstm-s10-localctc-u98-seed42 | synthetic_diagnostic_test/dwpose/composed_order | 78 | 0.97436 | 0.00727 | 0.99478 | 4.49679 |
| standing-data-c1-tcn-s10-fullctc-u98-seed42 | actual_REAL17/mediapipe/sentence | 3015 | 0.98010 | 0.00623 | 0.99461 | 2.03985 |
| standing-data-c1-tcn-s10-fullctc-u98-seed42 | actual_REAL17/mediapipe/emergency_word | 315 | 0.84762 | 0.15556 | 0.90002 | 2.04809 |
| standing-data-c1-tcn-s10-fullctc-u98-seed42 | actual_REAL17/dwpose/sentence | 3015 | 0.96517 | 0.01116 | 0.99065 | 2.03908 |
| standing-data-c1-tcn-s10-fullctc-u98-seed42 | actual_REAL17/dwpose/emergency_word | 315 | 0.86667 | 0.13968 | 0.89177 | 2.00999 |
| standing-data-c1-tcn-s10-fullctc-u98-seed42 | synthetic_diagnostic_dev/dwpose/composed_order | 91 | 0.95604 | 0.01238 | 0.99283 | 4.42803 |
| standing-data-c1-tcn-s10-fullctc-u98-seed42 | synthetic_diagnostic_test/dwpose/composed_order | 78 | 0.96154 | 0.01455 | 0.99174 | 4.39658 |
| standing-data-c1-bilstm-s15-fullctc-u98-seed42 | actual_REAL17/mediapipe/sentence | 3015 | 0.98010 | 0.00674 | 0.99207 | 3.97120 |
| standing-data-c1-bilstm-s15-fullctc-u98-seed42 | actual_REAL17/mediapipe/emergency_word | 315 | 0.94921 | 0.05079 | 0.95922 | 2.92135 |
| standing-data-c1-bilstm-s15-fullctc-u98-seed42 | actual_REAL17/dwpose/sentence | 3015 | 0.96517 | 0.01176 | 0.98786 | 3.95468 |
| standing-data-c1-bilstm-s15-fullctc-u98-seed42 | actual_REAL17/dwpose/emergency_word | 315 | 0.94286 | 0.05714 | 0.94857 | 2.93850 |
| standing-data-c1-bilstm-s15-fullctc-u98-seed42 | synthetic_diagnostic_dev/dwpose/composed_order | 91 | 0.98901 | 0.00310 | 0.99937 | 4.64120 |
| standing-data-c1-bilstm-s15-fullctc-u98-seed42 | synthetic_diagnostic_test/dwpose/composed_order | 78 | 1.00000 | 0.00000 | 1.00000 | 4.63480 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed123 | actual_REAL17/mediapipe/sentence | 3015 | 0.98242 | 0.00533 | 0.99390 | 3.97258 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed123 | actual_REAL17/mediapipe/emergency_word | 315 | 0.95238 | 0.04762 | 0.95224 | 2.93482 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed123 | actual_REAL17/dwpose/sentence | 3015 | 0.96849 | 0.00975 | 0.98792 | 3.94830 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed123 | actual_REAL17/dwpose/emergency_word | 315 | 0.95556 | 0.04444 | 0.95419 | 2.91620 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed123 | synthetic_diagnostic_dev/dwpose/composed_order | 91 | 1.00000 | 0.00000 | 1.00000 | 4.62940 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed123 | synthetic_diagnostic_test/dwpose/composed_order | 78 | 0.98718 | 0.00364 | 1.00000 | 4.61897 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed2026 | actual_REAL17/mediapipe/sentence | 3015 | 0.97313 | 0.00855 | 0.99284 | 3.97045 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed2026 | actual_REAL17/mediapipe/emergency_word | 315 | 0.95556 | 0.04444 | 0.95586 | 2.94315 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed2026 | actual_REAL17/dwpose/sentence | 3015 | 0.95655 | 0.01368 | 0.98909 | 3.96110 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed2026 | actual_REAL17/dwpose/emergency_word | 315 | 0.95238 | 0.04762 | 0.95838 | 2.93346 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed2026 | synthetic_diagnostic_dev/dwpose/composed_order | 91 | 0.96703 | 0.00929 | 0.99443 | 4.64044 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed2026 | synthetic_diagnostic_test/dwpose/composed_order | 78 | 0.98718 | 0.00364 | 0.99937 | 4.55010 |

GPU batch1 p95는 특징 입력부터 모델·greedy decode까지이며 추출·촬영·네트워크·LLM을 포함하지 않는다. 학습 중 다른 GPU 작업의 부하가 있으면 단독 지연 결과로 해석하지 않는다.
개별 standing-benchmark.json에는 첫/중간/끝 토큰 재현율·라벨별 누락, 각 추출기의 REAL08 가드와 원본 prediction이 있다. seed1개 탐색과3seed 확인을 구분한다.

기존 데이터·가중치·완료 결과를 보존하고 새 버전으로 저장한다. 완료 모델은 별도 원격 테스트 묶음에 추가한다.

## 원격 등록 및 최종 해석

완료 후보 8개를 기존32개에 추가했다. `standing`은 새 후보 전체, `standing-candidate`는 이번 검증의 잠정 후보다. `native32`와 `release`는 기존 목록을 유지하고 `all`은 전체를 선택한다.
잠정 후보: `standing-data-c1-bilstm-s10-fullctc-u98-seed42`. 새 실제 카메라 검증이 없으므로 서비스 기본 모델 채택은 보류한다.
원격 검증: 32개 모델·추출기 조합 strict load 및 Gloss 배열 검사, 384개 SDK/고정 평가 일치 검사 통과. 서버19개·클라이언트7개 검증 통과.
체크포인트는 GPU 서버에 저장했다. Git에는 모델 ID·SHA256·설정·평가 결과·등록 코드를 저장하며 .pt·촬영 영상·API key는 넣지 않는다. 클라이언트와 서버의 같은 브랜치 변경을 함께 적용한다.
가드를 통과하지 못한 모델도 비교용으로 등록하고 해당 상태를 공개 메타데이터에 표시한다. S0와 C0는 가드 기준 대조군이므로 표의 True를 개선 판정으로 읽지 않는다. 후보 가드는 REAL08 문장 유지 검사이며 응급 연속 문장 정확도를 입증하지 않는다.
실제 차렷 시작/즉시 시작을 짝지은 새 camera-dev/test가 없으므로 그 시작 조건별 개선 점수는 N/A다. 차렷만 유지하는 무수어 영상의 오방출률도 N/A이며 이번 데이터만으로 확인했다고 주장하지 않는다.
REAL06 confidence 보정이 새 응급 연속 문장에서도 정확하게 보정된다는 뜻은 아니다. 차렷에는 확정된 프레임 unknown 정답이 없으며 CTC blank 정렬을 학습할 기회만 추가했다. 이 버전으로 unknown 헤드가 개선됐다고 단정하지 않는다.
데이터 audit 안의 training_executed=false는 이전 데이터 구축 시점의 불변 검수 영수증이다. 이번 학습 실행은 각 result/history 및 standing_experiments.json의 실제16epoch 기록으로 확인한다.
Macro F1은 각 평가 범위 정답에 등장하는 글로스의 정렬 기반 평균이다. 응급 고립단어와 실제 문장·합성 순서의 표본 및 분모가 다르므로 점수를 하나로 합치지 않는다. confidence/is_question은 기존 실제 감독과 새 모델별 보정 결과를 사용하며, 자동 차렷 구간을 unknown 정답이나 질문 정답으로 확정하지 않았다.
배포 검증용 기존 AI Hub 영상과 고정 Test 일치 검사는 코드 호환성 검사다. 기존 사용자 목→통증 영상은 반복 분석했던 자료여서 이번 후보 선정이나 독립 Test에 사용하지 않았다.

### 토큰 위치 및 confidence·질문 평가

| 모델 | 입력 | Test 첫/중간/끝 토큰 recall | confidence ECE | 질문 F1 |
|---|---|---|---:|---:|
| standing-data-s0-bilstm-s10-fullctc-u98-seed42 | mediapipe | 0.99370 / 0.99034 / 0.98925 | 0.02224 | 0.72941 |
| standing-data-s0-bilstm-s10-fullctc-u98-seed42 | dwpose | 0.99370 / 0.98889 / 0.98136 | 0.01793 | 0.70000 |
| standing-data-c0-bilstm-s10-fullctc-u98-seed42 | mediapipe | 0.99270 / 0.99444 / 0.98961 | 0.02584 | 0.76364 |
| standing-data-c0-bilstm-s10-fullctc-u98-seed42 | dwpose | 0.99005 / 0.99396 / 0.98674 | 0.01522 | 0.75145 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed42 | mediapipe | 0.99602 / 0.99614 / 0.99247 | 0.01227 | 0.77612 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed42 | dwpose | 0.99237 / 0.99275 / 0.98530 | 0.01982 | 0.83019 |
| standing-data-c2-bilstm-s10-localctc-u98-seed42 | mediapipe | 0.99768 / 0.99155 / 0.99140 | 0.01116 | 0.69512 |
| standing-data-c2-bilstm-s10-localctc-u98-seed42 | dwpose | 0.99370 / 0.98599 / 0.98495 | 0.01797 | 0.70659 |
| standing-data-c1-tcn-s10-fullctc-u98-seed42 | mediapipe | 0.99536 / 0.99662 / 0.99355 | 0.00692 | 0.82418 |
| standing-data-c1-tcn-s10-fullctc-u98-seed42 | dwpose | 0.99038 / 0.99396 / 0.98817 | 0.01449 | 0.84444 |
| standing-data-c1-bilstm-s15-fullctc-u98-seed42 | mediapipe | 0.99735 / 0.99493 / 0.98925 | 0.01147 | 0.88750 |
| standing-data-c1-bilstm-s15-fullctc-u98-seed42 | dwpose | 0.99204 / 0.99372 / 0.98136 | 0.01062 | 0.82895 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed123 | mediapipe | 0.99801 / 0.99638 / 0.99140 | 0.01137 | 0.80000 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed123 | dwpose | 0.99337 / 0.99372 / 0.98674 | 0.01824 | 0.81928 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed2026 | mediapipe | 0.99469 / 0.99444 / 0.98674 | 0.01194 | 0.84810 |
| standing-data-c1-bilstm-s10-fullctc-u98-seed2026 | dwpose | 0.98839 / 0.99275 / 0.98100 | 0.01669 | 0.82803 |

### Seed 확인

seed42 탐색과 선택 조건의 seed123·2026 확인을 구분한다. 아래 평균±표준편차는 같은 최종 조건의 독립3seed를 모두 완료한 경우만 표시한다.
- ('C1', 'bilstm', 0.1, False) / mediapipe / sentence WER: 0.654% ± 0.175%p (3seed).
- ('C1', 'bilstm', 0.1, False) / mediapipe / emergency_word WER: 5.291% ± 1.202%p (3seed).
- ('C1', 'bilstm', 0.1, False) / dwpose / sentence WER: 1.143% ± 0.202%p (3seed).
- ('C1', 'bilstm', 0.1, False) / dwpose / emergency_word WER: 4.868% ± 0.485%p (3seed).

실험 설정·학습 곡선: `standing_experiments.json`; 위치별·라벨별 및 보정 지표: `standing_metrics.json`; 평가표: `standing_benchmark.csv`; 등록 검증: `validation-standing.json`.
