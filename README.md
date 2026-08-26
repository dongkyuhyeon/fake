# Audio Deepfake Detection Lab

음성과 음악이 섞인 오디오에서 AI 생성 여부를 탐지하기 위한 개인 실험 기록입니다.

## Experiment 001 — Zero-shot baseline

추가 학습 없이 공개 사전학습 모델을 조합했을 때 어느 정도까지 탐지할 수 있는지 확인하는 실험입니다.

### Pipeline

```text
Input audio
├─ PANNs Cnn14
│  ├─ Voice presence
│  └─ Music presence
└─ HTDemucs
   ├─ Vocals ─────────> DF-Arena 1B ─> Voice fake probability
   └─ Accompaniment ──> DF-Arena 1B ─> Music fake probability
```

파일 전체의 생성 확률은 음성과 음악 성분별 위험도 중 큰 값을 사용합니다.

```text
voice risk = voice presence × voice fake probability
music risk = music presence × music fake probability
file risk  = max(voice risk, music risk)
```

### Why this setup?

- PANNs로 음성과 음악의 존재 여부를 먼저 구분합니다.
- HTDemucs로 혼합 오디오를 성분별로 분리합니다.
- DF-Arena 1B로 각 성분의 합성 가능성을 독립적으로 추론합니다.
- 모든 모델을 로컬에서 불러와 오프라인 추론이 가능하도록 구성했습니다.

### Repository structure

```text
baseline/
├─ baseline_notebook.ipynb
├─ script.py
├─ requirements.txt
└─ model/
   ├─ df_arena_1b/
   ├─ htdemucs/
   └─ panns/
```

대용량 모델 가중치는 Git에서 관리하지 않습니다. 필요한 가중치 경로와 예상 해시는 `baseline/model/SHA256SUMS.txt`에 기록합니다.

### Current notes

- 입력 오디오는 16 kHz mono로 정규화합니다.
- 짧은 구간 단위로 추론한 뒤 파일 단위 결과로 집계합니다.
- 음성·음악 분리 품질이 성분별 fake 확률에 직접 영향을 줄 수 있습니다.
- zero-shot 결과이므로 도메인이 달라질 때 점수 분포가 불안정할 가능성이 있습니다.

## Next experiments

- [ ] 성분별 threshold와 pooling 방식 비교
- [ ] 긴 오디오의 segment sampling 전략 비교
- [ ] 압축, 전화 채널, 잡음 환경에 대한 강건성 확인
- [ ] 범용 오디오 encoder를 이용한 multi-task fine-tuning
- [ ] 추론 시간과 GPU 메모리 사용량 측정
