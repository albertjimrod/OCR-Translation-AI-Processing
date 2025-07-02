#!/bin/bash

# Solicita un número al usuario
read -p "Introduce la imagen: " numero

# Sustituye el número en el comando y ejecuta las operaciones

convert "$numero.png" -resize 200% -type Grayscale -normalize "$numero.png"
tesseract "$numero.png" preprocess_text --dpi 300
export MAGICK_MEMORY_CACHE_LIMIT=256

echo "traducelo al español" | ollama run hf.co/mradermacher/Qwen2.5-7B-Instruct-abliterated-v2-GGUF:Q4_K_M "$(cat preprocess_text.txt)"
