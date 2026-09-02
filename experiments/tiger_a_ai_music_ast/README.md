# Tiger A — AI-Music AST frozen expert

## 상태

`IN_PROGRESS — RESULT NOT RECORDED`

이 디렉터리는 Tiger A 실험의 설정과 실행 산출물을 한곳에 정리하기 위한 전용 작업 공간이다. 현재는 폴더 구조만 준비한 상태이며, 점수·지표·성공 여부·실험 해석은 기록하지 않는다.

## 실험 범위

Tiger A는 기존 시스템을 기준으로 `AI-Music-Detection/ai_music_detection_large_10.24s`를 frozen Music Fake expert로 적용하는 실험이다. 기존 시스템의 다른 출력과 평가 조건은 유지하고, AI 음악 탐지 score의 유효성을 분리해서 확인한다.

명시적인 체크포인트 라이선스와 학습 데이터 이용 조건이 확인되기 전까지 해당 모델은 로컬 검증에만 사용하며 최종 제출 가중치에 포함하지 않는다.

## 디렉터리 구조

```text
tiger_a_ai_music_ast/
├── README.md       # 실험 목적, 범위 및 상태
├── configs/        # 실행에 사용한 YAML/JSON 설정
├── reports/        # 사람이 읽는 최종 실험 보고서
├── predictions/    # 파일별 예측 CSV/Parquet
├── runtime/        # 속도, VRAM, 패키지 크기 측정 결과
├── logs/           # 원본 실행 로그와 오류 로그
└── provenance/     # 모델 revision, 라이선스 및 데이터 출처
```

## 결과 기록 원칙

- 사용자가 실제 결과를 전달하거나 검증된 실행 산출물이 생성되기 전에는 수치를 작성하지 않는다.
- 측정하지 않은 지표는 추정하지 않고 `NOT_MEASURED`로 기록한다.
- Baseline과 Tiger A는 동일한 split, segment, seed 및 평가 코드를 사용한다.
- 모델 가중치, 원본 오디오, DACON 비공개 데이터와 인증정보는 Git에 저장하지 않는다.
- GitHub 업로드는 자동으로 수행하지 않고 사용자의 명시적인 요청이 있을 때만 진행한다.

## 예정 산출물 이름

실험 종료 후 검증된 파일만 다음 위치에 저장한다.

```text
configs/experiment_config.yaml
reports/experiment_report.md
reports/metrics.json
predictions/per_file_predictions.csv
predictions/slice_metrics.csv
predictions/error_cases.csv
runtime/runtime_profile.json
logs/execution.log
provenance/THIRD_PARTY_MODELS.md
```
