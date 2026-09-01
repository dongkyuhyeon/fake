# Result 001

## Configuration

- Presence model: MIT AST AudioSet
- ADS model: DF-Arena 1B
- Source separation: HTDemucs
- AST and ADS weights: frozen
- Additional training data: none
- Test device: NVIDIA RTX A5000

## Validation

- AST offline load: passed
- AST labels: 527
- Voice/music label mapping: passed
- End-to-end GPU inference on 3 format-check samples: passed
- Output schema and ID order: passed
- All five probabilities finite and within `0~1`: passed
- Model SHA-256 checks: passed
- ZIP integrity test: passed

## Submission artifact

- File: `submit_ast_v1.zip`
- Compressed size: `4,580,604,158 bytes`
- Uncompressed size: `5,022,413,777 bytes`
- SHA-256: `480486260fcff15ea731336d579d5e0fa56e8a964f540b51a4aefe7025877602`

## Evaluation result

| Metric | Previous baseline | Result 001 | Change |
|---|---:|---:|---:|
| Total | 0.69091 | 0.69647 | +0.00556 |
| ADS | 0.65775 | 0.66603 | +0.00828 |
| CPS | 0.98932 | 0.97034 | -0.01898 |

ADS 상승분이 CPS 하락분보다 크게 반영되어 총점이 개선됐다. 다음 실험에서는 AST presence를 `FILE_FAKE_PROB` 계산 내부에 유지하고, 제출용 voice/music presence에는 기존 presence 모델을 사용하는 역할 분리를 검증한다.
