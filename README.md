# SMS 원격 수어 분석 — 노트북 프로그램

## 원격 테스트 모델 20개

기존 75개 중 선정한 **후보 10개**와 새로 완료한 **10개**, 총 20개를 비교합니다. 기본 선택은 **통합 98라벨 BiLSTM seed2026**입니다. `추천 통합 BiLSTM`, `기존 후보 10개`, `신규 10개`, `전체 20개` 묶음 또는 서버 목록의 개별 모델을 선택하세요.

모든 활성 모델은 MediaPipe 또는 DWPose **직접 15fps** 입력입니다. 기존 S50은 문장 50어휘, 신규 U98은 문장+응급 단어 통합 98어휘, 신규 E50 대조군은 응급 단어 전용 50어휘입니다. E50은 문장 번역 모델이 아니며, 기존 모델의 단어 보조 헤드는 응급 단어 Gloss 출력에 사용되지 않습니다.

```bash
python remote_client.py --list-models --password
python remote_client.py --video sentence.mp4 --extractors mediapipe dwpose --models new10 --password --open-report
python remote_client.py --video sentence.mp4 --extractors mediapipe --models old10 --password --open-report
python remote_client.py --video sentence.mp4 --extractors mediapipe dwpose --models all --password --open-report
python remote_client.py --video sentence.mp4 --extractors mediapipe --models release --password --open-report
```

`all`/`native20`은 20개, `old10`과 `new10`은 각각 10개, `release`는 추천 통합 BiLSTM 1개입니다. 이전 `native75`/`legacy` 묶음과 제외된 개별 ID는 더 이상 활성 목록에서 실행하지 않습니다. 모델 가중치와 원래 학습 결과는 서버에 보존합니다. 목록·선정 근거는 [MODEL_CATALOG.md](MODEL_CATALOG.md), 고정 ID는 [model_selection.json](model_selection.json), 완료 Test 결과는 [benchmark.csv](benchmark.csv)에 있습니다.

클라이언트와 sms-my 서버를 함께 업데이트하세요. 기존 `client-config.json`·SSH 키·녹화본·반환 결과는 유지합니다. 가중치는 클라이언트에 받지 않습니다. 실제 모델 목록은 서버의 `--list-models` 응답을 기준으로 확인합니다.

반환 보고서는 순서 있는 Gloss, confidence, 질문 여부, 입력 프레임 수, 보정 상태와 모델의 출력 어휘 범위를 제공합니다. 정답 없는 촬영 영상의 정확도를 만들어 표시하지 않습니다. AIHub REAL06 기준 confidence 보정이 전시장 카메라 환경에서도 검증된 확률을 뜻하지는 않습니다.

노트북에서는 **웹캠 녹화와 영상 전송만** 합니다. GPU 컴퓨터에서 키포인트와 문장 모델을 실행하고, 비교 보고서·결과 영상·좌표·예측 JSON을 다시 노트북에 저장합니다. 노트북에 Torch·MediaPipe·가중치를 설치할 필요가 없습니다.

## Windows에서 시작

1. 이 저장소를 노트북에 내려받습니다. Python **3.10~3.12**를 설치합니다(권장 3.11, Tcl/Tk 포함).
2. `setup.cmd`를 실행해 촬영·SSH 전송에 필요한 패키지를 설치합니다.
3. `remote_test.cmd`를 실행합니다.
4. 서버 주소, SSH 포트, 사용자 이름을 확인하고 SSH 비밀번호 또는 개인키 경로를 입력합니다. 기본 주소 `gpu-server.example.com`는 예시값입니다. 실제 서버 주소로 변경하세요. 노트북도 같은 VPN에 연결돼 있어야 합니다. 일반 SSH 접속이 가능해야 하며, 원격 데스크톱 연결만으로는 충분하지 않습니다.
5. 원하는 추출기와 수어 모델을 선택하고 **촬영·전송·분석 시작**을 누릅니다.
6. 카메라 창에서 **Space 시작 → 수어 수행 → Space 종료**합니다. 한 번 촬영한 원본으로 선택한 분석을 모두 실행합니다.
7. 전송·분석이 끝나면 받은 보고서가 자동으로 열립니다. 인터넷 연결 없이도 결과 영상을 볼 수 있습니다.

처음 연결하면 SSH 서버 지문 확인 창이 뜹니다. 서버에서 다음 명령으로 확인한 지문과 같은지 비교하고 연결하세요. 이미 저장된 서버 키가 바뀌면 자동으로 신뢰하지 않습니다.

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256
```

비밀번호와 개인키 암호는 디스크에 저장하지 않습니다. 주소·사용자·개인키 위치는 `client-config.json`에 저장합니다. 개인키 자체와 설정·녹화본·보고서는 Git에 올리지 않습니다. 비밀번호 대신 SSH agent 또는 개인키를 사용할 수 있습니다.

## 촬영과 분석

30fps, 640×480을 요청하며 최대 60초를 촬영합니다. 실제 수집 속도가 27fps 미만이면 분석을 중단하고 촬영 원본은 보존합니다. 화면 미리보기만 좌우 반전하며 서버 입력 영상은 반전하지 않습니다. `r`은 다시 촬영, `q`/ESC는 취소입니다. 미리 녹화한 MP4·AVI 파일도 선택할 수 있습니다. 영상 한 개를 문장 하나로 처리합니다.

기본 분석은 MediaPipe 직접 15fps + 통합 98라벨 BiLSTM입니다. 활성 20개는 MediaPipe·DWPose로 비교합니다. RTMW·hybrid·30fps는 현재 모델 목록의 입력 계약에 포함되지 않습니다. **MediaPipe 키포인트 추출은 서버 CPU**, 나머지 ONNX 추출과 모든 문장 모델 추론은 서버 GPU를 사용합니다.

모델 결과는 순서가 있는 gloss와 confidence·질문 판별입니다. 별도의 자연어 문장 생성은 하지 않습니다. 정답 없이 측정한 손 검출률은 인식 정확도가 아니며, confidence 보정과 입력 도메인의 검토 상태는 보고서에 그대로 표시됩니다.

## 저장 위치와 연결 복구

- `recordings/`: 노트북 촬영 원본과 촬영 속도 기록
- `results/<작업번호>/job.json`: 다시 연결할 작업 정보
- `results/<작업번호>/result.zip`: 서버에서 받은 원본 결과 묶음
- `results/<작업번호>/result/report.html`: 오프라인 비교 보고서
- `results/<작업번호>/result/<추출기>/`: 키포인트 MP4, 좌표·특징 NPZ, 예측·측정 JSON

서버는 시작된 분석을 노트북 연결이 끊겨도 계속합니다. **기존 작업 다시 연결**을 누르고 이전 `job.json`을 선택하면 진행 상황을 확인하거나 완성된 결과를 받습니다. 같은 작업을 다시 분석하지 않습니다. 업로드가 끊겼다면 같은 원본을 다시 전송합니다. 다운로드가 끊겼다면 결과를 다시 받습니다. 재연결 전에 주소·사용자·서버 프로그램 설정을 바꾸지 마세요.

서버가 실패한 경우 로그도 노트북으로 받습니다. 서버 재부팅으로 분석이 중단됐다면 새 작업으로 제출합니다. 영상과 결과는 자동 삭제하지 않습니다.

## 명령줄 / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp client-config.example.json client-config.json
# client-config.json의 서버 주소·사용자·개인키 경로를 설정
python remote_client.py --camera 0 --password --open-report
python remote_client.py --video sentence.mp4 --extractors mediapipe dwpose --models all --password --open-report
python remote_client.py --resume results/작업번호/job.json --password --open-report
python -m unittest discover -s tests -v
```

SSH 개인키를 사용하면 `--password`를 생략합니다. 암호화된 개인키는 GUI의 개인키 암호란 또는 SSH agent를 사용하세요. GUI가 없는 서버에서는 웹캠 대신 `--video`를 사용합니다.

## 서버 코드

서버 코드는 별도로 [sms-my의 sms-demo/sms-remote](https://github.com/kimwonshin/sms-my/tree/main/sms-demo/sms-remote)에 있습니다. 서버 프로그램 경로 기본값은 `/path/to/workspace/sms-demo/sms-remote/server.py`입니다. 노트북에서 새 HTTP 포트를 열거나 모델을 설치할 필요가 없습니다.

## 20개 구성 확인

서버·클라이언트 검증 17개와 실제 영상의 MediaPipe/DWPose 40개 GPU 예측을 통과했습니다. 키포인트 추출·추론·보고서 ZIP 생성은 22.037초였으며 외부 네트워크 전송 시간은 포함하지 않습니다. 상세 기록은 [validation-catalog20.json](validation-catalog20.json)에 있습니다. 전시장 다인 환경 성능 시험은 포함하지 않습니다.
