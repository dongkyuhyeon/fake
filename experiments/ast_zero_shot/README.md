# AST zero-shot result 001

## Pipeline

```text
input audio
├─ MIT AST AudioSet ───────────> voice/music presence
└─ HTDemucs
   ├─ vocals ───────> DF-Arena 1B ─> voice fake
   └─ accompaniment > DF-Arena 1B ─> music fake
```

파일 fake 확률은 presence가 반영된 성분별 fake 위험도의 최댓값이다.

```text
file fake = max(voice presence × voice fake,
                music presence × music fake)
```

AST와 기존 ADS 모델은 모두 고정하며 추가 학습은 하지 않는다. 모든 가중치는 제출 ZIP의 `model/`에서 오프라인으로 로드한다.

## Build inputs

- AST: `/workspace/model_artifacts/ast`
- 기존 ADS 모델: `baseline_submit.zip`의 DF-Arena 1B 및 HTDemucs
- 실행 코드: `script.py`
- 설치 목록: `requirements.txt`
