#!/usr/bin/env python3
"""경진대회 테스트 데이터에 대한 5개 확률값을 생성한다."""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

# 추론에는 model 폴더에 포함된 로컬 파일만 사용한다.
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
sys.dont_write_bytecode = True

import librosa
import numpy as np
import torch
import torchaudio
from demucs.apply import apply_model
from demucs.pretrained import get_model
from demucs.separate import load_track
from tqdm import tqdm
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification


# 경로 설정
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"
DF_ARENA_DIR = MODEL_DIR / "df_arena_1b"
HTDEMUCS_DIR = MODEL_DIR / "htdemucs"
AST_DIR = MODEL_DIR / "ast"

DEFAULT_TEST_DIR = Path("data") / "test"
DEFAULT_SAMPLE_SUBMISSION = Path("data") / "sample_submission.csv"
DEFAULT_OUTPUT_PATH = Path("output") / "submission.csv"

# 오디오 처리 설정
AUDIO_SAMPLE_RATE = 16_000
AST_SEGMENT_SAMPLES = 160_000
SEGMENT_SAMPLES = 64_600
SILENCE_RMS = 1e-5

PREDICTION_COLUMNS = [
    "FILE_FAKE_PROB",
    "VOICE_FAKE_PROB",
    "MUSIC_FAKE_PROB",
    "VOICE_PRESENT_PROB",
    "MUSIC_PRESENT_PROB",
]

SUPPORTED_AUDIO_EXTENSIONS = {
    ".aac", ".flac", ".m4a", ".mp3", ".ogg", ".opus", ".wav", ".wma"
}


# -----------------------------------------------------------------------------
# 1. 입력 파일 및 제출 양식 확인
# -----------------------------------------------------------------------------

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run the AST-assisted zero-shot audio deepfake baseline."
    )
    parser.add_argument("--test-dir", type=Path, default=DEFAULT_TEST_DIR)
    parser.add_argument(
        "--sample-submission", type=Path, default=DEFAULT_SAMPLE_SUBMISSION
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--device", choices=["cuda", "cpu"], default="cuda")
    return parser.parse_args()


def select_device(device_name):
    if device_name == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")
    return torch.device(device_name)


def find_audio_files(test_dir):
    if not test_dir.is_dir():
        raise FileNotFoundError(f"Test directory not found: {test_dir}")

    audio_files = []
    for path in test_dir.iterdir():
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
            audio_files.append(path)
    audio_files.sort(key=lambda path: path.stem)

    if not audio_files:
        raise FileNotFoundError(f"No audio files found in {test_dir}")

    audio_ids = [path.stem for path in audio_files]
    if len(audio_ids) != len(set(audio_ids)):
        raise ValueError("Audio IDs must be unique")
    return audio_files


def read_sample_submission(csv_path):
    if not csv_path.is_file():
        raise FileNotFoundError(f"Sample submission not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        column_names = reader.fieldnames
        rows = list(reader)

    if column_names is None or not rows:
        raise ValueError(f"Invalid sample submission: {csv_path}")

    required_columns = ["ID"] + PREDICTION_COLUMNS
    missing_columns = [name for name in required_columns if name not in column_names]
    if missing_columns:
        raise ValueError(f"Sample submission is missing columns: {missing_columns}")

    seen_ids = set()
    for row in rows:
        audio_id = str(row["ID"]).strip()
        if not audio_id:
            raise ValueError("Sample submission contains an empty ID")
        if audio_id in seen_ids:
            raise ValueError(f"Duplicate ID in sample submission: {audio_id}")
        seen_ids.add(audio_id)
        row["ID"] = audio_id

    return column_names, rows


def order_audio_files(audio_files, submission_rows):
    audio_by_id = {path.stem: path for path in audio_files}
    submission_ids = [row["ID"] for row in submission_rows]

    missing_ids = [audio_id for audio_id in submission_ids if audio_id not in audio_by_id]
    extra_ids = [audio_id for audio_id in audio_by_id if audio_id not in submission_ids]
    if missing_ids or extra_ids:
        raise ValueError(
            "Test audio and sample submission IDs do not match. "
            f"Missing: {missing_ids[:5]}, Extra: {extra_ids[:5]}"
        )

    return [audio_by_id[audio_id] for audio_id in submission_ids]


def load_audio(audio_path):
    audio, _ = librosa.load(
        audio_path, sr=AUDIO_SAMPLE_RATE, mono=True, dtype=np.float32
    )
    if audio.size == 0 or not np.isfinite(audio).all():
        raise ValueError(f"Invalid audio: {audio_path}")
    return audio


# -----------------------------------------------------------------------------
# 2. 오디오 구간 분할
# -----------------------------------------------------------------------------

def get_segment_starts(audio_length, segment_samples=SEGMENT_SAMPLES):
    if audio_length <= segment_samples:
        return [0]

    last_start = audio_length - segment_samples
    starts = list(range(0, last_start + 1, segment_samples))
    if starts[-1] != last_start:
        starts.append(last_start)
    return starts


def extract_segment(audio, start, segment_samples=SEGMENT_SAMPLES, repeat=True):
    if audio.size < segment_samples:
        if not repeat:
            return audio.astype(np.float32, copy=False)
        repeat_count = segment_samples // audio.size + 1
        audio = np.tile(audio, repeat_count)
        return audio[:segment_samples].astype(np.float32)

    end = start + segment_samples
    return audio[start:end].astype(np.float32, copy=False)


# -----------------------------------------------------------------------------
# 3. AST를 이용한 음성·음악 존재 여부 추론
# -----------------------------------------------------------------------------

VOICE_LABELS = [
    "Speech",
    "Male speech, man speaking",
    "Female speech, woman speaking",
    "Child speech, kid speaking",
    "Conversation",
    "Narration, monologue",
    "Babbling",
    "Speech synthesizer",
    "Singing",
    "Choir",
    "Male singing",
    "Female singing",
    "Child singing",
    "Synthetic singing",
    "Rapping",
    "Humming",
    "Chant",
    "Mantra",
]

MUSIC_LABELS = [
    "Music",
    "Musical instrument",
    "Plucked string instrument",
    "Guitar",
    "Electric guitar",
    "Bass guitar",
    "Acoustic guitar",
    "Steel guitar, slide guitar",
    "Tapping (guitar technique)",
    "Strum",
    "Banjo",
    "Sitar",
    "Mandolin",
    "Zither",
    "Ukulele",
    "Keyboard (musical)",
    "Piano",
    "Electric piano",
    "Organ",
    "Electronic organ",
    "Hammond organ",
    "Synthesizer",
    "Sampler",
    "Harpsichord",
    "Percussion",
    "Drum kit",
    "Drum machine",
    "Drum",
    "Snare drum",
    "Rimshot",
    "Drum roll",
    "Bass drum",
    "Timpani",
    "Tabla",
    "Cymbal",
    "Hi-hat",
    "Wood block",
    "Tambourine",
    "Rattle (instrument)",
    "Maraca",
    "Gong",
    "Tubular bells",
    "Mallet percussion",
    "Marimba, xylophone",
    "Glockenspiel",
    "Vibraphone",
    "Steelpan",
    "Orchestra",
    "Brass instrument",
    "French horn",
    "Trumpet",
    "Trombone",
    "Bowed string instrument",
    "String section",
    "Violin, fiddle",
    "Pizzicato",
    "Cello",
    "Double bass",
    "Wind instrument, woodwind instrument",
    "Flute",
    "Saxophone",
    "Clarinet",
    "Harp",
    "Bell",
    "Accordion",
    "Bagpipes",
    "Didgeridoo",
    "Shofar",
    "Theremin",
    "Background music",
    "Theme music",
    "Jingle (music)",
    "Soundtrack music",
    "Video game music",
    "Pop music",
    "Hip hop music",
    "Rock music",
    "Heavy metal",
    "Punk rock",
    "Grunge",
    "Progressive rock",
    "Rock and roll",
    "Psychedelic rock",
    "Rhythm and blues",
    "Soul music",
    "Reggae",
    "Country",
    "Swing music",
    "Bluegrass",
    "Funk",
    "Folk music",
    "Middle Eastern music",
    "Jazz",
    "Disco",
    "Classical music",
    "Opera",
    "Electronic music",
    "House music",
    "Techno",
    "Dubstep",
    "Drum and bass",
    "Electronica",
    "Electronic dance music",
    "Ambient music",
    "Trance music",
    "Music of Latin America",
    "Salsa music",
    "Flamenco",
    "Blues",
    "New-age music",
    "Music of Africa",
    "Music of Asia",
    "Carnatic music",
    "Music of Bollywood",
    "Traditional music",
    "Independent music",
    "Dance music",
]


def load_ast_model(device):
    extractor = AutoFeatureExtractor.from_pretrained(
        AST_DIR,
        local_files_only=True,
    )
    model = AutoModelForAudioClassification.from_pretrained(
        AST_DIR,
        local_files_only=True,
        use_safetensors=True,
    ).to(device).eval()

    label_to_index = {
        str(label): int(index) for index, label in model.config.id2label.items()
    }
    missing_labels = [
        label
        for label in VOICE_LABELS + MUSIC_LABELS
        if label not in label_to_index
    ]
    if missing_labels:
        raise ValueError(f"AST config is missing labels: {missing_labels}")

    voice_indices = [label_to_index[label] for label in VOICE_LABELS]
    music_indices = [label_to_index[label] for label in MUSIC_LABELS]
    return extractor, model, voice_indices, music_indices


def make_ast_segments(audio):
    starts = get_segment_starts(audio.size, AST_SEGMENT_SAMPLES)
    return [
        extract_segment(
            audio,
            start,
            segment_samples=AST_SEGMENT_SAMPLES,
            repeat=False,
        )
        for start in starts
    ]


def predict_presence(extractor, model, voice_indices, music_indices, audio, device):
    segments = make_ast_segments(audio)
    inputs = extractor(
        segments,
        sampling_rate=AUDIO_SAMPLE_RATE,
        return_tensors="pt",
        padding=True,
    )
    input_values = inputs["input_values"].to(device)

    with torch.inference_mode():
        with torch.cuda.amp.autocast(enabled=device.type == "cuda"):
            logits = model(input_values=input_values).logits
        probabilities = torch.sigmoid(logits.float())

    voice_probability = float(probabilities[:, voice_indices].max())
    music_probability = float(probabilities[:, music_indices].max())
    return voice_probability, music_probability


def predict_presence_for_all_files(audio_files, device):
    extractor, model, voice_indices, music_indices = load_ast_model(device)
    presence_scores = {}

    for audio_path in tqdm(audio_files, desc="AST presence"):
        audio = load_audio(audio_path)
        presence_scores[audio_path.stem] = predict_presence(
            extractor,
            model,
            voice_indices,
            music_indices,
            audio,
            device,
        )

    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return presence_scores


# -----------------------------------------------------------------------------
# 4. HTDemucs를 이용한 음성·음악 분리
# -----------------------------------------------------------------------------

def load_htdemucs_model():
    original_torch_load = torch.load

    def load_trusted_checkpoint(*args, **kwargs):
        # PyTorch 2.6부터 바뀐 기본값에 맞춰 기존 체크포인트를 불러온다.
        kwargs.setdefault("weights_only", False)
        try:
            return original_torch_load(*args, **kwargs)
        except TypeError as error:
            # PyTorch 2.5 이하는 weights_only 인자를 지원하지 않을 수 있다.
            if "weights_only" not in str(error):
                raise
            kwargs.pop("weights_only", None)
            return original_torch_load(*args, **kwargs)

    torch.load = load_trusted_checkpoint
    try:
        model = get_model("htdemucs", repo=HTDEMUCS_DIR)
    finally:
        torch.load = original_torch_load
    return model.cpu().eval()


def separate_voice_and_music(audio_path, model, device):
    waveform = load_track(
        audio_path, model.audio_channels, model.samplerate
    ).float()
    mono_waveform = waveform.mean(0)
    mean = mono_waveform.mean()
    std = mono_waveform.std()

    if float(std) < 1e-8:
        length = round(waveform.shape[-1] * AUDIO_SAMPLE_RATE / model.samplerate)
        silence = np.zeros(max(1, length), dtype=np.float32)
        return silence, silence.copy()

    normalized_waveform = (waveform - mean) / std
    with torch.inference_mode():
        sources = apply_model(
            model,
            normalized_waveform[None],
            device=device,
            shifts=0,
            split=True,
            overlap=0.25,
            progress=False,
        )[0]
    sources = sources * std + mean

    vocal_index = model.sources.index("vocals")
    voice_audio = sources[vocal_index].mean(0, keepdim=True)

    music_sources = []
    for index, source_name in enumerate(model.sources):
        if source_name != "vocals":
            music_sources.append(sources[index])
    music_audio = torch.stack(music_sources).sum(0).mean(0, keepdim=True)

    voice_audio = torchaudio.functional.resample(
        voice_audio, model.samplerate, AUDIO_SAMPLE_RATE
    )[0]
    music_audio = torchaudio.functional.resample(
        music_audio, model.samplerate, AUDIO_SAMPLE_RATE
    )[0]
    return (
        voice_audio.cpu().numpy().astype(np.float32),
        music_audio.cpu().numpy().astype(np.float32),
    )


# -----------------------------------------------------------------------------
# 5. DF-Arena 1B를 이용한 성분별 Fake 추론
# -----------------------------------------------------------------------------

def load_df_arena_model(device):
    if str(MODEL_DIR) not in sys.path:
        sys.path.insert(0, str(MODEL_DIR))
    from df_arena_1b.modeling_antispoofing import DF_Arena_1B_Antispoofing

    previous_directory = Path.cwd()
    os.chdir(DF_ARENA_DIR)
    try:
        model = DF_Arena_1B_Antispoofing.from_pretrained(
            str(DF_ARENA_DIR),
            local_files_only=True,
            low_cpu_mem_usage=True,
        )
    finally:
        os.chdir(previous_directory)

    # 구형 PyTorch의 weight_norm 키 이름과 최신 체크포인트 키 이름을 맞춘다.
    legacy_prefix = "backbone.ssl_model.encoder.pos_conv_embed.conv"
    legacy_keys = {
        f"{legacy_prefix}.weight_g": f"{legacy_prefix}.parametrizations.weight.original0",
        f"{legacy_prefix}.weight_v": f"{legacy_prefix}.parametrizations.weight.original1",
    }
    model_keys = set(model.state_dict())
    if all(key in model_keys for key in legacy_keys):
        checkpoint_path = DF_ARENA_DIR / "pytorch_model.bin"
        try:
            checkpoint = torch.load(
                checkpoint_path,
                map_location="cpu",
                weights_only=True,
            )
        except TypeError:
            checkpoint = torch.load(checkpoint_path, map_location="cpu")

        compatibility_weights = {
            old_key: checkpoint[new_key]
            for old_key, new_key in legacy_keys.items()
        }
        model.load_state_dict(compatibility_weights, strict=False)
        del checkpoint, compatibility_weights

    model = model.to(device).eval()
    fake_label_index = int(model.config.label2id["spoof"])
    return model, fake_label_index


def calculate_rms(audio):
    return float(np.sqrt(np.mean(np.square(audio, dtype=np.float64))))


def predict_fake(model, fake_label_index, audio, device):
    if calculate_rms(audio) < SILENCE_RMS:
        return 0.0

    segment_scores = []
    for start in get_segment_starts(audio.size):
        segment = extract_segment(audio, start)
        segment_tensor = torch.from_numpy(segment).to(device)

        with torch.inference_mode():
            logits = model(input_values=segment_tensor)["logits"]
            probabilities = torch.softmax(logits.float(), dim=-1)
        segment_scores.append(float(probabilities[0, fake_label_index]))

    return max(segment_scores)


# -----------------------------------------------------------------------------
# 6. 파일 단위 점수 계산 및 제출 파일 저장
# -----------------------------------------------------------------------------

def combine_file_fake_score(voice_fake, music_fake, voice_present, music_present):
    voice_score = voice_present * voice_fake
    music_score = music_present * music_fake
    return max(voice_score, music_score)


def predict_fake_scores_for_all_files(
    audio_files, submission_rows, presence_scores, device
):
    df_arena_model, fake_label_index = load_df_arena_model(device)
    htdemucs_model = load_htdemucs_model()

    for index, audio_path in enumerate(tqdm(audio_files, desc="Components")):
        voice_audio, music_audio = separate_voice_and_music(
            audio_path, htdemucs_model, device
        )
        voice_fake = predict_fake(
            df_arena_model, fake_label_index, voice_audio, device
        )
        music_fake = predict_fake(
            df_arena_model, fake_label_index, music_audio, device
        )

        voice_present, music_present = presence_scores[audio_path.stem]
        file_fake = combine_file_fake_score(
            voice_fake, music_fake, voice_present, music_present
        )

        row = submission_rows[index]
        row["FILE_FAKE_PROB"] = round(file_fake, 10)
        row["VOICE_FAKE_PROB"] = round(voice_fake, 10)
        row["MUSIC_FAKE_PROB"] = round(music_fake, 10)
        row["VOICE_PRESENT_PROB"] = round(voice_present, 10)
        row["MUSIC_PRESENT_PROB"] = round(music_present, 10)

    return submission_rows


def save_submission(output_path, column_names, rows):
    for row in rows:
        for column in PREDICTION_COLUMNS:
            value = float(row[column])
            if not np.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"Invalid probability for {row['ID']} {column}: {value}"
                )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=column_names)
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_arguments()
    device = select_device(args.device)

    # 1. 테스트 파일을 제출 양식의 ID 순서에 맞춘다.
    audio_files = find_audio_files(args.test_dir)
    column_names, submission_rows = read_sample_submission(args.sample_submission)
    audio_files = order_audio_files(audio_files, submission_rows)

    # 2. AST로 파일별 음성·음악 존재 확률을 계산한다.
    presence_scores = predict_presence_for_all_files(audio_files, device)

    # 3. 음성과 음악을 분리한 뒤 성분별 Fake 확률을 계산한다.
    submission_rows = predict_fake_scores_for_all_files(
        audio_files, submission_rows, presence_scores, device
    )

    # 4. 5개 예측값을 제출 파일로 저장한다.
    save_submission(args.output, column_names, submission_rows)
    print(f"Saved {len(submission_rows)} predictions to {args.output}")


if __name__ == "__main__":
    main()
