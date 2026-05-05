# ComfyUI Workflow Notes

## FLUX Image Generation
- Checkpoint: `flux1-dev.safetensors`
- CLIP: built-in
- Resolution: 1280x720 for 16:9 video
- Steps: 20-30
- CFG: 1.0 (guidance-distilled)
- Sampler: euler

## AnimateDiff Video Generation
- Model: `animatediff-v3.safetensors`
- Motion module: `mm_sd_v15_v3.ckpt`
- Frames: 16
- FPS: 8 (output 2s clip)
- Resolution: 512x512 or 768x432
- For longer clips, use sliding window or VFI

## LivePortrait (Face Animation)
- Use reference image from Character model
- Driving video: generated or uploaded
- Apply to talking-head scenes

## IP-Adapter (Character Consistency)
- Model: `ip-adapter_sd15.bin`
- Image encoder: `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors`
- Reference image uploaded per project
- Scale: 0.6-0.8 for strong consistency without overfitting
