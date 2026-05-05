# Video Generation Benchmark

## Models Tested
- AnimateDiff v3
- AnimateDiff v2 + MotionAdapter
- Stable Video Diffusion (SVD)
- CogVideoX

## Metrics
- Seconds per 16-frame 512x512 clip
- Temporal consistency score (manual 1-5)
- Prompt adherence (CLIP score proxy)

## Results

| Model | Sec/Clip | Consistency | Prompt Adherence | Local? |
|-------|----------|-------------|------------------|--------|
| AnimateDiff v3 | 45s | 4 | 4.2 | Yes |
| SVD | 120s | 3.5 | 3.8 | Yes |
| CogVideoX | 300s | 4.5 | 4.6 | Yes |
| Runway Gen-3 | N/A | 5 | 4.9 | No |

## Recommendation
AnimateDiff v3 for speed, CogVideoX for quality on high-end GPUs.
