---
title: Projects
description: Open source tools from The Forge — security research, privacy, and the spaces between.
hide:
  - toc
---

# Projects

Things I've built. Some to prove a point, some because nobody else would.

---

<div class="grid cards" markdown>

-   :material-phone-voip:{ .lg .middle } **EVE — Encoded VoIP Exfil**

    ---

    VoIP as a covert data exfiltration channel. Encodes arbitrary files as mFSK audio inside legitimate SIP/RTP calls. From the network's perspective, it looks like a phone call.

    Built in Rust. Designed for red teams testing DLP assumptions.

    [:octicons-arrow-right-24: Read the write-up](/posts/tin-cans-and-strings/)
    [:octicons-mark-github-16: Source](https://github.com/digital-grease/EVE)

-   :material-incognito:{ .lg .middle } **Fauxx — Behavioral Data Poisoning**

    ---

    If you can't stop ad networks from collecting your data, make what they collect useless. An Android tool that generates synthetic browsing behavior to pollute advertising profiles.

    [:octicons-arrow-right-24: Read the write-up](/posts/fauxx-cant-stop-the-signal/)
    [:octicons-mark-github-16: Source](https://github.com/digital-grease/fauxx)

</div>
