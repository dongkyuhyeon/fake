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
- Compressed size: `4,580,604,555 bytes`
- Uncompressed size: `5,022,413,769 bytes`
- SHA-256: `300bf9b31906a470608df801004ed01c8c4a91857eb13691f9e04c053dc4fad4`

리더보드 점수는 실제 제출 후 기록한다.
