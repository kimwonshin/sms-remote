# 원격 모델 목록 검증 — 2026-11-20

> 아래는 이전 구성의 검증 기록입니다. 현재 활성 20개 구성은 [MODEL_CATALOG.md](MODEL_CATALOG.md)와 [validation-catalog20.json](validation-catalog20.json)을 확인하세요.

기존 30fps 모델 3개 + 초기 native15 12개 + 추가 native15 63개, 총 78개를 등록했다. 새 학습 60회는 등록 대상에 포함하지 않았다. W63 공동학습 9개에는 이전 WORD ID 기준 표시를 붙였다. checkpoint와 추출기별 calibration profile 해시를 검증했으며 가중치를 복사하거나 노트북으로 보내지 않았다.

- 서버 단위 검증 8개, 클라이언트 7개, 총 15개 통과. 경로 입력 거부·목록 alias 확장·FPS 계약·모델 경로 비공개·업로드 해시·중복 제출·안전한 ZIP·재연결을 확인했다.
- REAL17 `NIA_SL_SEN0005_REAL17_F.mp4` 한 편을 사용했다. MediaPipe와 DWPose 각각 기존 30fps는 110프레임, native15는 55프레임을 별도로 추출했다. native15는 학습용 PTS 선택·추출기·canonical 매핑을 재사용했다.
- 추출기별 78개, 총 **156개 모델 예측**에서 순서 있는 gloss 배열을 반환했다. native 150개 예측의 input_frames와 model_frames가 모두 일치했다. checkpoint strict load와 각 profile 해시 검사를 통과했다. needs_review를 정상 확정으로 바꾸지 않았다.
- NVIDIA GeForce RTX 2080 Ti CUDA에서 모델을 실행했다. MediaPipe 추출은 CPU, DWPose 추출은 CUDA다. 기존 추가 학습 서비스를 중단하지 않았다.
- localhost에만 열린 임시 OpenSSH 서버와 임시 시험키로 실제 SSH/SFTP 업로드 → 분리된 서버 worker → 상태 조회 → 78개 모델/두 추출기 실행 → SHA256 ZIP 다운로드 → 안전한 압축 해제 → report.html 수신을 통과했다. 기존 사용자 SSH 키·비밀번호·sshd 설정은 바꾸지 않았다.

실제 외부/VPN 노트북에서의 접속과 Windows 웹캠은 별도 기기에서 검증하지 않았다. 이번 기록은 실행·전송·정합성 검증이며 인식 정확도나 독립 카메라 일반화 평가가 아니다. 촬영 영상에는 정답을 입력하지 않았으므로 정확도 수치를 생성하지 않는다. inference_ms는 동시 학습 중 단일 요청 측정이며 p95 벤치마크가 아니다.
