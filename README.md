# Smart Document & Image Toolkit

A lightweight Streamlit application for document and image processing, scanning, PDF conversion, image enhancement, and photo compression.

## Features

### Image → PDF

- Convert one or multiple images into PDF
- A4 or Original page size
- Adjustable image quality

### PDF → Image

- Convert PDF pages into images
- Adjustable DPI
- Multi-page PDF support
- ZIP download for multiple converted images

### Scan Anything

- Upload documents or photos
- Automatic document crop
- Independent Auto Crop option
- Independent Perspective Correction option
- Before/After preview
- Download processed image as JPG or PDF

### Image Filters

- Document
- Original
- Black & White
- Grayscale
- Light Enhancement
- Outline
- Color Tone
- Brightness Tone
- Blur Removal
- Sharpen
- Skin Tone Sharpen
- Enhance

### Compress Photo

- Compress images according to target file size
- Target sizes from 20 KB to 1000 KB
- 50 KB step size
- Maximum dimension control
- Output file size verification

### PDF Tools

- Merge PDF
- Compress PDF
- Split PDF
- Delete PDF pages
- Reorder PDF pages
- Rotate PDF pages

### Government Form Preparation

Useful for preparing photos and documents according to online form requirements such as:

- Maximum file size
- Image width
- Image height
- File format
- Aspect ratio
- Background
- DPI

> Always check the official government website for the exact requirements before submitting a file.

## Technology

- Python
- Streamlit
- Pillow
- OpenCV
- NumPy
- PyMuPDF
- PyTesseract
- Python-docx

## Project Structure

```text
Smart-Document-Image-Toolkit/
│
├── app.py
├── requirements.txt
├── README.md
└── User_Manual.md