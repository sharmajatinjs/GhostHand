# 👻 GhostHand — Real-time Hand Gesture Laptop Controller

Control your laptop with hand gestures via webcam. Built for **manhwa reading** (AsuraScans, MangaDex, etc.) and general desktop use. Runs at **25–30 FPS** on an RTX 3050 with zero ML training — pure MediaPipe + NumPy math.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange)
![Platform](https://img.shields.io/badge/Windows-11-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Mode | Gesture | Action |
|------|---------|--------|
| **Manhwa** | ✌️ Two fingers swipe right | Next page (→) |
| **Manhwa** | ✌️ Two fingers swipe left | Previous page (←) |
| **Manhwa** | 🖐️ Open hand move up/down | Scroll page |
| **Manhwa** | ☝️ Index finger point + hold | Move mouse to click "Next Chapter" |
| **Desktop** | 🤏 Pinch (thumb + index) | Left click |
| **Desktop** | 🖐️ Open hand move up/down | Scroll up/down |
| **Both** | ✊ Fist | **Pause all input** |
| **Both** | ✌️ Peace sign held 1s | **Toggle mode** (overlay shows current) |

---

## 🚀 Quick Start

```powershell
git clone https://github.com/yourname/GhostHand.git
cd GhostHand
pip install -r requirements.txt
python main.py
