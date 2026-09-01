# Data and generator registry

> 확인일: 2026-09-01. 실제 다운로드 시점에 라이선스와 revision을 다시 확인한다.

| 역할 | 자원 | 사용 조건 요약 | 공식 출처 |
|---|---|---|---|
| real speech | Common Voice Korean | dataset CC0 1.0; Mozilla 배포 조건 별도 확인 | https://commonvoice.mozilla.org/en/datasets |
| real speech | LibriSpeech | CC BY 4.0 | https://www.openslr.org/12/ |
| real music | MTG-Jamendo | 비영리 연구/학술; 트랙별 CC 라이선스 확인 | https://github.com/MTG/mtg-jamendo-dataset |
| no-component | ESC-50 | CC BY-NC; speech/music class 제외 | https://github.com/karolpiczak/ESC-50 |
| fake speech | MeloTTS | MIT; 한국어·영어 지원 | https://github.com/myshell-ai/MeloTTS |
| fake speech | OpenVoice V2 | MIT; 한국어 포함 다국어 voice cloning | https://github.com/myshell-ai/OpenVoice |
| fake speech holdout | Bark | MIT repository; 한국어·영어 지원 | https://github.com/suno-ai/bark |
| fake music | MusicGen/AudioCraft | code MIT, released weights CC BY-NC 4.0 | https://github.com/facebookresearch/audiocraft |
| fake music | AudioLDM2 | repository license CC BY-NC-SA 4.0 | https://github.com/haoheliu/AudioLDM2 |
| fake music holdout | Stable Audio Open | Stability AI Community License | https://huggingface.co/stabilityai/stable-audio-open-1.0 |

## 다운로드 시 남길 증빙

- 원천 URL과 접근 날짜
- release, Git commit 또는 Hugging Face revision
- 라이선스 원문 사본과 attribution 목록
- 원본 archive 및 모델 weight SHA-256
- 다운로드/생성 명령과 실행 환경
- API를 사용하면 서비스명, 모델 버전, 요청 파라미터와 당시 이용약관

이 표는 사용 승인표가 아니라 후보 등록표다. 실제 사용 여부는 `source_registry.csv`에서 `license_review=approved`인 항목으로 제한한다.

