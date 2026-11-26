# RTMW 포함 E49 단일 CTC 학습 후보

현재 새 후보 학습이 진행 중입니다. 완료 결과는 `rtmw_training_benchmarking.md`와 `rtmw_benchmark.csv`, `rtmw_metrics.json`, `rtmw_experiments.json`, `rtmw_model_selection.json`, `validation-rtmw.json`에 추가합니다. 진행 중 모델은 원격 목록에 등록하지 않습니다.

응급 E49는 모든 후보에 포함합니다. 신체 **다리**는 유효한 양성 영상이 없어 미학습이며 WORD1599(교량)는 사용하지 않습니다. 전체 어휘는 유효한 S50∪E49=97글로스, 축소 조건은 E49+문장 전용25글로스=74글로스입니다. 출력은 공통 lexical CTC 하나이며 문장/단어별 별도 분류가 아닙니다.

| 조건 | 실제 입력 Train | 결합 Train | 모델/어휘 |
|---|---|---|---|
| R0 | RTMW | RTMW | BiLSTM /97 |
| R1 | MP+DW+RTMW | RTMW | BiLSTM /97 |
| R2 | MP+DW+RTMW | DW+RTMW | BiLSTM /97 |
| R3 | R2 동일 | R2 동일 | BiLSTM +공유 localCTC0.1 /97 |
| R4 | R2에서 전체 시퀀스 어휘 필터 | R2 동일 | BiLSTM /74 |
| R5 | R2 동일 | R2 동일 | TCN /97 |

6조건 seed42 후 REAL08/예약dev로 고른 전체 어휘 조건을 seed123·2026으로 확인합니다. RTX2080Ti·FP32·16epoch·epoch41924노출·단어20%·결합10%입니다. 한 UID의 MP/DW/RTMW는 시퀀스 전체를 순환하며 같은 원본을 서로 독립 표본으로 계산하지 않습니다. 축소 문장 라벨은 Train 빈도로만 정하고 E49는 제외하지 않습니다.

REAL06은 모델/추출기 자체 confidence 보정, REAL08은 모델/조건/임계값 선택, 동일 REAL17 3330건(문장3015·단어315)은 최종 Test입니다. 축소 어휘도 전체 Test에서 OOV를 오류로 계산하며 지원 어휘 하위점수는 별도입니다. 결합 예약 진단은 공통 지원 순서에서 측정하고 실제 카메라 정확도와 구분합니다. 새로운 실제 미학습 순서 카메라 검증이 없어 잠정 후보입니다.

학습의 UNKNOWN은 기존 MP/DW와 맞춘 자동 weak gap opt-in이며 검수된 neutral 정답이 아닙니다. 단어/합성은 UNKNOWN 무감독(-1), 질문은 원본 유효 라벨, confidence는 모델별 REAL06 보정입니다. quality는 detector score×observed mask 평균으로 추론까지 맞춥니다.

완료·검증 후 `rtmw-candidates`로 새 후보 전체, `rtmw-candidate`로 잠정 후보를 선택할 수 있습니다. 기존40개와 `release`는 유지합니다. 새 RTMW 프로필은 자기 체크포인트·자기 RTMW REAL06/08 자료의 해시 근거가 있어야 fitted로 인정하며, 기존 모델의 미보정 RTMW와 hybrid는 null confidence 정책을 유지합니다.

코드 pull만으로 가중치가 생성되지는 않습니다. 체크포인트는 GPU 서버 학습 경로에 보존하고 Git에 넣지 않으며, 원격 catalog 등록 완료 후 같은 서버에서 테스트합니다. 등록은 `extend_rtmw_registry.py --base-registry ... --runs-root ... --selection ... --output ... --inputs-root ...`가 모든 필수 응급 라벨의 양성 지원·16epoch·체크포인트 해시·단일 CTC를 검증한 뒤 수행합니다.
