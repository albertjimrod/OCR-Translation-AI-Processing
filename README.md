# OCR, Translation & AI Processing Pipeline

[![Bash](https://img.shields.io/badge/Bash-Automation-4EAA25?style=flat-square&logo=gnu-bash&logoColor=white)](https://www.gnu.org/software/bash/)
[![Tesseract](https://img.shields.io/badge/Tesseract-OCR-5A5A5A?style=flat-square&logo=google&logoColor=white)](https://github.com/tesseract-ocr/tesseract)
[![Ollama](https://img.shields.io/badge/Ollama-Local_AI-000000?style=flat-square)](https://ollama.ai/)

Bash automation for converting document images to translated text using OCR and local AI models.

---

## Features

- **OCR Extraction** - Tesseract-based text extraction from images
- **Image Preprocessing** - ImageMagick optimization for better OCR accuracy
- **Local AI Translation** - Ollama integration (no external APIs, privacy-first)
- **GPU Acceleration** - Optional SSH tunneling to remote GPU servers

---

## Workflow

```
Image → ImageMagick (preprocess) → Tesseract (OCR) → Ollama (translate/enhance) → Output
```

---

## Quick Start

```bash
# Clone
git clone https://github.com/albertjimrod/OCR-Translation-AI-Processing.git
cd OCR-Translation-AI-Processing/Systemantics

# Install dependencies
sudo apt-get install tesseract-ocr imagemagick

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral  # or any model

# Run
chmod +x procesarAI.sh
./procesarAI.sh
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Bash | Script automation |
| Tesseract | OCR engine |
| ImageMagick | Image preprocessing |
| Ollama | Local AI inference |

---

## Optional: Remote GPU via SSH

```bash
ssh -L 11434:localhost:11434 user@remote-gpu-server
```

Connect your local Ollama to a remote GPU for faster inference.

---

## Author

**Alberto Jiménez** - [datablogcafe.com](https://datablogcafe.com) | [GitHub](https://github.com/albertjimrod)

---

## License

MIT License
