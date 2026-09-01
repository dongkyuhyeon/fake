# AST zero-shot result 001

## 실험 목적

기존 탐지기의 fake 판정 부분은 유지하고, 음성·음악 존재 여부를 판정하는 모델만 MIT AST AudioSet으로 교체했을 때의 첫 결과를 확인한다.

이 실험은 추가 데이터 수집이나 재학습 없이 공개된 사전학습 가중치를 그대로 사용하는 zero-shot 실험이다.

## 실험 가설

- AudioSet 527개 클래스로 학습된 AST는 음성과 음악이 함께 포함된 일반 오디오를 처리할 수 있다.
- 기존 ADS 판정기를 그대로 유지하면 모델 교체에 따른 presence 결과의 영향을 분리해서 관찰할 수 있다.
- 하나의 파일 내부 구간만 독립적으로 처리하고 최댓값을 사용하면 짧게 등장하는 음성이나 음악도 놓치지 않을 수 있다.

## 추론 구조

```text
input audio (16 kHz mono)
├─ MIT AST AudioSet
│  ├─ voice presence
│  └─ music presence
└─ HTDemucs
   ├─ vocals ─────────> DF-Arena 1B ─> voice fake
   └─ accompaniment ─> DF-Arena 1B ─> music fake
```

파일 fake 확률은 presence가 반영된 성분별 위험도의 최댓값이다.

```text
voice risk = voice presence × voice fake
music risk = music presence × music fake
file fake  = max(voice risk, music risk)
```

## 모델 역할

| 모델 | 역할 | 학습 여부 |
|---|---|---|
| MIT AST AudioSet | 음성·음악 존재 확률 | 가중치 고정 |
| HTDemucs | vocals/accompaniment 분리 | 가중치 고정 |
| DF-Arena 1B | 분리된 성분의 fake 확률 | 가중치 고정 |

AST에서는 AudioSet 라벨 중 음성 계열 18개와 음악 계열 117개를 사용한다. 각 파일을 최대 10초 구간으로 나누고, 구간과 관련 라벨 전체에서 가장 큰 sigmoid 확률을 presence 값으로 사용한다.

## 출력

각 입력 파일마다 다음 다섯 값을 생성한다.

- `FILE_FAKE_PROB`
- `VOICE_FAKE_PROB`
- `MUSIC_FAKE_PROB`
- `VOICE_PRESENT_PROB`
- `MUSIC_PRESENT_PROB`

모든 값은 유한한 `0~1` 확률인지 저장 직전에 다시 검사한다.

## 오프라인 실행 패키지

생성 파일은 `submit_ast_v1.zip`이며 구조는 다음과 같다.

```text
submit_ast_v1.zip
├── model/
│   ├── ast/
│   ├── df_arena_1b/
│   ├── htdemucs/
│   ├── MODEL_INFO.txt
│   └── SHA256SUMS.txt
├── script.py
└── requirements.txt
```

실행 중 모델을 내려받지 않으며 모든 가중치를 `model/`에서 불러온다. 실행 환경에 기본 설치된 패키지만 사용하도록 `requirements.txt`에는 추가 패키지를 지정하지 않는다.

## 파일 안내

- `script.py`: 전체 오프라인 추론 코드
- `MODEL_INFO.txt`: 모델 출처, revision, 라이선스
- `SHA256SUMS.txt`: 패키징 대상 가중치 검증값
- `requirements.txt`: 실행 환경 패키지 정책
- `RESULTS.md`: GPU 실행과 ZIP 검증 결과

## 현재 범위

- 공개 형식 확인용 오디오 3개에서 전체 GPU 추론을 완료했다.
- 실제 평가 결과는 총점 `0.69647`, ADS `0.66603`, CPS `0.97034`다.
- 기존 기준점보다 ADS와 총점은 상승했고 CPS는 하락했다.
- 다음 실험에서는 AST presence를 파일 fake 계산에 유지하면서 제출용 presence를 기존 모델과 분리하는 구조를 비교한다.
