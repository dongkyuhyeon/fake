# Experiment 002: AST deepfake-domain fine-tuning

## 목표

첫 실험의 AST 기반 구조를 유지하되, 일반 오디오 분류용 표현을 실제/생성 음성·음악 판별에 직접 맞춘다. 작은 임계값 조정이 아니라 최종 점수 비중 90%인 ADS를 구조적으로 높이는 실험이다.

## 근거

| Metric | Baseline | Experiment 001 | Change |
|---|---:|---:|---:|
| Total | 0.69091 | 0.69647 | +0.00556 |
| ADS | 0.65775 | 0.66603 | +0.00828 |
| CPS | 0.98932 | 0.97034 | -0.01898 |

AST 표현을 사용했을 때 ADS와 총점이 상승했다. 그러나 첫 실험의 AST는 AudioSet 일반 사건 분류 가중치를 그대로 사용했으며 실제/생성 판별을 학습하지 않았다. 따라서 두 번째 실험은 AST를 deepfake 도메인에 파인튜닝해 이 상승 가능성을 직접 확대한다.

## 학습 구조

```text
10-second waveform
       │
       ▼
shared AST encoder
  ├─ file fake head
  ├─ voice fake head
  ├─ music fake head
  ├─ voice presence head
  └─ music presence head
```

- 음성이 없는 샘플은 voice-fake loss에서 제외한다.
- 음악이 없는 샘플은 music-fake loss에서 제외한다.
- file-fake는 하나 이상의 존재하는 성분이 생성이면 1이다.
- 긴 파일은 10초 창으로 추론하고, 짧은 생성 구간을 놓치지 않도록 file/성분 fake는 상위 구간 위험도를 집계한다.
- 제출용 presence는 Experiment 001에서 하락한 CPS를 복구하기 위해 기존 강한 presence 출력과 새 head를 검증셋에서 비교한 뒤 결정한다.

## 데이터

목표 규모는 10초 학습 예제 100,000개다.

- 핵심 8조합: 80,000개(조합별 10,000개)
- 짧은 생성 구간 삽입: 10,000개
- 음성·음악이 없는 환경음 hard negative: 10,000개

핵심 8조합은 voice absent/real/fake와 music absent/real/fake 중 둘 다 absent인 경우를 제외하고, 실제 평가 라벨에 필요한 조합을 균형 있게 구성한다. 자세한 원천, 생성법, 라벨, 분할은 `DATASET_PLAN.md`에 기록한다.

## 검증 원칙

1. 화자·곡·원본 파일을 split 전에 고정해 파생 clip이 서로 다른 split에 들어가지 않게 한다.
2. 생성 모델 계열을 분리한다. 학습은 MeloTTS/OpenVoice와 MusicGen/AudioLDM2, 검증은 Bark와 Stable Audio Open으로 구성한다.
3. 검증 생성기는 학습 중 보지 않으므로 특정 생성기의 흔적을 외우는 모델을 배제한다.
4. clean, codec, telephone 세 조건을 따로 보고한다.
5. 공식 평가 파일이나 그 통계는 학습·튜닝에 사용하지 않는다.

## 진행 기준

이 실험은 아래 내부 검증 조건을 모두 만족할 때만 제출 패키지로 진행한다.

- generator-disjoint validation ADS가 Experiment 001 대비 최소 `+0.03`
- 전화 채널과 codec 조건 모두에서 ADS 개선
- CPS가 `0.96` 미만으로 하락하지 않음
- 최종 ZIP 10GB 이하, 압축 해제 32GB 이하, L4 추론 60분 이하

조건을 통과하지 못하면 공개 리더보드의 작은 변화를 확인하기 위한 제출은 만들지 않는다.

## 저장 정책

Git에는 문서, manifest, 설정, 생성·학습 코드와 체크섬만 저장한다. 대용량 원본 및 생성 오디오는 Git에 올리지 않고 별도 서버 데이터 디렉터리에 보관한다. 2차 검증에 대비해 원천 데이터와 생성 데이터 전체를 재현 가능한 상태로 보존한다.

