---
date: 2026-04-19
slug: smudge-stop-trying-to-survive-the-codec
description: Adversarial face perturbation has spent five years trying to make perturbations survive video compression. That framing is the bug. Smudge points the SPECTER inversion at libx264. Use the quantizer as the amplifier, not the obstacle.
authors:
  - digitalgrease
categories:
  - Digital
tags:
  - security
  - engineering
  - ai
comments: true
---

# Smudge: Stop Trying to Survive the Codec

Most published work on adversarial face perturbation is trying to solve the wrong problem.

The premise: make a perturbation that survives JPEG, H.264, Twitch's transcoder, YouTube's transcoder. That sets up a fight against systems specifically engineered to throw away exactly the kind of signal you're trying to inject. You can win individual rounds. The recompression pipeline always gets a rematch.

A different framing showed up in [SPECTER](https://blog.digitalgrease.dev/posts/specter-hunting-ghosts-in-the-kv-cache/) earlier this year, in a completely different domain: KV cache quantization in LLMs. The move was to stop treating quantization as the adversary and start treating it as the amplifier. Craft inputs that nudge values across quantization bin boundaries on purpose, and let the quantizer itself produce the large output drift you wanted in the first place.

The shape of that argument transfers. This post covers the survive-the-codec research lineage, why it keeps hitting the same wall, what the SPECTER framing buys when you point it at a video codec, what [smudge](https://github.com/mflowers/smudge) is doing about it, and, honestly, what's actually novel here vs. what's been in the air for a few years.

<!-- more -->

## The Survive-the-Codec Lineage

Face perturbation against face recognition is a well-trodden adversarial-ML problem. The arc since 2020 looks roughly like this:

- **[Fawkes](https://www.usenix.org/system/files/sec20-shan.pdf)** (Shan et al., USENIX Security 2020). The original "image cloaking" attack. Optimize a perturbation against an ensemble of face encoders so the target's "true" identity stops being the closest match. Reported 100% protection against AWS Rekognition, Azure Face, Face++ at release.
- **[LowKey](https://arxiv.org/abs/2101.07922)** (Cherepanova et al., ICLR 2021). Lagrange-multiplier formulation, LPIPS perceptibility penalty, Gaussian-smoothed copy as a JPEG proxy. AWS Rekognition rank-50 accuracy down to ~2.4% in their evaluation.
- **[TIP-IM](https://arxiv.org/abs/2003.06814)** (Yang et al., ICCV 2021). Open-set targeted identity protection.
- **[GIFT](https://arxiv.org/abs/2408.01428)** (ACM MM 2024). Current state-of-the-art for naturalistic methods, ~89.7% protection success vs. ~64.9% for CLIP2Protect on Face++/Aliyun/Tencent.

Two problems keep showing up.

The first is decay. [Radiya-Dixit & Tramèr](https://arxiv.org/abs/2106.14851) (2021, *"Data Poisoning Won't Save You from Facial Recognition"*) measured what happens when defenders move on. Fawkes, released July 2020, dropped to **0% protection** against MagFace, released March 2021. LowKey held against MagFace but collapsed to **24%** against a CLIP-finetuned face recognizer released the same month. Against an *adaptive* defender that adversarially trains on perturbed images, both Fawkes and LowKey drop to **3%**. The reproduction lives at [github.com/ftramer/FaceCure](https://github.com/ftramer/FaceCure). The asymmetry is structural: users perturb once and publish; defenders iterate forever.

The second is compression. The threat-model story for these tools is "your video gets indexed by a face-rec API." That video has been through a codec, usually multiple times, since livestream platforms transcode aggressively at ingest and again at distribution. Published work routinely shows survive-compression effectiveness collapsing under realistic recompression pipelines. The state-of-the-art response is a differentiable JPEG approximation in the training loop ([Reich et al. 2024, *Differentiable JPEG: The Devil is in the Details*](https://arxiv.org/abs/2309.06978), or [Guo et al. 2024](https://arxiv.org/abs/2402.16586) which sidesteps differentiable JPEG with a downsample-perturb-upsample loop), so perturbations are forced to live in the part of the spectrum the codec preserves.

That works at JPEG quality 90. It works less well at quality 50. It barely works through Twitch ingest. And there is essentially zero published work on the harder version of the problem: video codecs in the loop.

## Fighting the Codec Is Fighting Yourself

A lossy video codec exists to discard perceptually-irrelevant high-frequency content. That's the entire job. The DCT splits the signal by spatial frequency; the quantizer flattens the high-frequency coefficients more aggressively than the low-frequency ones; the entropy coder packs what's left.

Adversarial perturbations, in pixel space, mostly look like high-frequency noise. They have to. The perceptibility budget (typically L_inf 8/255, ~3.1% of dynamic range) only buys you that. You don't get to make low-frequency, large-amplitude changes; those would be visible.

So the survive-compression formulation says: *generate a high-frequency perturbation that survives an operation specifically designed to remove high-frequency content.* The two objectives are not just in tension. They are aimed in opposite directions by construction. You are training a network to find the narrow sliver of high-frequency space that the codec's specific quantization tables happen to preserve, and then betting that the next codec or the next bitrate setting also preserves that sliver. It often doesn't.

The conventional approach has been the right thing to do for years because it's the only thing that works at all. But it has a ceiling, and the ceiling is structural.

## The SPECTER Detour

SPECTER asked a different question about a different system. LLM inference quantizes the KV cache to 4 or 8 bits. The quantization step looks innocent: round each cached value to the nearest representable bin. But values that sit close to a bin boundary cross that boundary discontinuously under tiny input perturbations, and a crossing flips the cached value by the full quantization step.

That asymmetry is the attack surface. The input-space budget can be small (sub-token, sub-perceptible) because the quantizer does the amplification. You don't perturb the KV cache directly. You craft inputs whose un-quantized cache values land *just* on the wrong side of bin edges, and let the quantizer hand you a large drift in the cached representation for free.

Two things matter about that framing.

First, the leverage scales with quantization aggressiveness. Coarser quantization = wider bins = more coefficients within striking distance of edges = more leverage per input perturbation. The thing that "should" make the system more robust actually opens more attack surface.

Second, the attack lives at a level of indirection from the input. The perturbation does not have to be present in the input in any visible or meaningful way. It only has to be present after quantization. The input can look completely clean.

Both of those things are interesting in face perturbation for video.

## Mapping It onto Video

H.264, H.265, VP9, AV1, the entire production lossy-video-codec lineage, quantize DCT coefficients block-by-block. The quantization step is dominated by an integer-division-and-round operation against a quantization table. For livestream-typical bitrates the quantization is aggressive enough that the quantization parameter (QP) values sit in the 23–28 range, which means many coefficients are within a quantization step of a bin boundary at any given moment.

The bin-boundary leverage argument transplants without much modification. There exist input frames whose pre-quantized DCT coefficients sit close to bin edges, and small input perturbations cross those edges, and the post-decode reconstruction of the frame differs from the unperturbed version by something like the full quantization step in those coefficients. *And the perceptibility cost of the input perturbation can be much smaller than the resulting reconstruction shift,* because the quantizer is doing the amplification.

The clean version of this attack:

- **Don't** train a perturbation that lives in pixel space and survives the codec.
- **Do** train an input perturbation whose *post-decode* reconstruction is what shifts face-rec embeddings.

The conventional approach is weakest at aggressive recompression on livestream platforms. This approach should be strongest there. Lower bitrate = wider bins = more leverage.

That is the thesis. Whether it actually works for face recognition is the experiment.

## What Smudge Is

Smudge is the project I'm building against this thesis. Architecturally:

```
face_perturb/
├── capture/        # Virtual camera driver, video file ingest
├── detection/      # MediaPipe Tasks face detection + lightweight tracker
├── perturbation/   # ONNX Runtime inference, U-Net delta + L_inf clamp
├── output/         # Virtual camera output, file export
├── training/       # PyTorch adversarial training pipeline (MIT-licensed)
└── ui/             # Honesty/threat-level indicator, controls
```

The Python/Rust split is unavoidable. Virtual camera drivers are kernel-adjacent (v4l2loopback on Linux, CoreMediaIO on macOS, DirectShow/MediaFoundation on Windows) and the platform APIs do not do Python. The ML pipeline stays Python; the platform glue is Rust; frames cross the boundary over shared memory.

Two training tracks run in parallel.

**Track A: survive-compression.** The conservative path. Frozen face-rec ensemble (ArcFace IResNet-50 + AdaFace R100 + FaceNet, expanding to 6 models including a CLIP-based face encoder at v0.1). The CLIP encoder is in the v0.1 ensemble explicitly because the absence of CLIP in LowKey's ensemble is what cost LowKey 76 percentage points against a CLIP-finetuned defender in the Tramèr eval. Differentiable JPEG via [necla-ml/Diff-JPEG](https://github.com/necla-ml/Diff-JPEG) in the loop. This ships a working file-filter at v0.2 and a working video-call virtual camera at v0.3, with honest decay-curve numbers from day one. The [FaceCure](https://github.com/ftramer/FaceCure) adaptive-defender suite runs in the regression CI.

**Track B: codec-amplifier.** The research spike. Borrows the four-agent structure from SPECTER:

- **CodecInspector** instruments libx264 via PyAV, captures pre/post-quantization DCT coefficients per macroblock, surfaces per-block bin-edge-proximity heatmaps. Reconnaissance only.
- **PerturbationEngine** does gradient-guided search over input pixels with a straight-through estimator through the codec's quantization step. The STE trick that SPECTER uses through LLM weight quantization is directly applicable; the integer-division quantization step in H.264 has the same gradient-death problem.
- **BehaviorProbe** measures face-rec embedding drift on the *decoded* output, not the input. This is the load-bearing measurement shift.
- **ExploitSynthesizer** closes the loop with a multi-criteria objective (decoded-output embedding shift + input imperceptibility + transferability across QP settings).

Track B is gated on a proof-of-effect spike: at QP values typical of Twitch ingest, do random perturbations of input frames produce *systematically larger* post-decode face-rec embedding shifts than meaning-preserving input changes (translation jitter, brightness jitter, Gaussian noise)? If yes, signal exists and the full STE-through-libx264 pipeline is worth building. If no, write up the negative result and stop.

The proof-of-effect experiment costs ~$200–300 in rented GPU time and resolves cleanly either way. That's the right shape for a spike: cheap, decisive, publishable on either outcome.

## What's Actually Novel

The honest answer requires splitting "novel" along two axes.

**Not novel:** the conceptual move of treating quantization as the attack surface rather than an obstacle. SPECTER did it for LLM weight quantization. [RoVISQ](https://arxiv.org/abs/2203.10183) (NDSS 2023) attacked the quantization layer of *neural* video codecs (DVC), not standard H.264, but the framing is the same. [Sandwiched Compression](https://arxiv.org/abs/2402.05887) (Guleryuz et al. 2024) wraps a real codec with learned pre/post-processing using a differentiable JPEG proxy with STE quantization. Adjacent in spirit, different in target.

The general idea, *the quantizer is the leverage,* has been in the air for several years across multiple sub-fields.

**Novel as far as I can find:** the specific composition of (a) STE through *real, standard* libx264 quantization (b) driving (c) adversarial face-recognition embedding shifts on the decoded output, evaluated against (d) a frozen ensemble of production face-rec models. The closest prior work is [Reich et al. 2024 *Deep Video Codec Control for Vision Models*](https://arxiv.org/abs/2308.16215). Same shape: train against H.265-in-the-loop for a downstream vision task. They *explicitly punted on real-codec gradients in favor of a neural surrogate* because real-codec STE was not workable for them. They cite the gradient pathology. They describe the surrogate as a workaround.

That's the gap smudge is targeting. Not the inversion itself, which others have argued for in adjacent settings, but the demonstration that the inversion works against actual production face recognition through actual production video codecs.

It might not work. The Reich-2024 punt is informative. The fact that nobody published the real-codec STE result might just mean nobody has found one worth publishing yet.

## Why It Might Still Not Work

Five reasons to keep expectations honest:

1. **H.264 isn't pure DCT quantization.** It has rate-distortion-optimized mode decision, motion-compensated residuals for P/B-frames, deblocking filters, entropy coding. None of those have clean STE analogs. The gradient signal flowing back through the full encode/decode round trip may be too noisy to drive useful optimization, even if the DCT-quantization step in isolation cooperates.

2. **The STE through coarse quantization is documented to plateau and then collapse** in the LLM-quantization literature ([Yin et al. 2019](https://arxiv.org/abs/1903.05662), and the 2025 follow-ups). The biased-gradient regime is real. Vanilla identity-STE through libx264's quantizer is the documented failure case.

3. **Face-rec embeddings are deeper than LLM token logits.** SPECTER's signal lived one layer below the model output. Face-rec ensemble embeddings are the output of a 50–100-layer network; the pathway from a single DCT-coefficient flip to an embedding shift is much longer, and the gradient is correspondingly fainter.

4. **Cross-codec transfer is an open question.** A perturbation optimized against libx264 at QP=26 may have nothing to say about VP9 at the same nominal bitrate. The quantization tables and block structures are different. The clean version of the attack is per-codec, per-QP. The general version requires research that hasn't happened yet.

5. **Inter-frame coding is its own pathology.** P-frames and B-frames quantize motion-compensated residuals, not raw DCT coefficients. Whether the same bin-boundary leverage applies to residual quantization, and whether attacks on I-frame DCT quantization carry over to the inter-frame case, is genuinely unstudied.

This is a list of reasons the attack might not generalize, not reasons it definitely won't work. The point of the spike is to find out.

## The Honest Stopping Point

Smudge ships the survive-compression track first because that's what fits a tight cloud-GPU budget and produces a working artifact at v0.2. The codec-amplifier track runs in parallel as a research spike, gated on a discrete proof-of-effect experiment that resolves in two to three weeks of rented A100 time.

If signal shows up, the codec-amplifier approach becomes the primary mechanism for the livestream tier, exactly the tier where survive-compression is structurally weak. The threat model gets meaningfully better. If signal doesn't show up, that result is itself worth publishing, because it constrains what everyone else working on this should expect.

Either way the project commits to publishing the numbers: both the wins and the losses, both the oblivious-defender accuracy and the adaptive-defender accuracy via the [FaceCure](https://github.com/ftramer/FaceCure) suite, and the longitudinal decay curve as defenders iterate. That commitment matters more than any single architectural choice. The previous generation of this work shipped impressive day-one numbers and got broken in months. The differentiator is honesty about decay, not cleverness about perturbation.

The codec-amplifier inversion is the most interesting bet on the table. It might be wrong. We'll know.
