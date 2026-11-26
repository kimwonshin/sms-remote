# SMS 원격 수어 분석 — 노트북 프로그램

## 원격 테스트 모델 32개

이전 **20개를 유지하고 새 결합 학습 12개를 추가**, 총32개를 비교합니다. 기본 선택은 **M4 결합10% · 실제 응급 단어20% · 통합98라벨 BiLSTM seed42**입니다. 새 최상위 조건은 seed3개로 확인했습니다.

GUI에서 `추천 결합 BiLSTM`, `새 결합 12개`, `이전 통합10개`, `기존 문장10개`, `이전20개`, `전체 모델` 또는 서버 목록의 개별 ID를 선택합니다. 모든 활성 모델은 네 추출기의 직접15fps 입력을 받습니다. hybrid/RTMW는 미보정 비교용입니다.

```bash
python remote_client.py --list-models --password
python remote_client.py --video sentence.mp4 --extractors mediapipe dwpose --models domain12 --password --open-report
python remote_client.py --video sentence.mp4 --extractors mediapipe --models native20 --password --open-report
python remote_client.py --video sentence.mp4 --extractors mediapipe dwpose --models all --password --open-report
python remote_client.py --video sentence.mp4 --extractors mediapipe --models release --password --open-report
```

`old10`과 `new10`은 이전 각10개, `native20`은 이전20개, `domain12`는 새12개, `native32`/`all`은32개, `release`는 추천 새 결합 모델1개입니다. 이전 `native75`/`legacy`와 제외된 ID는 계속 실행하지 않습니다. 모델 가중치와 원래 결과는 서버에 보존합니다.

새12개는 **U98 10개·U97 1개·U74 1개**로, blank 포함 출력은 각각99·98·75입니다. U74의 저장 설정 이름은 Utop25입니다. 새 U98의 신체 다리는 검증된 원본이 없어 미학습 예비 클래스이며 목록·JSON에 표시합니다. 기존 S50의 단어 보조 헤드는 응급 Gloss 출력에 쓰지 않고, E50 대조군은 문장 번역용이 아닙니다.

목록·선정 근거는 [MODEL_CATALOG.md](MODEL_CATALOG.md), 고정 ID는 [model_selection.json](model_selection.json), Test 결과는 [benchmark.csv](benchmark.csv)에 있습니다. 이전 응급 E50(335편)과 새 의미 정정 E49(315편)는 평가 분모가 달라 점수를 직접 합치지 않습니다. 새 U74는 전체/지원 범위 성능과 커버리지를 분리합니다.

클라이언트와 sms-my 서버를 함께 업데이트하세요. 기존 client-config.json·SSH 키·촬영본·반환 결과는 유지하며, 노트북에 가중치를 받지 않습니다. 실제 모델 목록은 서버 `--list-models` 응답이 기준입니다.

반환 보고서는 순서 있는 Gloss, confidence, 질문 여부, 입력 프레임 수, 어휘 범위와 미학습 라벨을 제공합니다. 정답 없는 촬영 영상의 정확도를 만들지 않습니다. REAL06 confidence 보정이 전시장 카메라 환경에서도 검증된 확률을 뜻하지는 않습니다.


## 네 추출기 비교

GUI에서 **MediaPipe / DWPose-L / hybrid / RTMW-x 384**를 선택할 수 있습니다. CLI ID는 `mediapipe dwpose hybrid rtmw`입니다. RTMW는 로컬에 고정된 **RTMW-x 384×288** 가중치이고, hybrid는 **RTMW-x + 손 확대 재추정 + MediaPipe 누락 보완**입니다.

```bash
python remote_client.py --video sentence.mp4 --extractors mediapipe dwpose hybrid rtmw --models release --password --open-report
python remote_client.py --video sentence.mp4 --extractors hybrid rtmw --models domain12 --password --open-report
python remote_client.py --video sentence.mp4 --extractors mediapipe dwpose hybrid rtmw --models all --password --open-report
```

32개 모델 모두 동일 원본에서 직접15fps로 추출한 canonical74 → 465특징을 받습니다. 같은 추출기의 특징은 선택한 모델들에 공유합니다. 추출 영상·좌표·특징은 `mediapipe-15fps/`, `dwpose-15fps/`, `hybrid-15fps/`, `rtmw-15fps/`로 분리합니다. RTMW/DWPose의 ONNX와 인식 모델은 CUDA, hybrid의 RTMW/손 ONNX는 CUDA 및 MediaPipe 보완은 CPU에서 실행합니다.

**hybrid·RTMW는 새 입력 출처의 비교 실험**입니다. 현재32개 모델의 학습·REAL06 보정은 MediaPipe/DWPose 기준입니다. 두 새 출처에서 Gloss 배열과 raw_score를 출력하지만 confidence·토큰 confidence·질문 확률·is_question은 null, 상태는 `needs_review`/`uncalibrated_extractor`로 표시합니다. 입력 품질이 나쁘면 기존 `invalid_input`을 보존합니다. 다른 추출기의 보정 계수를 이름만 바꿔 재사용하지 않으며, 모델별 신규 profile에 보정 계수나 임계값을 넣지 않습니다.

기존 checkpoint와 MediaPipe/DWPose profile은 그대로 보존합니다. 기존 benchmark.csv 점수는 MediaPipe/DWPose만의 Test 결과이며, 새 두 출처의 정확도를 나타내지 않습니다. 새 추출기용 독립 보정·정확도 평가를 하기 전까지 전시장 성능 향상을 가정하지 않습니다.

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

기본 분석은 MediaPipe 직접15fps + 새 M4 결합10% 통합98라벨 BiLSTM입니다. 활성32개는 MediaPipe·DWPose·hybrid·RTMW-x384로 비교합니다. 네 출처는 직접15fps 입력이며 hybrid/RTMW는 별도 미보정 상태로 표시합니다. **MediaPipe 키포인트 추출은 서버 CPU**, 나머지 ONNX 추출과 모든 문장 모델 추론은 서버 GPU를 사용합니다.

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

## 이전 20개 구성 확인 (2026-11-20)

서버·클라이언트 검증 17개와 실제 영상의 MediaPipe/DWPose 40개 GPU 예측을 통과했습니다. 키포인트 추출·추론·보고서 ZIP 생성은 22.037초였으며 외부 네트워크 전송 시간은 포함하지 않습니다. 상세 기록은 [validation-catalog20.json](validation-catalog20.json)에 있습니다. 전시장 다인 환경 성능 시험은 포함하지 않습니다.

## 32개 구성 확인 — 2026-11-21

서버10개·클라이언트7개 테스트와 실제 영상의 두 추출기×32개 모델, 총64개 CUDA 예측·보고서 ZIP 생성 검증을 통과했습니다. 서버 처리23.055초이며 네트워크 전송과 촬영은 제외합니다. 이전20개 checkpoint/profile 해시는 그대로 보존됐고, CTC75/98/99출력 및 미학습 다리 표시를 확인했습니다. 상세 기록은 [validation-catalog32.json](validation-catalog32.json)입니다.

## 네 추출기 실행 확인 — 2026-11-21

실제 REAL17 영상 한 편을 네 출처에서 직접15fps 55프레임으로 추출하고, 32개 모델의 총128개 CUDA 예측과 보고서 ZIP 검증을 통과했습니다. 모든 출처의 표본 시각·원본 프레임 번호가 같고 canonical74/465특징을 확인했습니다. RTMW ONNX 입력은 [batch,3,384,288]입니다. 기존64개 MP/DW profile 해시는 보존했고 새64개 profile은 미보정으로 생성했습니다. 서버 처리57.115초이며 네트워크 전송·촬영 시간은 제외합니다. [validation-extractors4.json](validation-extractors4.json)에 기록했습니다. 단위 검증은 서버13개·클라이언트7개를 통과했습니다.

## 차렷·새 순서 학습 후보

`standing`은 차렷 복원과 새 결합 순서를 사용한 완료 모델 전체, `standing-candidate`는 검증 기준의 잠정 후보입니다. 기존 `native32`와 `release`는 기존 모델을 유지합니다. `all`은 등록된 전체를 포함합니다. 이 모델들은 같은 U98(98글로스+blank) CTC로 문장과 응급 단어를 출력합니다. C2의 공유 보조 CTC는 학습에만 사용하며 별도 출력 헤드가 없습니다.

합성 diagnostic-dev/test는 Train 원본 조각을 재사용한 순서 검사입니다. 새 실제 카메라 검증이 없으므로 전시장 성능 개선으로 해석하지 마세요. 학습·Test·seed·보존 가드 및 한계는 [standing_and_data_benchmarking.md](standing_and_data_benchmarking.md), 완료 목록은 `standing_model_selection.json`, 결과는 `standing_benchmark.csv`를 참고하세요. 가중치는 서버의 완료 학습 디렉터리에 보존하며 Git에 넣지 않습니다.

```bash
python remote_client.py --video sentence.mp4 --extractors mediapipe dwpose --models standing --password --open-report
```


## RTMW 포함 학습 후보

[RTMW_TRAINING.md](RTMW_TRAINING.md)에 새 E49 단일 CTC 후보의 조건·진행 상태·보정 정책을 기록합니다. 완료 후 `rtmw-candidates`/`rtmw-candidate` 프리셋으로 비교하며 기존 `release`를 유지합니다.
