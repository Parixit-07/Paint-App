# 🎨 Paint Application (Tkinter)

A feature-rich desktop paint application built using **Python Tkinter and PIL (Pillow)**.
This app provides a smooth drawing experience with multiple tools, shapes, colors, and undo/redo functionality.

---

## 🚀 Overview

This is not a basic paint clone. It includes:

* Multiple drawing tools (pen, brush, spray, eraser)
* Shape rendering with live preview
* Flood fill (bucket tool) without external dependencies
* Undo/Redo system
* Image saving using PIL

All drawing operations are mirrored to a **PIL image backend**, ensuring accurate rendering and export.

---

## ✨ Features

### 🖌 Drawing Tools

* Pen (smooth drawing)
* Brush (solid strokes)
* Spray tool (randomized particle effect)
* Eraser

### 📐 Shapes

* Line
* Rectangle
* Circle
* Triangle
* Diamond
* Live preview before final placement

### 🎨 Color System

* Predefined color palette
* Custom color picker
* Separate **pen color** and **fill color**

### 🪣 Fill Tool

* Flood fill using PIL (no Ghostscript)
* Threshold-based filling

### ↩️ Undo / Redo

* Full action-based undo/redo stack
* Supports:

  * Drawing strokes
  * Shapes
  * Fill operations

### 📏 Size Controls

Adjustable sliders for:

* Pen size
* Brush size
* Eraser size
* Spray size
* Spray density

### 💾 Save Support

* Export canvas as:

  * PNG
  * JPEG

### 🧠 Smart Backend

* Canvas drawing synced with **PIL image**
* Ensures:

  * Accurate saving
  * Reliable fill operations

---

## 🛠 Tech Stack

* Python 3
* Tkinter (GUI)
* PIL / Pillow (image processing)

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/paint-app.git
cd paint-app
```

### 2. Install dependencies

```bash
pip install pillow
```

### 3. Run the app

```bash
python main.py
```

---

## 🎮 Controls & Shortcuts

| Action | Shortcut   |
| ------ | ---------- |
| Undo   | Ctrl + Z   |
| Redo   | Ctrl + Y   |
| Draw   | Mouse Drag |
| Fill   | Click      |

---

## 📁 Project Structure

```bash
paint-app/
│
├── main.py        # Main application file
├── README.md
```

---

## ⚙️ Core Concepts Used

* Event-driven programming (Tkinter bindings)
* Canvas rendering
* PIL image manipulation
* Flood fill algorithm
* State management (undo/redo stacks)

---

## ⚠️ Limitations (Be Real About It)

* No layers support
* No zoom/pan system
* No pressure sensitivity (not tablet optimized)
* Performance may drop with very heavy spray usage

---

## 🚀 Possible Improvements

If you actually want to level this up:

* Add **layers system**
* Add **zoom + pan**
* Add **shape resizing/editing after creation**
* Add **export to SVG**
* Add **keyboard tool switching**
* Optimize spray performance

---

## 👨‍💻 Authors

Made by:

* Parixit
* Megh
* Vivek

---

## 🧠 Final Note

This project is a solid step beyond beginner-level Tkinter apps.

But don’t get comfortable —
real-world tools need:

* better architecture
* separation of concerns
* performance optimization

Treat this as a **foundation, not a finished product**.

---
