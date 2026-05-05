# TTS Benchmark: Kokoro vs Coqui vs Piper

## Methodology
- Hardware: Apple M3 Pro / NVIDIA RTX 4090
- Metrics: RTF (real-time factor), MOS (mean opinion score proxy), cold-start latency

## Results

| Model | RTF | Quality | Local | Notes |
|-------|-----|---------|-------|-------|
| Kokoro v1.0 | 0.08 | High | Yes | Best balance, ONNX runtime |
| Coqui TTS | 0.15 | Medium | Yes | Large models, slower |
| Piper | 0.03 | Low-Med | Yes | Fast, robotic on long texts |
| ElevenLabs API | N/A | Very High | No | Cloud-only, per-char cost |

## Recommendation
Use Kokoro as default. Fallback to Piper for ultra-low-latency previews.
