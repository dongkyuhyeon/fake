# Competition Rules & Submission Checklist

> 마지막 확인: 2026-08-31  
> 이 문서는 작업용 요약이며, 충돌 시 공식 페이지와 운영진 공지가 우선합니다.

## 1. 문제와 예측 항목

각 오디오 파일에 대해 다음 5개 확률을 `0~1` 범위로 예측합니다.

- `FILE_FAKE_PROB`: 파일 전체가 AI 생성 또는 변조일 확률
- `VOICE_FAKE_PROB`: 음성 성분이 AI 생성일 확률
- `MUSIC_FAKE_PROB`: 음악 성분이 AI 생성일 확률
- `VOICE_PRESENT_PROB`: 음성 성분이 존재할 확률
- `MUSIC_PRESENT_PROB`: 음악 성분이 존재할 확률

보컬은 음성 성분으로 분류합니다. 음성과 음악 중 하나라도 FAKE라면 파일 전체는 FAKE입니다. 단순 잡음 제거, 음량 조정 등 성분을 새로 생성하지 않는 후처리는 REAL로 간주합니다.

## 2. 데이터 규칙

- 별도의 학습 데이터는 제공되지 않습니다.
- 참가자가 필요한 학습 데이터를 직접 수집하거나 생성해야 합니다.
- 공개 파일의 `data/test/`에는 형식 확인용 더미 오디오 3개만 있습니다.
- 실제 평가 데이터는 1,200개이며 외부에 공개되지 않습니다.
- 평가 파일은 4초 이상 1분 이하, 16 kHz이며 WAV, MP3, FLAC 등 여러 형식으로 구성됩니다.
- 일부 평가 샘플에는 전화 채널 오디오가 포함됩니다.
- 비공개 평가 데이터를 이용한 학습, 튜닝, pseudo-labeling 및 모델 갱신은 금지됩니다.

## 3. 외부 데이터·모델·API

다음 조건을 모두 만족하면 사전학습 모델, API, 외부 데이터 수집 및 생성 등의 방법을 사용할 수 있습니다.

- 누구나 접근 가능한 공개 자원일 것
- 최소 비영리 목적의 사용이 허용될 것
- 해당 라이선스와 이용조건을 참가자가 직접 확인하고 준수할 것
- 사용한 모든 모델, 데이터, 코드, API 및 생성 도구의 출처를 기록할 것

라이선스가 불분명하거나 비영리 사용도 금지된 자원은 사용하지 않습니다.

## 4. 평가 파일 독립성

- 평가 파일은 각각 독립적으로 예측해야 합니다.
- 한 파일을 여러 segment로 나누어 추론하고 파일 내부 결과를 결합하는 것은 허용됩니다.
- 다른 평가 파일의 데이터, 통계 또는 예측값을 이용해 특정 파일의 결과를 보정하는 것은 금지됩니다.
- 테스트 전체 분포를 이용한 정규화, 순위 보정, 비율 강제 등의 후처리를 적용하지 않습니다.
- 평가 데이터 유출 시도는 즉시 실격 사유입니다.

## 5. 평가 지표

```text
Score = 0.9 × ADS + 0.1 × CPS

ADS = 0.5 × (1 - File EER)
    + 0.2 × (1 - Voice EER)
    + 0.3 × (1 - Music EER)

CPS = 0.5 × Voice Presence ROC-AUC
    + 0.5 × Music Presence ROC-AUC
```

최종 점수 기준 실질 비중은 다음과 같습니다.

| 항목 | 최종 점수 비중 |
|---|---:|
| File EER | 45% |
| Voice EER | 18% |
| Music EER | 27% |
| Voice Presence ROC-AUC | 5% |
| Music Presence ROC-AUC | 5% |

- FAKE가 양성 클래스 `1`입니다.
- Voice EER은 음성이 존재하는 샘플에서만 계산합니다.
- Music EER은 음악이 존재하는 샘플에서만 계산합니다.
- Public Score는 전체 테스트 데이터 100%로 계산되며 대회 종료 시 Private Score가 됩니다.

## 6. 제출 ZIP 구조

ZIP 최상위 구조를 정확히 맞춰야 합니다. 추가 최상위 폴더를 만들지 않습니다.

```text
submit.zip
├── model/
├── script.py
└── requirements.txt
```

평가 서버가 실행 시 `data/`와 `output/`을 추가합니다. 코드는 `data/test/`의 입력을 읽고 `output/submission.csv`를 생성해야 합니다.

### 제출 제한

- ZIP 크기: 10GB 이하
- 압축 해제 후 크기: 32GB 이하
- 패키지 설치: 10분 이내
- 추론 실행: 60분 이내
- 인터넷: 패키지 설치 외 사용 불가
- 언어: Python
- CSV 인코딩: UTF-8
- 제출 횟수: 하루 최대 3회

### 평가 서버

- Ubuntu 22.04.5 LTS
- Python 3.11.15
- NVIDIA L4, VRAM 22.4GiB
- CPU 6 vCPU
- RAM 28GB
- CUDA 12.8

필요한 모델 가중치는 모두 ZIP의 `model/`에 포함해야 합니다. 추론 중 외부 모델 다운로드에 의존하지 않습니다.

## 7. 1차·2차 평가

- 1차: Private Score 기준 상위 15팀이 2차 평가 대상입니다.
- 2차: 검증을 통과한 상위 15팀을 대상으로 서면 종합 평가를 진행합니다.
- 최종 상위 7팀을 수상팀으로 선정합니다.

2차 평가 대상자는 다음 자료를 제출해야 합니다.

- Private Score를 재현할 수 있는 학습 코드
- 모델 개발 보고서(HWP)
- 학습데이터 구성 보고서(HWP)
- 학습에 사용한 데이터 파일 전체
- 팀원 성명, 생년월일, 성별 및 현재 소속

따라서 실험 시작 시점부터 데이터 출처, 라이선스, 다운로드 날짜, 생성 방법, 전처리, 학습 설정, seed와 체크포인트를 기록합니다.

## 8. 팀 및 일정

- 개인 또는 최대 5명 팀으로 참가할 수 있습니다.
- 동일인이 개인 및 복수 팀에 중복 등록할 수 없습니다.
- 팀 병합 마감: 2026-09-23
- 리더보드 제출 마감: 2026-09-29
- 대회 종료: 2026-09-30
- 2차 자료 제출 마감: 2026-10-05
- 최종 결과 발표: 2026-10-16

## 9. 제출 전 체크리스트

- [ ] ZIP 최상위에 `model/`, `script.py`, `requirements.txt`만 필요한 형태로 배치했는가?
- [ ] 모든 가중치를 오프라인으로 로드하는가?
- [ ] WAV, MP3, FLAC 입력을 모두 처리하는가?
- [ ] `output/submission.csv`를 UTF-8로 생성하는가?
- [ ] ID와 5개 예측 컬럼의 순서 및 행 수가 정확한가?
- [ ] 모든 확률이 유한한 `0~1` 값인가?
- [ ] 평가 파일 간 정보를 공유하지 않는가?
- [ ] ZIP 및 압축 해제 용량 제한을 만족하는가?
- [ ] 설치 10분, 추론 60분 제한을 만족하는가?
- [ ] 외부 데이터와 모델의 출처·라이선스를 기록했는가?
- [ ] 동일 환경에서 학습과 추론을 재현할 수 있는가?

## Official References

- [Description](https://dacon.io/competitions/official/236749/overview/description)
- [Evaluation](https://dacon.io/competitions/official/236749/overview/evaluation)
- [Rules](https://dacon.io/competitions/official/236749/overview/rules)
- [Data](https://dacon.io/competitions/official/236749/data)
- [Code submission guide](https://cfiles.dacon.co.kr/competitions/236564/guide.html)
