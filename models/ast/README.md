# MIT AST AudioSet

## 역할

`MIT/ast-finetuned-audioset-10-10-0.4593`를 공통 오디오 인코더로 사용한다.

- AudioSet 출력으로 speech/music presence 계산
- 마지막 hidden state를 pooling해 범용 오디오 특징 생성
- 최초 결과에서는 기존 ADS 판정 로직 유지
- 후속 실험에서는 AST 특징 위에 fake/real 분류기 학습

## 모델 준비

```bash
python models/ast/download_model.py
python models/ast/verify_model.py
```

기본 저장 위치는 `/workspace/model_artifacts/ast`다. 제출 패키지를 만들 때 이 디렉터리를 패키지 내부 모델 경로로 복사하고 `local_files_only=True`로 불러온다.

## 출력 결합

```text
speech presence = speech 계열 AudioSet 확률 집계
music presence  = music 계열 AudioSet 확률 집계
file fake       = 기존 ADS 판정 결과
```

presence 임계값과 구간별 pooling 방식은 검증 결과에 따라 별도로 조정한다.
