# BEATs_iter3+ (AS2M)

오디오 표현 추출 실험용으로 Microsoft의 사전학습 모델 `BEATs_iter3+ (AS2M)`를 고정했다. 이 디렉터리에는 재현을 위해 공식 구현, 출처 정보, 체크포인트 다운로드 및 검증 도구를 보관한다.

## 선택한 모델

- 모델: `BEATs_iter3+ (AS2M)` pre-trained checkpoint
- 용도: 입력 음성의 범용 오디오 임베딩 추출
- 공식 저장소: https://github.com/microsoft/unilm/tree/master/beats
- 고정한 upstream commit: `ca43e4cd19445a536f133bf2bc25b573b2f0c7c5`
- 라이선스: MIT (`LICENSE` 참고)

`upstream/`의 파일은 위 커밋에서 그대로 가져왔다. 모델 가중치는 GitHub 일반 파일 크기 제한을 초과하므로 저장소에 커밋하지 않는다.

## 체크포인트 준비

```bash
bash models/beats/download_checkpoint.sh
python models/beats/verify_checkpoint.py
```

기본 저장 위치는 저장소 밖의 `/workspace/model_artifacts/beats/BEATs_iter3_plus_AS2M.pt`다. 다른 위치를 쓰려면 두 명령 모두 첫 번째 인자로 경로를 지정한다.

2026-08-31 기준 공식 OneDrive 링크가 이 서버에서 HTTP 403을 반환했다. 스크립트가 같은 오류로 중단되면 공식 README의 `BEATs_iter3+ (AS2M)` 링크를 브라우저에서 내려받은 뒤 위 경로에 둔다. 출처가 불명확한 미러 파일로 대체하지 않는다.

## 체크포인트 구조

공식 예제 기준 파일은 PyTorch checkpoint이며 최상위에 `cfg`, `model` 키가 있어야 한다. `verify_checkpoint.py`는 이 구조와 SHA-256을 확인하고, 가중치를 실행하지 않도록 `weights_only=True` 로드부터 시도한다.
