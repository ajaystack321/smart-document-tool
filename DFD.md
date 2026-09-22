---

# 3. `DFD.md`

```markdown
# Data Flow Diagram (DFD)

## 1. Overview

The Smart Document & Image Toolkit processes user-uploaded images and PDF files through different processing modules.

The application primarily follows an in-memory data flow.

```text
User
  ↓
Upload File
  ↓
Streamlit Application
  ↓
Processing Module
  ↓
Processed Output
  ↓
User Download
2. Context-Level DFD
                  ┌──────────────────┐
                  │       USER       │
                  └────────┬─────────┘
                           │
                    Upload File
                           │
                           ▼
              ┌─────────────────────────┐
              │ Smart Document & Image  │
              │        Toolkit          │
              └────────────┬────────────┘
                           │
                     Processed File
                           │
                           ▼
                  ┌──────────────────┐
                  │       USER       │
                  └──────────────────┘
3. Level 1 DFD
                         USER
                           │
                           │ Upload
                           ▼
                  ┌─────────────────┐
                  │  Streamlit UI   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ File Validation │
                  └────────┬────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        Image → PDF   Scan Anything  Compress Photo
              │            │            │
              │            │            │
              ▼            ▼            ▼
         PDF Tools     OpenCV/Pillow  Pillow
              │            │            │
              └────────────┼────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Output Creation │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Download Output │
                  └────────┬────────┘
                           │
                           ▼
                         USER
4. Image → PDF Data Flow
User
 ↓
Upload Image(s)
 ↓
Streamlit
 ↓
Pillow
 ↓
Page Size / Quality
 ↓
PyMuPDF
 ↓
PDF Generation
 ↓
PDF Output
 ↓
Download
5. PDF → Image Data Flow
User
 ↓
Upload PDF
 ↓
Streamlit
 ↓
PyMuPDF
 ↓
Select DPI
 ↓
Render PDF Pages
 ↓
Image Output
 ↓
Single Image / ZIP
 ↓
Download
6. Scan Anything Data Flow
User
 ↓
Upload Document / Photo
 ↓
Streamlit
 ↓
Image Preparation
 ↓
Auto Crop
 │
 ├── Enabled → Document Detection
 │
 └── Disabled → Continue
 ↓
Perspective Correction
 │
 ├── Enabled → Perspective Transformation
 │
 └── Disabled → Continue
 ↓
Selected Filter
 ↓
Before / After Preview
 ↓
JPG / PDF Output
 ↓
Download
7. Compress Photo Data Flow
User
 ↓
Upload Photo
 ↓
Streamlit
 ↓
Read Image
 ↓
Maximum Dimension
 ↓
Resize if Required
 ↓
JPEG Compression
 ↓
Target KB Check
 ↓
Compressed Output
 ↓
Download
8. PDF Tools Data Flow
User
 ↓
Upload PDF
 ↓
Streamlit
 ↓
PyMuPDF
 ↓
Select Operation
 │
 ├── Merge
 ├── Compress
 ├── Split
 ├── Delete Pages
 ├── Reorder Pages
 └── Rotate Pages
 ↓
Processed PDF
 ↓
Download
9. Data Processing Components
Data	Input	Processing	Output
Image	JPG/PNG	Pillow/OpenCV	Processed Image
Document Photo	JPG/PNG	OpenCV/Pillow	Scanned Image
PDF	PDF	PyMuPDF	Images/PDF
Multiple Images	JPG/PNG	Pillow/PyMuPDF	PDF
Photo	JPG/PNG	Pillow	Compressed JPG
PDF Pages	PDF	PyMuPDF	Modified PDF
10. Data Storage

The application does not require a permanent database for the current processing workflow.

User Upload
     ↓
Application Memory
     ↓
Processing
     ↓
Output
     ↓
User Download

The core workflow does not depend on persistent database storage.

11. External Data Flow

The application does not require external APIs for its core image and PDF processing functions.

Main processing occurs locally within the application runtime using:

Pillow
OpenCV
NumPy
PyMuPDF
12. Security and Privacy Flow

Sensitive files should follow this lifecycle:

User Upload
     ↓
Temporary/In-Memory Processing
     ↓
Transformation
     ↓
Output
     ↓
User Download

The application should avoid unnecessary permanent storage of uploaded documents.

Users should verify the privacy and storage configuration of the hosting environment before processing sensitive documents.

13. Overall Data Flow
                         ┌─────────────┐
                         │    USER     │
                         └──────┬──────┘
                                │
                                ▼
                       ┌────────────────┐
                       │  File Upload   │
                       └───────┬────────┘
                               │
                               ▼
                       ┌────────────────┐
                       │ Streamlit UI   │
                       └───────┬────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
          Image Processing  CV Processing  PDF Processing
                │              │              │
                └──────────────┼──────────────┘
                               │
                               ▼
                       ┌────────────────┐
                       │ Output Creation│
                       └───────┬────────┘
                               │
                               ▼
                       ┌────────────────┐
                       │    Download    │
                       └───────┬────────┘
                               │
                               ▼
                         ┌─────────────┐
                         │    USER     │
                         └─────────────┘

