# Audio Deepfake Detection Lab

음성과 음악이 섞인 오디오의 AI 생성 여부를 탐지하기 위한 실험 기록입니다.

## Current design

```text
Input audio (16 kHz mono)
        │
        ├─ MIT AST AudioSet
        │    ├─ speech presence
        │    ├─ music presence
        │    └─ pooled audio embedding
        │
        └─ existing ADS logic
             └─ file fake probability
```

첫 실험에서는 추가 학습 없이 AST가 음성·음악 존재 확률과 범용 오디오 특징을 추출하고, 기존 판정 로직이 파일의 생성 확률을 계산한다. 이후에는 같은 AST 특징 위에 진짜/가짜 분류기를 학습해 ADS를 개선한다.

## Model

- `MIT/ast-finetuned-audioset-10-10-0.4593`
- AudioSet 527개 클래스 기반 오디오 분류 모델
- BSD-3-Clause
- 가중치는 로컬에 내려받고 Git에는 코드와 설정만 보관

모델 준비 방법과 고정된 revision은 [`models/ast`](models/ast)에 기록한다.

## Experiment reports

전체 실험 목록과 현재 상태는 [`experiments/README.md`](experiments/README.md)에서 확인할 수 있다.

- [`AST zero-shot`](experiments/ast_zero_shot)
- [`AST deepfake-domain fine-tuning plan`](experiments/ast_deepfake_finetune)
- [`Tiger A — AI-Music AST`](experiments/tiger_a_ai_music_ast)
- [`Specialist Pipeline v3`](experiments/specialist_pipeline_v3)

## Experiment stages

1. AST 가중치와 오프라인 로딩 검증
2. 음성·음악 존재 확률 산출
3. 기존 ADS 로직과 결합한 최초 결과 생성
4. 직접 구성한 학습 데이터로 ADS 분류기 개선
5. 구간 집계와 임계값 조정
