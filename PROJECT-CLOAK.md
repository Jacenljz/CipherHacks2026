# Cloak — Disappear From AI, Live On Stage

> **CipherHacks 2026** · Theme: Cyber Security · Build window: 36–48h
> Working name: **Cloak** (alternatives: *Vanish*, *BlindSpot*, *Ghost*)

## One-liner
Hold up a printed patch and **disappear — live — from an AI security camera**. We turn the "invisible to AI" sci-fi trope into a real, on-stage demo, and show exactly *why* modern computer-vision security can be fooled.

## The hook (the problem)
AI cameras now watch streets, stores, borders, and campuses. Object detectors like **YOLO** decide, in real time, *"is there a person here?"* But these models can be defeated by **adversarial examples** — carefully crafted patterns that exploit how a neural network "sees." Cloak makes that threat **physical and visceral**: a printed patch that erases you from the camera's eyes. If AI vision can be fooled by a piece of paper, every system that relies on it needs to know.

## What we're building
1. **A live detection pipeline.** Webcam → YOLO → bounding boxes drawn on screen in real time. *"This is what an AI security camera sees."*
2. **An adversarial patch.** A pattern optimized so that, when it's in frame, the detector's "person" confidence drops below its threshold → no box → **you're invisible**.
3. **An explanation layer.** A side panel showing the "person" confidence score collapse when the patch appears — proving it's a targeted attack on the model's math, not a camera trick.

## The demo (the 2 minutes that win)
1. Webcam on the audience: **everyone gets boxed** as "person" in real time. *"This is what an AI security camera sees."*
2. You raise the patch → **your box vanishes**; everyone else stays boxed. *"To the AI, I no longer exist."*
3. Walk around — it keeps tracking others, never you.
4. **Hand the patch to a peer** → they vanish too. (People vote for what they touched.)
5. Show the side panel: the "person" confidence drops to ~0 when the patch is in frame. *"This isn't magic — it's a precise attack on how the model thinks."*

## Why this wins (scoring: 60% judges + 40% peers)
- **Peer vote (40%) — the single biggest jaw-drop.** "He disappeared from the AI" is graspable in 1 second, and peers can try it themselves. Highest peak peer-wow of any idea on our list.
- **Judge vote (60%) — real adversarial ML.** A live, physical-world attack (cf. Thys et al., 2019) on a serious 2026 problem: surveillance and autonomous-system safety. To push novelty beyond "adapted a known repo," we add a clear contribution — robustness across conditions, a wearable design, and/or the live explanation layer.
- **On-theme.** Computer-vision / AI security is core cyber security.

## How it works (high level — no code)
- A pretrained object detector (YOLO) outputs how confident it is that each region contains a person.
- We **don't change the model.** We optimize a *patch image* so that, wherever it appears, it pushes the "person" confidence **below the detection threshold**.
- We train the patch against many images under many simulated conditions (angle, lighting, scale) so it survives the real world, and constrain it to be **printable**.
- Print it, hold it up, and the live camera fails to detect you.

## Tech stack
- **Core:** Python + PyTorch + Ultralytics **YOLO**.
- **Patch training:** adapted from the open-source *adversarial-yolo* work (Thys et al.), with strong augmentation (Expectation over Transformation) for robustness.
- **Live demo:** OpenCV (webcam → detection → overlay) + a simple UI with the confidence panel.
- **Compute:** a GPU (Colab / Kaggle / cloud) to train the patch; the live demo runs on a laptop.
- **Physical:** a color printer + matte paper for the patch.

## 48-hour plan
| Phase | Focus |
|---|---|
| 0–4h | Lock scope, stand up the YOLO live pipeline, get the patch-training repo running |
| 4–12h | Live webcam detection UI ‖ first patch-training run on GPU |
| 12–24h | Iterate the patch with augmentation (robustness); test printed versions under different lighting; first working "disappear" |
| 24–36h | Harden robustness, polish UI + confidence panel, build the **digital fallback** mode |
| 36–44h | Print + test the final patch, lock the demo environment (camera + lighting), rehearse |
| 44–48h | Rehearse the demo 3×, build a 1-page slide, prep Q&A |

## Suggested roles
- **ML:** patch optimization + training (the critical path).
- **Vision / App:** live YOLO pipeline + UI + confidence panel + digital fallback.
- **Demo / Logistics:** printing, lighting + camera setup, rehearsal, slides.

*(Scale up/down by team size.)*

## Risks & mitigations (read this carefully)
- **Live robustness is the #1 risk.** The patch is sensitive to lighting, angle, distance, and print-color fidelity; on an unfamiliar demo floor it may flicker or fail — and a failed live demo hurts *both* the judge and peer scores. **Mitigations:** train with strong augmentation; control the demo environment (known camera + good lighting + practiced distance); **always** carry a recorded video backup **and** a software "digital patch" mode that is 100% reliable.
- **Needs a GPU, and most of the 48h can go into chasing robustness.** *Mitigation:* timebox patch quality — a "good-enough physical patch + flawless digital fallback" still demos great.
- **Novelty cap.** Adapting a known repo can read as "not original." *Mitigation:* add a clear contribution — robustness across conditions, a wearable/fashion version, a multi-model attack, or the explanation layer.
- **Ethics framing.** Present it as a **defensive wake-up call** — why AI surveillance and safety systems need adversarial robustness — not a tool for evading real-world security.

## Alternative considered: "Mirage"
A live 3D globe of *real* attackers hitting our honeypot, where everything they steal is **Honey-Encrypted fake data** they can't tell from the real thing. Lower peak "wow," but a **much higher floor**: the attack data is guaranteed, and the payoff is scripted + interactive (it doesn't depend on live conditions). It's also a more original fusion and fits the *CipherHacks* (encryption) theme better. **Choose Mirage** if demo reliability is the priority; **choose Cloak** if we have a strong ML member, a GPU, and time to harden it — and want the highest possible "wow" moment.

## Idea pool (for reference)
- **GhostText** — hide ciphertext inside natural, AI-written text (LLM steganography).
- **TrojanSign** — a small sticker that flips a traffic-sign classifier (STOP → Speed-80).
- **AirGap** — exfiltrate data from an offline computer (screen brightness / acoustics).
- **TrafficGhost** — fingerprint what a person is watching over encrypted traffic.
- **DolphinCmd** — inaudible voice commands to a phone / assistant.
- **Deniable** — deniable encryption: a decoy password reveals fake data; the real data's existence can't be proven.
