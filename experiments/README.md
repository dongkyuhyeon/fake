# Experiments

이 디렉터리는 오디오 딥페이크 탐지 실험을 독립된 폴더로 관리한다. 각 실험은 목적, 설정, 보고서, 정형 지표, 실행 성능 및 모델 출처를 분리해서 기록한다.

## 실험 목록

| 폴더 | 내용 | 현재 기록 상태 |
|---|---|---|
| [`ast_zero_shot`](ast_zero_shot) | MIT AST Presence와 기존 ADS 로직을 결합한 zero-shot 실험 | DACON 결과 기록됨 |
| [`ast_deepfake_finetune`](ast_deepfake_finetune) | AST deepfake-domain fine-tuning 데이터 및 설계 | 계획 문서 |
| [`tiger_a_ai_music_ast`](tiger_a_ai_music_ast) | AI-Music AST frozen expert 전용 작업 공간 | 결과 미기록 |
| [`specialist_pipeline_v3`](specialist_pipeline_v3) | PANNs·DF-Arena·SSL-AASIST 역할 분담 파이프라인 | 외부 Voice 검증 기록, 공식 결과 미기록 |

## 공통 저장 원칙

- 실제로 측정된 결과만 기록한다.
- 공식 DACON 결과와 외부 validation 결과를 구분한다.
- 모델 가중치, 원본 데이터와 비공개 평가 데이터는 Git에 올리지 않는다.
- 모델 revision, 라이선스 및 데이터 출처는 각 실험의 provenance 문서에 기록한다.
- GitHub 업로드는 사용자가 요청할 때만 수행한다.
