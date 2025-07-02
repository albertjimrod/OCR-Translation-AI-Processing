

# 📸 **Bash Automation: OCR, Translation & AI Processing (Local Ollama)** 🤖📖

---

## 📌 **Project Overview**

This project provides a robust Bash automation script (`procesarAI.sh`) designed for capturing screenshots of digital documents (such as books or web content), converting these captures into structured text via OCR (`Tesseract`), translating and enhancing content through locally-hosted AI models (`Ollama`), and finally exporting results into professional-quality OpenDocument Text (`.odt`) files.

---

## 🛠️ **Technologies & Tools**

* **Bash / Shell Scripting**
* **Tesseract OCR**
* **Ollama (Local AI hosting)**
* **SSH Tunneling (Remote GPU)**
* **ImageMagick (Image optimization)**
* **LibreOffice (ODT export)**
* **Regex (Text optimization)**

---

## 🚀 **Workflow & Functionality Explained**

### 1. **Sequential Image Capture**

The script prompts for an initial numeric input to create sequentially-named image files (`image_001.png`, `image_002.png`, etc.). This facilitates straightforward tracking and debugging.

> **Why Sequential Numbers?**
> Sequential naming quickly identifies problematic images in case of OCR or processing errors.

### 2. **OCR Text Extraction (Tesseract)**

Captured images undergo pre-processing (brightness/contrast enhancements via ImageMagick) to boost OCR accuracy before extraction using `Tesseract`.

### 3. **Local AI Processing (Ollama)**

Extracted text is translated and enhanced using `Ollama`, a local AI-model host (like LLaMA, Mistral, Gemma). This avoids external APIs (such as ChatGPT), reducing costs and enhancing privacy.

### 4. **Remote GPU via SSH Tunneling (Optional)**

Leverage GPU resources on remote servers using SSH tunneling for improved performance without cloud-based fees.

```bash
ssh -L 11434:localhost:11434 user@remote-gpu-server
```

This connects your local Ollama instance to a remote GPU-accelerated environment.

### 5. **Automated Translation & Text Enhancement**

Text processed by Ollama undergoes simultaneous translation, grammar correction, summarization, and formatting.

### 6. **Final Output in ODT Format**

LibreOffice CLI converts processed text into professionally formatted `.odt` documents, suitable for editing or distribution.

---

## 📂 **Project Structure**

```
bash-automation-image-to-text/
├── images/                 # Captured images
├── output/                 # Final ODT files
├── scripts/
│   └── procesarAI.sh       # Automation script
└── README.md               # Documentation (this file)
```

---

## ⚠️ **Potential Challenges & Solutions**

* **OCR Errors:**
  *Solution:* Optimize images with ImageMagick before OCR.

* **Remote Connection Stability:**
  *Solution:* Maintain a stable network, implement reconnection scripts.

* **Resource Demand by AI Models:**
  *Solution:* GPU acceleration via SSH tunneling.

---

## 🧑‍💻 **Installation & Usage**

### **Step 1: Clone Repo**

```bash
git clone https://github.com/yourusername/bash-automation-image-to-text.git
cd bash-automation-image-to-text/scripts
```

### **Step 2: Install Dependencies**

```bash
sudo apt-get install tesseract-ocr imagemagick libreoffice
```

### **Step 3: Install & Configure Ollama**

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

Download AI Model (e.g. Mistral):

```bash
ollama pull mistral
```

### **Step 4: SSH Tunnel (Remote GPU)** *(Optional but Recommended)*

```bash
ssh -L 11434:localhost:11434 user@remote-gpu-server
```

### **Step 5: Execute Automation Script**

```bash
chmod +x procesarAI.sh
./procesarAI.sh
```

---

## 📌 **Detailed Explanation of `procesarAI.sh`**

This script automates the following steps:

* Prompt user input for starting image number.
* Capture screenshots of documents (from platforms such as Amazon Kindle or webpages).
* Pre-process images using ImageMagick (brightness/contrast adjustments).
* Perform OCR with Tesseract to extract text.
* Send text through local Ollama instance for translation and enhancement.
* Use Regex for final text cleanup.
* Generate structured `.odt` documents with LibreOffice CLI.

---

## 📄 **Full Example of `procesarAI.sh` (Code)**

> *(This is a simplified representative example; adapt according to your environment.)*

```bash
#!/bin/bash

# Starting number for sequential images
echo "Enter starting image number:"
read num

# Capture, OCR, AI Processing loop
while true; do
  filename=$(printf "image_%03d.png" $num)
  textfile=$(printf "text_%03d.txt" $num)
  odtfile=$(printf "doc_%03d.odt" $num)

  # Capture screenshot
  import "$filename"

  # Image optimization (optional)
  mogrify -brightness-contrast 10x15 "$filename"

  # OCR extraction
  tesseract "$filename" "${textfile%.txt}"

  # Text processing with Ollama AI
  curl -X POST http://localhost:11434/api/generate \
       -d '{"model":"mistral","prompt":"Translate and correct this text: '"$(<"$textfile")"'"}' \
       | jq -r '.response' > "processed_$textfile"

  # Final formatting with Regex (example placeholder)
  sed -i 's/[[:space:]]\+/ /g' "processed_$textfile"

  # Generate ODT document
  soffice --headless --convert-to odt "processed_$textfile" --outdir ../output

  echo "Processed and saved: $odtfile"
  
  num=$((num + 1))

  echo "Continue? (y/n)"
  read ans
  if [ "$ans" != "y" ]; then break; fi
done
```

---

## 🎯 **Use Cases & Potentials**

* **Book Digitization & Translation:** Convert scanned books into translated and formatted digital documents rapidly.
* **Automated Content Generation:** Instant summaries or translated insights from digital resources.
* **Research & Academic Applications:** Efficient digitization and translation of academic materials.

---

## 📃 **License**

MIT License © [Your Name](https://github.com/yourusername)

---

Este documento README.md está listo para copiar y pegar directamente en tu repositorio GitHub. Ajusta únicamente tu nombre de usuario y datos específicos según corresponda.

