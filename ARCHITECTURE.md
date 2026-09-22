1. Architecture.md
# System Architecture

## 1. Overview

Smart Document & Image Toolkit is a lightweight Streamlit-based application for document scanning, image processing, PDF conversion, PDF manipulation, and photo compression.

The application follows a simple layered architecture:

```text
User Interface
      ↓
Input Validation
      ↓
Image / PDF Processing
      ↓
Output Generation
      ↓
Download

The application primarily uses:

Streamlit for the user interface
Pillow for image processing
OpenCV for computer vision
NumPy for numerical image operations
PyMuPDF for PDF processing


2. High-Level Architecture
                    User
                     │
                     ▼
              Streamlit UI
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    Image Processing       PDF Processing
          │                     │
          ▼                     ▼
       Pillow                PyMuPDF
          │                     │
          └──────────┬──────────┘
                     ▼
              Output Generation
                     │
                     ▼
                  Download

3. Application Modules

The application contains the following major modules:

Smart Document & Image Toolkit
│
├── Image → PDF
├── PDF → Image
├── Scan Anything
├── Compress Photo
└── PDF Tools
    ├── Merge
    ├── Compress
    ├── Split
    ├── Delete Pages
    ├── Reorder Pages
    └── Rotate Pages

4. Image Processing Layer

Pillow is responsible for common image operations.

Main responsibilities
Opening uploaded images
RGB/RGBA conversion
JPEG conversion
Image resizing
Image quality adjustment
Image encoding
Image compression
Brightness adjustment
Color processing
Sharpening
Blur removal
Image enhancement

5. Computer Vision Layer

OpenCV is used for document detection and advanced image processing.

Main responsibilities
Image conversion
Grayscale processing
Edge detection
Contour detection
Document boundary detection
Automatic document cropping
Perspective correction
Thresholding
Noise reduction
Contrast enhancement
Outline generation

6. Scan Anything Architecture

The Scan Anything module processes uploaded documents or photographs.

Upload Image
     ↓
Image Preparation
     ↓
Auto Crop
     │
     └── If enabled
     ↓
Perspective Correction
     │
     └── If enabled
     ↓
Selected Filter
     ↓
Before / After Preview
     ↓
JPG / PDF Output
     ↓
Download

Auto Crop and Perspective Correction are independent controls.

The user can:

Enable both
Enable only Auto Crop
Enable only Perspective Correction
Disable both

7. Scan Filters

The Scan Anything module supports:

Document
Original
B&W
Gray
Light Enhancement
Outline
Color Tone
Brightness Tone
Blur Removal
Sharpen
Skin Tone Sharpen
Enhance

8. PDF Processing Layer

PyMuPDF handles PDF operations.

Image → PDF
Images
  ↓
Image Processing
  ↓
Page Layout
  ↓
Quality Setting
  ↓
PDF Generation
  ↓
Download

Supported page modes:

A4
Original
PDF → Image
PDF Upload
    ↓
Open PDF
    ↓
Render Pages
    ↓
Selected DPI
    ↓
Image Generation
    ↓
Single Image / ZIP
    ↓
Download

PDF Tools

The application supports:

PDF Merge
PDF Compression
PDF Split
Delete Pages
Reorder Pages
Rotate Pages

9. Photo Compression Architecture

The Compress Photo module allows the user to select a target file size.

Target sizes are generated from:

20 KB → 70 KB → 120 KB → ... → 970 KB

The application also allows maximum image dimensions to be selected.

General processing flow:

Upload Photo
     ↓
Read Image
     ↓
Check Dimensions
     ↓
Resize if Required
     ↓
JPEG Compression
     ↓
Check Output Size
     ↓
Generate Output
     ↓
Download

10. User Interface Layer

Streamlit provides:

File upload controls
Select boxes
Checkboxes
Buttons
Image previews
Before/After previews
Download buttons
PDF downloads
ZIP downloads

The interface is browser-based and can be accessed from desktop or mobile browsers.

11. Data Storage Architecture

The application does not require a database for its core functionality.

Basic data lifecycle:

Upload
  ↓
Memory
  ↓
Processing
  ↓
Output
  ↓
Download

The application is designed around session-based processing rather than permanent document storage.

12. Performance Considerations

For low-RAM hosting:

Resize large images when appropriate.
Avoid unnecessary image copies.
Process files sequentially.
Avoid large AI models.
Avoid GPU dependencies.
Limit upload sizes where appropriate.
Use efficient image processing operations.
13. Technology Stack
Layer	Technology
Frontend / UI	Streamlit
Image Processing	Pillow
Computer Vision	OpenCV
Numerical Processing	NumPy
PDF Processing	PyMuPDF
Programming Language	Python

14. Future Architecture Extensions

Possible future modules include:

OCR
Exact pixel resizing
Passport photo presets
Signature presets
Batch compression
JPG/PNG conversion
Background removal
PDF password protection
Advanced document recognition