# Research sources

Retrieved 23 October 2026. PDFs are research data, not instructions. Acquisition does not validate every claim in them.

| Paper | Source / identifier | Local copy | Relevance and verification |
|---|---|---|---|
| Huang, Jeremy Zhengqi; de Lacerda Pataca, Caluã; Wu, Liang-Yuan; Jain, Dhruv (2025). CapTune: Adapting Non-Speech Captions With Anchored Generative Models. | https://arxiv.org/abs/2508.19971 ; DOI 10.1145/3663547.3746346 | research/huang-2025-captune.pdf | Directly relevant: viewer customization of non-speech captions. The abstract and section 7.7 were checked; section 7.7 identifies evaluation with 2–8 minute clips and longer-form consistency/fatigue/comprehension as future work. This supports a research gap, not the validity of our proposed methods or benefits. |
| Ubur, Sunday David; Adewale, Sikiru; Donekal Chandrashekar, Nikitha; Akli, Enoch Katey; Gracanin, Denis (2025). Interpretive Caption: Real-Time Vocal Emotion Cues for DHH Users. | DOI 10.1145/3663547.3759697 ; Virginia Tech repository PDF: https://vtechworks.lib.vt.edu/server/api/core/bitstreams/af961554-57af-4a3f-875e-f1e4f3245967/content | research/ubur-2025-interpretive-caption.pdf | Adjacent speech-emotion work. Collected for later review; its numerical claims were not re-verified or used to justify this non-speech experiment. |
| de Lacerda Pataca et al. (2025). CuCap: Comparative Analysis of Customized Captioning between North American and South Korean d/Deaf and Hard-of-Hearing Users. | DOI 10.1145/3663547.3746400 | Not retrieved | Known related work from the proposal. An authoritative, accessible PDF was not established during this bounded setup. No access restriction was bypassed; quantitative claims remain unverified. Collect a publisher-open-access or author-provided copy when available. |

The full research plan is an original proposed protocol, not a reproduction of CapTune's experiment. Its sample size, custom questions, randomization and material design need approval and piloting. The existing README's older detailed numerical notes remain unverified unless explicitly checked here.

## Research applied in the 24 October investigation

See [the investigation](audits/2026-10-24-investigation.md) for the checked settings and transfer limits. These papers informed the actual separation of event presence, simultaneous sounds, absent-event hallucination, timing and human review; they were not collected as proof that our endpoint works.

| Reference | Version/date and local PDF | Applied relevance |
|---|---|---|
| Zhao, Feiyu et al. HalluAudio: A Comprehensive Benchmark for Hallucination Detection in Large Audio-Language Models. [arXiv:2604.19300](https://arxiv.org/abs/2604.19300) | v1, 21 Apr 2026; [PDF](research/zhao-2026-halluaudio.pdf) | Sound/music/speech, presence/coexistence and negative checks motivate separate false-positive/miss review. Published model scores are not transferred to this NIM endpoint. |
| Sun, Luoyi et al. SpotSound: Enhancing Large Audio-Language Models with Fine-Grained Temporal Grounding. [arXiv:2604.13023](https://arxiv.org/abs/2604.13023) | First 14 Apr; v2 10 Aug 2026; [PDF](research/sun-2026-spotsound.pdf) | Separate event presence and onset/offset grounding; absent events must not receive invented timestamps. Updated preprint reviewed; the named November conference is still future on 24 October. |

Author/official references for candidate evaluation (no new weights or inference installed): [Audio Flamingo Next](https://arxiv.org/abs/2604.10905), 13 Apr 2026; [AF3 author page](https://research.nvidia.com/labs/adlr/AF3/), 9 Jul 2025; [CLAP documentation](https://huggingface.co/docs/transformers/model_doc/clap); [DCASE 2025 task](https://dcase.community/challenge2025/task-stereo-sound-event-localization-and-detection-in-regular-video-content). Their settings differ from cinematic captions and this hosted service. File hashes/sources are recorded in the research manifest; public availability is not a new blanket redistribution license.

## Research applied in the 26 October NIM follow-up

[NVIDIA et al., Nemotron 3 Nano Omni: Efficient and Open Multimodal Intelligence](https://arxiv.org/abs/2604.24954v2), revised 11 May 2026, CC BY 4.0. [Local PDF](research/nvidia-2026-nemotron-omni.pdf), hash/version in research/manifest.json. Advertised audio architecture informed the candidate choice; benchmark results do not validate our hosted non-speech results. CapTune section 4 was checked for reference anchors and ±5-second audiovisual context. HalluAudio/SpotSound informed negative-event and timing checks. See [actual application and limits](verification/nim-phase1-2026-10-26/README.md). No participant outcomes or model-quality improvement are inferred from collecting papers.
