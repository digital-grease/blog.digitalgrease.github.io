---
date: 2026-04-26
slug: meridian-drift-audit-with-receipts
description: Meridian is live. A longitudinal record of how commercial LLMs drift on contested topics — what v0.1 runs, how it's defensible, and what each tier of funding unlocks.
authors:
  - digitalgrease
categories:
  - Digital
tags:
  - ai
  - engineering
  - transparency
comments: true
---

# Meridian: drift audit, with receipts

**Meridian is live at [meridianaudit.org](https://meridianaudit.org).**

It is a longitudinal measurement of political, epistemic, and behavioral drift in deployed commercial LLMs. A fixed prompt corpus is queried weekly against major providers; responses are stored append-only with full version metadata; a public dashboard publishes statistically rigorous drift reports with receipts.

This post is the v0.1 launch note: what's running, what isn't, what it costs, and what it would take to make it more.

<!-- more -->

## The measurement that didn't exist

HELM and LMSYS Arena measure capability and preference. They do that well. Neither one tells you what model the deployed system was last week, what it declined to discuss this week, how the framing on a contested topic moved between two snapshots, or whether a refusal boundary quietly shifted after a silent provider update.

Nobody was measuring **whose side the model is on this month and how that differs from last month**, with a versioned corpus and a public raw-data export. That is the gap Meridian fills.

LLMs are increasingly the default knowledge interface. Whatever a model declines to discuss, reframes, caveats, or presents as settled — at scale — shapes what many people consider thinkable. Training-data curation is ideological curation. RLHF is normative curation. These choices are currently invisible to the public and change without notice or changelog.

A public drift record converts opaque decisions into measurable facts. Useful for journalists covering AI policy, researchers studying alignment, regulators evaluating concentration risk, and anyone making informed choices about which tools to depend on.

## What v0.1 actually runs

I'll be specific, because vague launch posts are how projects fail to get audited.

The current configuration is **Level 0**: `~$86/month`, volunteer-funded:

- **Corpus**: 30 public prompts, versioned, in `meridian/corpus/prompts.yaml`. Held-out corpus is committed as a template only; populating the real held-out set is gated on Level 4 funding so the file is never accidentally published.
- **Models**: Claude Opus 4.7 on even ISO weeks, GPT-5 Preview on odd ISO weeks, Ollama `llama3.2:3b` every week.
- **Sampling**: N=20 at provider-default temperature, N=5 at temperature=0 where supported.
- **Storage**: append-only JSONL local store, with a per-week `responses.jsonl.gz` snapshot committed to `main`. Retention is forever.
- **Site**: static, built weekly by a GitHub Actions workflow, deployed to GitHub Pages with a custom domain. The build refuses to run if a held-out prompt ever leaks into the public manifest.

Ollama is enabled by default in `meridian/config.yaml` because it costs nothing and gives every contributor a local baseline. Frontier-model alternation halves the time-resolution on Opus and GPT-5 Preview individually — acceptable when drift on the frontier is a months-scale story, not a weeks-scale one.

What is not yet running: Gemini, Grok, DeepSeek, Qwen, Mistral, Llama-via-API, the embedding-centroid drift analysis, the productionized refusal classifier, the held-out validation runs, IPFS pinning, and the read-only public Postgres replica. All of these are scoped. Most are blocked on funding, not design.

## How it's built to be defensible

The accusations are easy to predict: *cherry-picking*, *biased corpus*, *misinterpreting legitimate safety improvements*, *bias in the choice of axes*. Transparency is the only defense that matters, so the design is aggressive about it:

- **Raw data is append-only.** Nothing is ever overwritten. Retention is forever.
- **Corpus changes are versioned transactions**, never in-place edits. Every prompt has provenance, an axis label, expected-dimension-of-drift, and historical context notes.
- **The corpus is split**: ~70% public, ~30% held-out. Drift is reported on both. If public drift diverges meaningfully from held-out drift, that gap is itself the story: evidence of benchmark-targeting.
- **No provider sees a report before publication.** Not for "factual review," not for "context," not for any reason.
- **No funding from LLM providers.** Ever. Funding sources are public and prominent at `/funding/`.
- **Reproducibility is a hard guarantee.** Anything on the dashboard reproduces from the published raw data within 5%. The methodology page documents the steps.
- **Refusal-rate changes are reported separately** for clearly-harmful prompts (often legitimate safety) and merely-contested prompts (often normative). The distinction is not collapsed.

Code is MIT. Corpus, raw data, and reports are CC-BY-SA 4.0. Lower the barrier for others to run their own instances, audit ours, or fork the methodology.

## The tier ladder

Meridian is volunteer-maintained and API-cost-dominated. Each tier above Level 0 unlocks a specific capability. Every level is already implemented in code or requires only minor config changes. The gate is funding.

| Level | Add'l/mo | What it unlocks |
|---|---:|---|
| 1 | +$7 | Haiku + GPT-4.1-mini every week. Two more per-provider data points; better silent-update coverage. |
| 2 | +$165 | Unalternate Opus + GPT-5; add Gemini 2.5 Pro. Weekly frontier granularity, three major providers. |
| 3 | +$470 | Expand corpus 30 → 75. ~10 prompts per axis, credible coverage. |
| 4 | +$1,000 | Full 150-prompt v1.0 corpus + durable S3/IPFS storage. Makes "retention forever" real. |
| 5 | +$2,100 | CLAUDE.md spec corpus (200–300 prompts) + trained refusal classifier + Postgres index for researchers. |

The full BUDGET.md in the repo shows the underlying cost model. Sponsorship is a single Buy Me a Coffee link: no Patreon, no GitHub Sponsors, no provider-adjacent corporate tier. If the record is useful to you, a coffee meaningfully extends how many weeks the project can keep running.

We never take funding from an LLM provider. The reason this rule is hard rather than soft is the same reason no provider gets a report preview: if there is even a perception that money or access shapes the analysis, the project's central artifact, *a citation-quality public record*, is worthless.

## What you can do today

- **Read the methodology** at [meridianaudit.org/methodology/](https://meridianaudit.org/methodology/). Not academic; written for journalists.
- **Run it locally**, no API keys needed:

  ```bash
  git clone https://github.com/digital-grease/meridian
  cd meridian
  uv sync
  ollama pull llama3.2:3b
  uv run python -m meridian.pipeline.cli run --yes
  ```

- **Propose a prompt** via the `Prompt proposal` template on GitHub Issues. Axis coverage is gappy at 30 prompts; well-argued additions move the project up the ladder.
- **Add a provider runner**: one adapter per provider, see `meridian/runners/README.md`.
- **Sponsor a coffee** if the record is useful to you. The button is on the homepage and on every report.

The goal of v0.1 is not to ship the final dashboard. The goal is to start the longitudinal record now, on a small but rigorous corpus, and grow it as funding and contributors arrive. Every week that passes with no record running is a week of drift that will never be reconstructable.
