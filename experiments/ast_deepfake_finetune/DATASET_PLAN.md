# Dataset plan

## 1. 필요한 데이터 종류

| 종류 | 용도 | 주요 라벨 |
|---|---|---|
| 실제 음성 | voice real 기준과 voice presence | voice present=1, voice fake=0 |
| 생성 음성 | TTS/voice cloning 탐지 | voice present=1, voice fake=1 |
| 실제 음악 | music real 기준과 music presence | music present=1, music fake=0 |
| 생성 음악 | text-to-music 탐지 | music present=1, music fake=1 |
| 환경음/무음 | presence 오탐 억제 | voice present=0, music present=0 |
| 합성 혼합물 | 파일 단위 및 성분별 판별 | 각 성분 라벨과 file fake |
| 부분 생성물 | 짧은 생성 구간 탐지 | file fake=1, 해당 성분 fake=1 |

보컬이 있는 음악의 보컬은 음성으로도 취급한다. 원천 음악의 보컬 여부가 확실하지 않으면 자동 라벨을 확정하지 않고 검수 대기 상태로 둔다.

## 2. 공개 원천 후보

### 실제 음성

- Mozilla Common Voice Korean: 한국어 실제 음성, CC0 1.0. 다운로드 release와 날짜를 manifest에 기록한다.
- LibriSpeech: 영어 실제 음성, CC BY 4.0. speaker ID 기준으로 split한다.
- 팀 직접 녹음: 참가자 동의서를 보관하고 화자별로 split한다. 공개 데이터의 부족한 전화·마이크 조건을 보완한다.

### 실제 음악

- MTG-Jamendo: 비영리 연구/학술 용도로 사용하고, 각 트랙의 개별 Creative Commons 라이선스를 `audio_licenses.txt`로 확인한다.
- artist와 track ID를 보존하고 artist-disjoint split을 적용한다.
- 라이선스가 불명확하거나 재배포 조건을 충족하지 못하는 곡은 사용하지 않는다.

### 환경음

- ESC-50: CC BY-NC 조건으로 사용하며 speech/music 성격의 class는 제외한다.
- 전화선 잡음, 실내음 등은 직접 녹음하거나 사용 조건이 명확한 공개 음원만 추가한다.

## 3. 생성 데이터

### 생성 음성

| split 역할 | 생성기 | 생성 방식 |
|---|---|---|
| train | MeloTTS | 한국어·영어 문장, 속도와 seed 변화 |
| train | OpenVoice V2 | 동의·허용된 실제 음성을 source/target로 voice conversion |
| validation/test | Bark | 한국어·영어 문장과 화자 preset 변화 |

- 한국어 60%, 영어 40%를 시작 비율로 사용한다.
- 문장은 CC0/public-domain 텍스트 또는 팀이 직접 작성한 문장만 사용한다.
- 속도, 문장 길이, 화자, seed를 바꾸되 생성기 이름과 정확한 revision/weight hash를 남긴다.
- voice cloning은 당사자의 동의가 있거나 라이선스가 명시적으로 허용하는 음성만 사용한다.

### 생성 음악

| split 역할 | 생성기 | 생성 방식 |
|---|---|---|
| train | MusicGen | 장르·악기·템포 prompt와 seed 변화 |
| train | AudioLDM2 | text-to-music prompt와 seed 변화 |
| validation/test | Stable Audio Open | 학습에 없는 생성 계열의 일반화 측정 |

- electronic, acoustic, classical, hip-hop, ambient, percussion 등 장르와 instrumental/vocal 조건을 균형화한다.
- 10~30초를 생성한 뒤 무음·클리핑 검사를 통과한 구간에서 10초 clip을 만든다.
- prompt, negative prompt, sampler, step, guidance, seed, model revision과 weight hash를 저장한다.
- 모델·가중치 라이선스는 실행 전에 다시 고정하고, 허용 범위를 벗어난 모델은 대체한다.

## 4. 100,000개 예제 구성

### 핵심 8조합: 80,000개

| Voice | Music | File fake | 수량 |
|---|---|---:|---:|
| real | absent | 0 | 10,000 |
| fake | absent | 1 | 10,000 |
| absent | real | 0 | 10,000 |
| absent | fake | 1 | 10,000 |
| real | real | 0 | 10,000 |
| fake | real | 1 | 10,000 |
| real | fake | 1 | 10,000 |
| fake | fake | 1 | 10,000 |

추가 20,000개는 다음과 같다.

- 부분 생성물 10,000개: 실제 10초 성분에 0.5~3초 생성 구간을 무작위 위치에 삽입
- hard negative 10,000개: 환경음, 저음량, 순간 충격음, 전화선 잡음 등 음성·음악 부재 예제

수량은 생성 성공률과 검수 후 확정한다. 균형을 맞추기 위해 동일 원본을 반복 복제하지 않는다.

## 5. 생성 절차

1. 원천 등록: URL, 라이선스, 다운로드 날짜, 원본 SHA-256과 화자/artist/track ID를 저장한다.
2. 누수 방지 split: clip을 만들기 전에 화자, artist, 원본 파일과 생성기 계열을 train/validation/test로 나눈다.
3. 성분 생성: 음성과 음악을 각각 실제/생성 component library로 만든다.
4. 품질 검사: 길이, sample rate, NaN, 완전 무음, peak clipping, 중복 hash를 검사한다.
5. 혼합: voice/music 상대 gain을 `-12~+12 dB`, onset과 활성 길이를 무작위화해 10초 파일을 만든다.
6. 부분 생성: 0.5~3초 생성 성분을 실제 성분 중간에 삽입하고 위치를 기록한다.
7. 채널 변형: 원본 라벨을 유지한 채 WAV/MP3/AAC/Opus, 8 kHz 전화 채널 후 16 kHz 복원, 잡음, 잔향, resampling 조건을 만든다.
8. manifest 고정: 모든 랜덤 seed와 변형 파라미터를 기록하고 SHA-256으로 결과를 검증한다.
9. 사람 검수: split별·class별 표본과 보컬 음악의 presence 라벨을 확인한다.

clean 예제를 반드시 남기고 변형 예제가 전체를 덮지 않게 한다. 채널 효과만 보고 fake를 맞히는 지름길을 막기 위해 실제와 생성 양쪽에 동일한 변형 분포를 적용한다.

## 6. 라벨 규칙

- `file_fake = max(voice_present * voice_fake, music_present * music_fake)`
- 음성이 없으면 `voice_fake` 값은 0으로 저장하되 `voice_fake_mask=0`으로 loss에서 제외한다.
- 음악이 없으면 `music_fake` 값은 0으로 저장하되 `music_fake_mask=0`으로 loss에서 제외한다.
- presence와 fake를 혼동하지 않도록 mask를 반드시 별도 컬럼으로 둔다.

manifest 필드는 `schemas/manifest.schema.json`에 정의한다.

## 7. 라이선스·재현성 게이트

다운로드 전에 다음을 모두 통과해야 한다.

- 누구나 접근 가능하고 최소 비영리 연구 사용이 허용되는가?
- 원본 또는 파생 데이터를 2차 검증에 제출할 수 있는가?
- attribution, share-alike, 비상업 조건을 충족할 수 있는가?
- 정확한 release/revision과 체크섬을 고정할 수 있는가?
- 생성 음성이 실제 인물을 사칭하거나 동의 없는 음성을 복제하지 않는가?

특히 Common Voice는 CC0이지만 Mozilla의 배포 요청 조건을, MTG-Jamendo는 개별 트랙 라이선스와 비상업 조건을 별도로 확인한다. 2차 제출 가능 여부가 애매하면 운영진에 서면 문의해 답변을 보관하거나 해당 원천을 제외한다.

## 8. Git과 서버 저장 위치

```text
Git repository
└── experiments/ast_deepfake_finetune/
    ├── README.md
    ├── DATASET_PLAN.md
    ├── DATA_SOURCES.md
    ├── configs/dataset_v1.yaml
    └── schemas/manifest.schema.json

Server data area (not Git)
└── data_v2/
    ├── raw/
    ├── generated/
    ├── mixtures/
    ├── manifests/
    ├── licenses/
    └── checksums/
```

오디오 파일은 제출 ZIP 전용 폴더에도 넣지 않는다. 학습 완료 후 제출 ZIP에는 추론 코드와 최종 가중치만 포함한다.

