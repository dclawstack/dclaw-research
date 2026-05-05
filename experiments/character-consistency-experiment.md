# Character Consistency Experiment

## Goal
Maintain the same face across 5+ storyboard scenes using IP-Adapter.

## Setup
- Reference: single 512x512 portrait photo
- Model: SD 1.5 + IP-Adapter (faceid-plus)
- Prompts varied: "standing in office", "walking in park", "presenting on stage"

## Results
- IP-Adapter scale 0.5: good similarity, some drift in extreme angles
- IP-Adapter scale 0.7: very strong similarity, slight overfitting to reference pose
- IP-Adapter scale 0.6 + face restore: best balance

## Conclusion
Recommended default: 0.6 with GFP/CodeFormer face restore.
Store face embedding in `characters.face_embedding` for fast lookup.
