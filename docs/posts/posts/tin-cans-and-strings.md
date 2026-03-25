---
date: 2026-03-24
slug: tin-cans-and-strings
authors:
  - digitalgrease
categories:
  - Digital
tags:
  - red-team
  - voip
  - covert-channel
  - signal-processing
  - rust
comments: true
---

# Tin Cans and Strings: VoIP as a Covert Channel

Most DLP deployments are looking at the wrong thing. They inspect email attachments, scan outbound HTTP, maybe flag USB writes. What they're not doing—what almost nobody is doing—is decoding the audio content of VoIP calls.

That's a meaningful gap. VoIP traffic is high-volume, expected on corporate networks, and encrypted at the transport layer in most modern deployments. Even when it isn't, the assumption is that it's just audio—phone calls. Nobody questions the phone calls.

[EVE](https://github.com/digital-grease/EVE) (Encoded VoIP Exfil) is a tool built to test that assumption. It transfers arbitrary files between two endpoints by encoding them as mFSK audio and streaming that audio as a legitimate SIP/RTP call. The receiving end decodes the audio back to bytes. From the network's perspective, it looks like a phone call.

<!-- more -->

## Why audio works

The underlying idea is old: acoustic modems. The difference is that this isn't generating audio for physical transmission, it's generating PCM samples that get packetized directly into RTP. The analog transmission artifacts that killed modem speeds over PSTN don't apply here. The audio path is digital end-to-end.

mFSK (multiple Frequency Shift Keying) encodes data as distinct audio tones. With M tones, each symbol carries log₂(M) bits. At 16 tones, a 50-symbol/second transmission carries 200 bits per second—25 bytes/second, roughly 1.5 KB/minute. Slow by any network standard, but fast enough to exfiltrate interesting things: SSH keys, configuration files, small archives.

The constraint this is working within is G.711 narrowband: 8 kHz sample rate, 300–3400 Hz usable frequency range. EVE's default configuration uses 400–1900 Hz for 16 tones at 100 Hz spacing—comfortably within the passband, with room to breathe on both ends.

One wrinkle: VoIP infrastructure often re-encodes audio. A call might pass through a PBX, a STUN server, a media gateway. μ-law compression (G.711) is lossy, but the loss is predictable—it's 8-bit companding with a well-defined table. Tone detection using Goertzel filters is robust to this; leaving us with frequency-domain analysis, not amplitude reconstruction.

## The pipeline

EVE's sender pipeline:

```
File → Packetizer → mFSK Encoder → μ-law encode → RTP → UDP
```

The packetizer wraps file data in frames with a 13-byte header: 2-byte magic, 4-byte sequence number, 1-byte flags, 2-byte payload length, CRC-32 trailer. The first frame is SYN—it carries filename and total size as JSON in the payload. The last frame sets FIN. Everything between has incrementing sequence numbers so the receiver can detect gaps and reorder.

The mFSK encoder converts frame bytes to PCM samples. Each symbol is a sine wave at the corresponding tone frequency, held for `sample_rate / symbol_rate` samples (160 samples at default settings). Symbol transitions get a 2ms raised-cosine ramp to reduce spectral splatter—without it, abrupt transitions generate harmonics that can confuse the decoder.

Before the data symbols, the encoder prepends a synchronization preamble: a chirp sweeping all tones low-to-high then high-to-low. The decoder uses a matched filter (cross-correlation against the known chirp) to find the exact sample offset where data begins. RTP delivery timing is not precise, and finding where the data starts is the first thing that can go wrong.

On receive, the decoder segments audio into symbol-length windows and runs a Goertzel filter at each of the M tone frequencies. Goertzel is a single-frequency DFT—cheaper than a full FFT and trivially parameterized to your tone set. The bin with highest energy wins. SNR per symbol is logged in verbose mode.

The VoIP layer is minimal SIP: INVITE, 200 OK, ACK, BYE. SDP negotiation exchanges RTP ports. The sender times RTP packets at 20ms intervals (160 samples per packet at 8 kHz) using a tokio interval timer to maintain correct pacing. The receiver runs a dejitter buffer—by default 60ms deep—to absorb delivery variance before feeding audio to the decoder.

## The ARQ layer

Raw mFSK over a real network loses packets. A dropped RTP packet means a hole in the audio stream, which means corrupted symbols, which means garbage bytes in that frame, which the CRC-32 check will catch. But "caught the error" is not the same as "recovered the data."

EVE's ARQ (Automatic Repeat reQuest) layer runs post-transfer over the reverse RTP channel—the same channel the receiver is already using for the call. After the sender sends FIN, the receiver checks its depacketizer for missing sequence numbers and sends NACKs. The sender retransmits those frames. This repeats until the receiver has everything and sends an explicit ACK, or until a configurable retry limit.

The implementation detail that made this clean in Rust: `UdpSocket` needs to be shared between the main ARQ coordinator and the receive loop. Wrapping it in `Arc<UdpSocket>` lets both hold references without a mutex around every operation—UDP sends and receives are independent operations.

## Building this in Rust

The codec is CPU-bound: sine generation, cross-correlation, Goertzel evaluation at every symbol. The network layer is I/O-bound. Mixing those in a single async task produces the worst of both worlds—long codec operations block the tokio thread, starving the I/O polling loop.

`tokio::task::spawn_blocking` handles the encoding and decoding work, pushing CPU-heavy operations onto a dedicated thread pool and keeping the async executor free for packet I/O. The bridge between them is an `mpsc` channel: the blocking task produces decoded frames; the async task consumes them.

Error handling uses `thiserror` throughout. Each module has its own error enum. Adding the ARQ layer didn't touch error types in unrelated modules—the transport layer doesn't need to know why a frame failed to decode.

## The numbers

| Tones | Bits/symbol | Raw bitrate | Effective (after framing overhead) |
|-------|-------------|-------------|--------------------------------------|
| 2     | 1           | 50 bps      | ~40 bps                              |
| 4     | 2           | 100 bps     | ~80 bps                              |
| 8     | 3           | 150 bps     | ~120 bps                             |
| 16    | 4           | 200 bps     | ~160 bps                             |
| 32    | 5           | 250 bps     | ~200 bps                             |

These are at the default 50 symbols/second. Increasing symbol rate improves throughput linearly but reduces robustness—shorter symbol windows mean less energy for the Goertzel filters to work with, which hurts SNR at the decoder. In practice, 16 tones at 50 sym/s is a reasonable default: ~1.5 KB/min under good conditions, degrades gracefully under packet loss.

Transcoding is the real reliability concern. If the call path recompresses audio with aggressive noise reduction or voice activity detection, tones can be attenuated or stripped entirely. EVE's frequency range sits in the clearest part of the G.711 passband, but there's no guarantee a particular PBX won't treat the signal as noise. Testing against the specific target infrastructure is not optional.

## What defenders should look for

VoIP traffic warrants the same inspection scrutiny as web or email traffic.

Calls that are unusually long relative to their apparent content, or that originate from endpoints not normally associated with voice, are worth a second look. Frequency analysis of captured RTP payloads can identify tonal patterns inconsistent with speech—speech has formants and prosody; mFSK has fixed-frequency sustained tones. Behavioral detection (call duration anomalies, off-hours calling, unusual destination IPs) is often more tractable than signal analysis at scale.

EVE was built for authorized red team engagements—to demonstrate that this class of channel exists and to give defenders something concrete to test against. The gap it exploits isn't obscure. It's just underexamined.
