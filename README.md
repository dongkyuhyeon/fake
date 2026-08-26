# DACON Deepvoice Detection

Workspace for the [딥보이스 범죄 대응을 위한 AI 탐지 모델 경진대회](https://dacon.io/competitions/official/236749/overview/description).

## Baseline

The `baseline/` directory contains the unmodified code from DACON's official code-share post:

- [PANNs·HTDemucs·DF_Arena_1B 기반 AI 탐지](https://dacon.io/competitions/official/236749/codeshare/14153)
- `baseline_notebook.ipynb`: original code-share notebook
- `script.py`: inference entrypoint
- `requirements.txt`: additional Python dependency
- `model/`: model source and configuration files

The baseline is a zero-shot inference pipeline:

1. PANNs estimates voice and music presence.
2. HTDemucs separates vocals and accompaniment.
3. DF-Arena 1B estimates fake probabilities for both components.
4. The component risks are fused into the file-level fake probability.

## Model weights and submission ZIP

Large binary files are intentionally not tracked by Git:

- `baseline/model/df_arena_1b/pytorch_model.bin`
- `baseline/model/htdemucs/955717e8-8726e21a.th`
- `baseline/model/panns/Cnn14_mAP=0.431.pth`
- `submit.zip`

Download the official [`open.zip`](https://cfiles.dacon.co.kr/competitions/236749/open.zip) and extract `baseline_submit.zip` to obtain the exact weights and submission package. The expected weight hashes are recorded in `baseline/model/SHA256SUMS.txt`.
