# Specialist Pipeline v3

음성 존재, 음악 존재, 파일 Fake, 음성 Fake, 음악 Fake를 한 모델에 맡기지 않고 역할별 전문 모델에 분담한 세 번째 파이프라인 실험이다.

## 상태

- 외부 Voice Fake 검증: 완료
- WAV/MP3/FLAC 파이프라인 검증: 완료
- 실행 성능 측정: 완료
- DACON 공식 제출 결과: `NOT_REPORTED`

## 핵심 설계

```text
입력 오디오
├─ PANNs
│  ├─ VOICE_PRESENT_PROB
│  └─ MUSIC_PRESENT_PROB
├─ DF-Arena 1B (원본 전체)
│  └─ FILE_FAKE_PROB
├─ SSL-AASIST
│  └─ VOICE_FAKE_PROB
└─ DF-Arena 1B (음악 성분)
   └─ MUSIC_FAKE_PROB
```

HTDemucs는 모든 파일에 적용하지 않는다. PANNs의 음악 존재 확률이 `0.5` 이상인 혼합 파일에서만 vocals와 accompaniment를 분리한다. 순수 음성에는 원본을 그대로 사용한다.

## 문서 안내

- [`reports/experiment_report.md`](reports/experiment_report.md): 전체 실험 설명과 결과
- [`reports/metrics.json`](reports/metrics.json): 기계 판독 가능한 검증 수치
- [`configs/inference_design.yaml`](configs/inference_design.yaml): 출력 담당 모델과 조건부 routing
- [`runtime/runtime_profile.json`](runtime/runtime_profile.json): 속도·메모리 측정
- [`provenance/MODEL_INFO.md`](provenance/MODEL_INFO.md): 모델과 변환 정보
- [`assets/`](assets): 전달받은 원본 실험 캡처

## 주의

첨부 자료에는 이 파이프라인의 DACON 공식 Total, ADS, CPS, File EER, Music EER이 포함되지 않았다. 이전 Baseline과 두 번째 모델의 점수는 비교 배경으로만 기록했으며 이 실험의 공식 성능으로 간주하지 않는다.
