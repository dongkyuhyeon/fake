# Model and conversion information

## PANNs

- 역할: Voice/Music Presence
- 입력: 원본 오디오
- 상태: 기존 Baseline Presence를 유지
- 정확한 checkpoint revision: `NOT_REPORTED_IN_SOURCE`

## DF-Arena 1B

- 역할: File Fake 및 Music Fake
- File Fake 입력: 원본 전체 파일
- Music Fake 입력: 원본 또는 조건부 HTDemucs accompaniment
- 저장소에 기존 기록된 출처: `Speech-Arena-2025/DF_Arena_1B_V_1`
- 저장소에 기존 기록된 revision: `fb6ce85de12c2c5a509d89114adaf827dd75f49f`

## SSL-AASIST

- 역할: Voice Fake
- 입력: 원본 또는 조건부 HTDemucs vocals
- fine-tuned 가중치 보고 크기: 약 1.27GB
- 기존 초기 XLS-R fairseq 가중치 보고 크기: 약 3.8GB
- 원본 저장소와 정확한 revision: `NOT_REPORTED_IN_SOURCE`

## 제출용 변환

fine-tuned SSL-AASIST 내부의 XLS-R 가중치를 Transformers 형식으로 변환했다. 이 변환으로 fairseq 의존성과 중복 XLS-R 3.8GB 파일을 제거하고 Python 3.11 설치 위험을 줄였다.

- 비교 파일 수: 400
- 변환 전후 score 상관계수: `0.9999560`
- 변환 후 EER: `12.00%`
- 변환 후 ROC-AUC: `0.94904`

정확한 변환 코드, 변환 checkpoint checksum 및 라이선스 정보는 첨부 자료에 포함되지 않았으므로 별도 확인이 필요하다.
