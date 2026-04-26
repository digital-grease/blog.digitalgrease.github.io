---
date: 2026-04-02
slug: specter-hunting-ghosts-in-the-kv-cache
description: Two research domains have been studying KV cache attacks and quantization exploitation separately. SPECTER bridges the gap, testing whether crafted input tokens can exploit quantization boundaries in the KV cache to manipulate model behavior through normal inference.
authors:
  - digitalgrease
categories:
  - Digital
tags:
  - security
  - engineering
  - ai
comments: true
series: SPECTER
series_part: 1
series_parts:
  - title: "SPECTER: Hunting Ghosts in the KV Cache"
    url: /posts/specter-hunting-ghosts-in-the-kv-cache/
  - title: "Smudge: Stop Trying to Survive the Codec"
    url: /posts/smudge-stop-trying-to-survive-the-codec/
---

# SPECTER: Hunting Ghosts in the KV Cache

Production LLM inference runs on a lie of convenience. Every major serving platform (vLLM, SGLang, TGI) compresses its KV cache with quantization to keep memory from spiraling. INT4, INT8, NF4. Pick your poison. The math works. The throughput improves. And in multi-tenant environments, cached prefixes get shared across users because why compute the same thing twice?

Nobody asks what happens when you treat the cache as an attack surface. Or rather, two separate groups of researchers have been asking, but they've been asking different questions in different rooms.

<!-- more -->

## Two Rooms, One Gap

The first room studies KV cache manipulation. Ganesh et al. demonstrated "History Swapping": overwrite cached key-value blocks directly and you can redirect topic, inject context, steer generation. Hossain et al. went further with MTI, applying Gaussian noise, zeroing, and orthogonal rotation to cached tensors. They proved the cache is a viable attack surface. Mid-layer sensitivity peaks. Perturbations propagate.

The catch: both require direct write access to the cache. That's a strong assumption. You need to be inside the serving infrastructure, with access to the tensor store. Valid threat model for a compromised host. Not something you pull off from the API.

The second room studies quantization exploitation. Egashira et al. showed that quantization boundaries in model weights are exploitable. Fine-tuning plus projected gradient descent can push weight values across bin edges, flipping model behavior while the quantized model looks numerically identical to audits. Song et al. scaled this to 86-97% attack success rates across refusal bypass, jailbreak, and content injection scenarios.

The catch: they target static weights. The attack happens at training or fine-tuning time. You modify the model itself. Useful research, but it requires model access, not just inference access.

Here's the gap. Nobody has asked: **can crafted input tokens push KV cache values across quantization boundaries during normal inference, steering generation without ever touching the cache directly?**

That's what SPECTER is built to answer.

## What the Research Shows

The pieces are there. You just have to read across the aisle.

PROMPTPEEK (NDSS 2025) demonstrated gradient-based prompt reconstruction from shared prefix caches in SGLang. Not a theoretical concern, a working attack against a production-grade serving framework. The shared KV cache isn't an implementation detail. It's a live attack surface.

Song et al.'s "Early Bird" work showed that timing analysis alone can recover token-by-token prefix information from GPT-4 and Gemini APIs. Gu et al. confirmed prompt caching is exploitable across seven commercial providers through statistical timing. Luo et al. documented plaintext KV transmission between nodes and GPU memory leaks via LeftoverLocals.

These are all read-side attacks. They prove the surface exists and that production systems are exposed. But they don't write to the cache through the front door.

On the quantization side, the math from Egashira et al. is directly applicable. Quantization maps continuous values to discrete bins. Values near bin edges are unstable. A small perturbation in the input space can push the quantized representation into an adjacent bin, creating a disproportionate change in the dequantized output. This is the mechanism that makes weight-level attacks work.

KV cache values are computed from input tokens through attention. Different inputs produce different key and value tensors. If an input token substitution shifts a value that sits near a quantization boundary, the post-quantization representation changes discontinuously. The perturbation gets amplified, not smoothed.

The question isn't whether the physics works. It's whether the effect is large enough to matter, whether it can be directed, and whether it survives through the rest of the forward pass to change what the model actually generates.

## Three Ways This Could Hurt

SPECTER defines three concrete attack scenarios.

**Cross-tenant data leakage.** Multi-tenant platforms with prefix caching (vLLM's default configuration) share cache entries across users. An attacker crafts a request that poisons a shared prefix entry. The next user whose request hits that cached prefix gets completions contaminated by the attacker's perturbation. The model leaks or reconstructs context from the poisoned cache segment. You don't need to steal the data. You make the model hand it over in its own completions.

**Privilege escalation in agentic networks.** This one keeps me up at night. Gateway agents evaluate user permissions before dispatching to downstream tools and agents. The gateway's decision lives in the KV cache as part of the context window. A semantically benign request that carries adversarial tokens poisons the gateway's cache at the permission-evaluation step. The gateway misclassifies privilege level. Downstream agents trust the gateway's assessment because that's the entire point of the architecture. Elevated privileges propagate through the chain without any single agent seeing anything overtly malicious.

**System prompt extraction and injection.** The system prompt occupies the first segment of the KV cache and persists across turns. It's the most stable, most reused, and most security-critical cached content. Adversarial tokens in user messages corrupt attention patterns over the cached system prompt. The model either leaks the system prompt through its completions or begins ignoring the instructions it contains. Both outcomes are bad.

## How SPECTER Works

SPECTER is a five-agent framework, each agent independently testable, each addressing a specific link in the attack chain.

**CacheInspector** hooks into transformer attention layers using PyTorch forward hooks. It captures KV tensors before and after quantization, computes per-head L2 distances and cosine similarities, and serializes snapshots to safetensors for reproducible diffing. This is the reconnaissance layer. You can't exploit what you can't observe.

**PerturbationEngine** searches the token space for substitutions that maximize post-quantization cache divergence. Three strategies, increasing in sophistication: random search as a baseline, greedy coordinate descent that optimizes one token position at a time, and gradient-guided search using a straight-through estimator to backpropagate through the discrete quantization operation. The STE is critical. Without it, gradients die at the quantization step and you're back to random search.

**BehaviorProbe** measures whether cache-level perturbations actually change model behavior. KL divergence on output logits tells you the distribution shifted. Top-k overlap and rank shifts tell you whether the model's preferred tokens changed. Semantic drift via sentence-transformer embeddings tells you if the meaning moved. Attack success rate gives you a binary answer. Perplexity tells you if quality degraded. Trajectory analysis with sliding windows shows when and how the effect manifests across generation steps.

**ExploitSynthesizer** closes the loop. It orchestrates the other agents in a profile, perturb, evaluate, refine cycle, combining CacheInspector's observations with PerturbationEngine's search and BehaviorProbe's measurements. Multi-criteria success evaluation ensures you're not chasing a metric artifact. You need KL divergence *and* measurable behavioral change *and* specific token probability shifts before calling an attack successful.

**Coordinator** handles the CLI, async task dispatch, and experiment lifecycle through a Typer-based interface. Experiments are defined as YAML matrices: model × strategy × prompt category × seed. A single config file expands to dozens of reproducible runs tracked in SQLite.

Above the core agents sits a research automation layer: eight additional agents that handle environment validation, failure diagnosis, auto-repair (OOM handling, configuration fixes), result aggregation, statistical analysis, and even paper draft generation through Jinja2 LaTeX templates. The full research loop runs as a state machine from environment check through to paper drafting.

354 tests pass on CPU. The framework is built. The question it was built to answer still is.

## The Research Path

Phase 1 is signal detection. Load a small model (TinyLlama-1.1B) with INT4 quantization on GPU. Verify the hooks capture pre- and post-quantization tensors correctly. Then run the baseline experiment: 50 random token substitutions versus 50 semantic rephrasings. If random substitutions produce systematically larger post-quantization KV divergence than meaning-preserving rephrasings, there's a signal. The effect is real and exploitable tokens exist.

Next, boundary proximity analysis. What fraction of cache values actually sit near quantization boundaries at INT4? If it's 2%, the attack surface is thin. If it's 15%, there's room to work. Correlate proximity with layer position. Mid-layers should show the highest sensitivity based on Hossain et al.'s findings.

Then validate that optimization works. Does greedy coordinate descent outperform random search? If yes, the optimization landscape is navigable and gradient-guided search should do even better.

Phase 2 bridges divergence to behavior. Take the top-10 and bottom-10 perturbations ranked by KV divergence. Measure KL divergence in output logits, top-k overlap, and semantic drift between the groups. If high-divergence perturbations don't produce measurably different outputs, the effect is real but doesn't survive the forward pass. Interesting but not exploitable.

The targeted attack test: sentiment flipping. "The movie was" ... can gradient-guided search with boundary-aware loss shift P("great") versus P("terrible")? Twenty trials. If the attack success rate is significantly above chance, the chain from input tokens through quantization boundaries to behavioral change is complete.

Negative results here are still valuable. The literature has no data on this specific question. If the chain breaks, if quantization boundaries in the cache aren't exploitable through input perturbation, understanding where and why it fails constrains the threat model for everyone working on KV cache security.

## The Gap Was Always There

Quantization is everywhere in production inference. It's not optional at scale. It's how you serve models to millions of users without melting your GPU budget. Shared KV caches are the norm in multi-tenant deployments. These aren't exotic configurations. They're the default.

Current defenses don't cover this vector. SafeKV's reuse diversity monitoring watches for anomalous cache sharing patterns, but input-level attacks look like normal inference. RedVisor's zero-copy architecture focuses on prompt injection detection, not cache-level perturbation. If input tokens can reliably poison the KV cache through quantization boundary exploitation, the entire defense posture needs to shift from "protect the cache from unauthorized access" to "the cache is hostile by construction."

SPECTER is the tool built to test that premise. The framework is complete. The research path is defined. The two rooms have been running separate experiments for years without speaking to each other. SPECTER asks the question in the hallway between them.
