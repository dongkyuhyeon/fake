# Experiment Report — Specialist Pipeline v3

## 1. 실험 목적

이 실험은 하나의 범용 모델에 모든 판단을 맡기지 않고 음성·음악·파일 전체를 각각 잘 보는 전문 모델에 역할을 분담하는 구조를 검증한다. 추가 학습이나 파인튜닝 없이 공개된 fine-tuned 모델을 배치할 수 있는지를 확인하는 모델 선별 실험이다.

## 2. 이전 결과와 문제 정의

| 실험 | Total | ADS | CPS |
|---|---:|---:|---:|
| Baseline | 0.69091 | 0.65775 | 0.98932 |
| 두 번째 모델 | 0.69647 | 0.66603 | 0.97034 |

두 번째 모델은 ADS와 Total을 개선했지만 CPS가 하락했다. 세 번째 실험은 다음 문제를 겨냥했다.

- Voice Fake와 Music Fake를 더 전문적으로 판단한다.
- 이미 안정적인 PANNs Presence를 유지해 CPS를 훼손하지 않는다.
- 모든 파일을 HTDemucs로 분리할 때 생길 수 있는 원본 특징 손상과 실행 시간 증가를 줄인다.
- SSL-AASIST의 fairseq 및 중복 XLS-R 가중치를 제거해 제출 구조를 경량화한다.

> 위 표는 이전 실험의 배경 수치다. 세 번째 파이프라인의 DACON 공식 점수는 첨부 자료에 없으며 `NOT_REPORTED`다.

## 3. 최종 파이프라인

```text
입력 오디오
├─ PANNs
│  ├─ 음성 존재 여부
│  └─ 음악 존재 여부
│
├─ DF-Arena 1B
│  └─ 원본 파일 전체가 AI 생성인지 판단
│
├─ SSL-AASIST
│  └─ 음성 성분이 AI 생성인지 판단
│
└─ DF-Arena 1B
   └─ 음악 성분이 AI 생성인지 판단
```

최종 제출 컬럼별 담당은 다음과 같다.

| 제출 컬럼 | 담당 모델 | 기본 입력 |
|---|---|---|
| `FILE_FAKE_PROB` | DF-Arena 1B | 원본 전체 파일 |
| `VOICE_FAKE_PROB` | SSL-AASIST | 원본 또는 조건부 vocals |
| `MUSIC_FAKE_PROB` | DF-Arena 1B | 원본 또는 조건부 accompaniment |
| `VOICE_PRESENT_PROB` | PANNs | 원본 |
| `MUSIC_PRESENT_PROB` | PANNs | 원본 |

## 4. 두 번째 실험 대비 변경점

### 4.1 Voice Fake 전용 모델 도입

Voice Fake에는 SSL-AASIST를 사용한다. 음성 내용보다 합성 과정에서 나타나는 미세한 음향 흔적을 탐지하도록 학습된 모델을 전용 배치한다.

### 4.2 Presence를 PANNs로 복원

두 번째 실험의 MIT AST Presence에서 CPS가 `0.97034`로 하락한 반면 Baseline PANNs Presence의 CPS는 `0.98932`였다. 이미 잘 작동하는 Presence branch를 PANNs로 유지하고, 이번 실험에서는 변경하지 않는다.

### 4.3 HTDemucs 조건부 실행

모든 오디오를 무조건 분리하지 않는다. SSL-AASIST 입력 비교에서 원본 음성의 Voice EER가 더 낮았기 때문이다.

| SSL-AASIST 입력 | Voice EER |
|---|---:|
| 원본 음성 | 12.25% |
| HTDemucs vocals | 12.50% |

조건부 routing 규칙은 다음과 같다.

```text
MUSIC_PRESENT_PROB < 0.5
└─ 원본을 그대로 사용

MUSIC_PRESENT_PROB >= 0.5
├─ HTDemucs로 vocals + accompaniment 분리
├─ VOICE_FAKE_PROB: vocals를 SSL-AASIST에 입력
└─ MUSIC_FAKE_PROB: accompaniment를 DF-Arena 1B에 입력
```

분리된 음성은 작은 왜곡이나 합성 흔적 손실이 발생할 수 있으므로 순수 음성에는 HTDemucs를 적용하지 않는다.

## 5. SSL-AASIST 제출 구조 변환

원래 실행 구조는 다음 요소를 요구했다.

- fine-tuned SSL-AASIST 가중치: 약 1.27GB
- 초기 XLS-R fairseq 가중치: 약 3.8GB
- fairseq 라이브러리

초기 XLS-R 가중치는 모델 구조 생성을 위한 중복 파일에 가까웠다. fine-tuned SSL-AASIST 내부의 XLS-R 가중치를 Transformers 형식으로 변환하여 다음을 제거했다.

- fairseq 의존성
- 중복 XLS-R 3.8GB 파일
- Python 3.11에서 fairseq 설치 실패 위험

변환 전후 400개 score의 상관계수는 `0.9999560`으로 보고됐다. 판단을 사실상 유지하면서 제출 구조를 더 가볍고 안정적으로 만든 변환이다.

## 6. 외부 Voice Fake 검증 데이터

ShiftySpeech의 AISHELL 음성을 사용했다.

| 구분 | 생성 방식 | 파일 수 |
|---|---|---:|
| 실제 음성 | AISHELL | 200 |
| 가짜 음성 | APNet2 | 200 |
| 합계 |  | 400 |

실제 음성과 가짜 음성은 같은 발화 ID로 구성했다. SSL-AASIST의 기존 학습 중심인 HiFiGAN/LJSpeech와 다른 중국어 AISHELL 및 APNet2를 사용해 학습 때 보지 않은 언어·음성·생성기에 대한 일반화를 확인하려는 의도였다.

## 7. Voice Fake 검증 결과

| 방법 | EER | ROC-AUC | 처리 오류 |
|---|---:|---:|---:|
| 원본 SSL-AASIST | 12.25% | 0.94834 | 0/400 |
| HTDemucs vocals 사용 | 12.50% | 0.92950 | 0/400 |
| 추론용 Transformers 변환 | **12.00%** | **0.94904** | 0/400 |

관찰된 내용은 다음과 같다.

- SSL-AASIST는 학습 때 보지 못한 생성기에서도 유효한 분리력을 보였다.
- 음성 단독 파일에 HTDemucs를 적용할 이유는 확인되지 않았다.
- Transformers 변환 이후에도 성능이 유지됐다.
- 400개 파일에서 처리 오류가 발생하지 않았다.

다만 실제 음성과 가짜 음성 score가 모두 높은 구간에 몰리는 경향이 보고됐다. 순위 기반 EER에는 즉시 치명적이지 않지만 더 다양한 생성기와 음향 조건에서 추가 검증이 필요하다.

## 8. 파일 형식 검증

전체 파이프라인에서 다음 형식을 실행했다.

- WAV
- MP3
- FLAC

초기에는 MP3가 ffmpeg 경로 문제로 열리지 않았다. 디코딩을 torchaudio 우선, librosa fallback 방식으로 수정한 뒤 세 형식이 모두 통과했다.

## 9. 실행 성능

측정 장치는 GPU 0의 NVIDIA RTX A5000이다.

| 항목 | 측정값 |
|---|---:|
| 60초 오디오 처리 | 약 1.01초 |
| 전체 모델 로딩 | 약 21.27초 |
| 최대 GPU 메모리 | 약 6.88GB |
| 대회 GPU VRAM | NVIDIA L4 22.4GiB |

메모리는 충분한 것으로 보고됐다. 일반적인 파일 길이라면 시간도 가능성이 높지만, 1,200개가 모두 60초 혼합 오디오라면 HTDemucs 분리 때문에 약 60분에 근접할 수 있다는 위험이 남아 있다.

## 10. 현재 결론과 미확인 항목

현재 자료로 확인할 수 있는 것은 외부 Voice Fake 검증과 실행 가능성이다. 다음 항목은 첨부 자료에 없으므로 계산하거나 추정하지 않는다.

- 세 번째 파이프라인의 DACON Total
- 세 번째 파이프라인의 ADS 및 CPS
- 공식 File EER
- 공식 Voice EER
- 공식 Music EER
- generator-disjoint 전체 대회 성능
- L4에서의 1,200개 실측 총 추론 시간

따라서 상태는 `EXTERNAL_VALIDATION_COMPLETE / OFFICIAL_RESULT_NOT_REPORTED`로 기록한다.

## 11. 원본 자료

보고서 작성에 사용한 원본 캡처는 다음과 같다.

1. [`source_01_overview.png`](../assets/source_01_overview.png): 실험 배경과 최종 구조
2. [`source_02_changes.png`](../assets/source_02_changes.png): 이전 실험 대비 변경점과 조건부 분리
3. [`source_03_validation.png`](../assets/source_03_validation.png): SSL-AASIST 변환과 외부 검증
4. [`source_04_runtime.png`](../assets/source_04_runtime.png): 파일 형식 및 실행 성능
