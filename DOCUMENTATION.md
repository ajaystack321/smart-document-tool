<!-- # Developer Documentation

## Architecture

The application has four primary processing layers.

### Image Processing

Pillow handles:

- JPEG conversion
- resizing
- image encoding
- compression

### Computer Vision

OpenCV handles:

- edge detection
- contours
- document detection
- perspective correction
- grayscale
- thresholding
- denoising
- contrast enhancement

### PDF

PyMuPDF handles:

- PDF generation
- PDF rendering
- page conversion

### UI

Streamlit handles:

- uploads
- controls
- previews
- downloads
- mobile browser interface

## Data lifecycle

Upload
→ memory
→ process
→ output
→ download

The MVP does not require a database.

## Performance

For low-RAM hosting:

- Resize images early where possible.
- Avoid loading unnecessary copies.
- Avoid large AI models.
- Avoid GPU dependencies.
- Limit upload size.
- Process files sequentially.

## Future modules

Possible additions:

- OCR
- PDF merge
- PDF split
- PDF rotate
- PDF reorder
- PDF password protection
- JPG/PNG conversion
- exact pixel resizing
- passport photo presets
- signature presets
- batch compression
- image background removal -->

# Developer Documentation

## 1. Architecture

The application is organized into four primary processing layers:

1. Image Processing
2. Computer Vision
3. PDF Processing
4. User Interface

---

## 2. Image Processing

Pillow is used for image-related operations.

### Responsibilities

- JPEG conversion
- Image resizing
- Image encoding
- Image quality control
- Image compression
- Maximum dimension control
- RGB/RGBA image handling
- Image enhancement
- Brightness adjustment
- Color tone processing
- Sharpening
- Skin tone sharpening
- Blur removal

### Compression

The photo compression module supports target file sizes from:

- 20 KB
- 70 KB
- 120 KB
- 170 KB
- 220 KB
- ...
- 970 KB

The target-size list is generated programmatically in 50 KB increments according to the application's configured range.

---

## 3. Computer Vision

OpenCV is used for document detection and image processing operations.

### Responsibilities

- Edge detection
- Contour detection
- Document boundary detection
- Automatic document cropping
- Perspective correction
- Grayscale conversion
- Thresholding
- Denoising
- Contrast enhancement
- Outline detection

### Document Detection

The application analyzes the uploaded image to identify the document boundary.

The detected corner points are ordered before applying geometric transformations.

### Auto Crop

Auto Crop detects the document area and crops the image to the detected region.

Auto Crop is an independent user-controlled option.

### Perspective Correction

Perspective Correction transforms an angled document into a rectangular view.

Perspective Correction is also an independent user-controlled option.

The user can therefore:

- Enable both
- Enable only Auto Crop
- Enable only Perspective Correction
- Disable both

---

## 4. Image Filters

The Scan Anything module provides multiple processing filters.

### Available Filters

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

Filters are applied after the selected document-processing operations.

---

## 5. PDF Processing

PyMuPDF is used for PDF-related operations.

### Image → PDF

The application can:

- Convert images to PDF
- Process multiple images
- Generate A4 PDFs
- Generate Original-size PDFs
- Control image quality

### PDF → Image

The application can:

- Render PDF pages as images
- Convert multiple PDF pages
- Use configurable DPI
- Generate downloadable image files
- Generate ZIP files for multiple pages

### PDF Tools

The application currently supports:

- PDF Merge
- PDF Compression
- PDF Split
- Delete PDF Pages
- Reorder PDF Pages
- Rotate PDF Pages

---

## 6. User Interface

Streamlit is used as the application interface.

### Responsibilities

- File uploads
- Feature selection
- Checkboxes
- Select boxes
- Image previews
- Before/After previews
- Processing controls
- Download buttons
- PDF downloads
- ZIP downloads
- Mobile browser interface

The UI is designed to keep document and image processing accessible through a web browser without requiring a desktop application.

---

## 7. Data Lifecycle

The application follows a simple in-memory processing model:

```text
Upload
   ↓
Memory
   ↓
Validation
   ↓
Processing
   ↓
Output Generation
   ↓
Download

The MVP does not require a database.

Uploaded files are processed during the active application session rather than being stored in a permanent database.

8. Processing Flow
Scan Anything
Upload Image
     ↓
Read Image
     ↓
Auto Crop (if enabled)
     ↓
Perspective Correction (if enabled)
     ↓
Selected Filter
     ↓
Before / After Preview
     ↓
JPG or PDF Output
     ↓
Download
Compress Photo
Upload Image
     ↓
Read Image
     ↓
Resize According to Maximum Dimension
     ↓
Iterative JPEG Compression
     ↓
Check Output Size
     ↓
Generate Compressed Image
     ↓
Download
Image → PDF
Upload Image(s)
     ↓
Read Images
     ↓
Resize / Page Layout
     ↓
Apply Quality Setting
     ↓
Generate PDF
     ↓
Download
PDF → Image
Upload PDF
     ↓
Open PDF
     ↓
Render Pages at Selected DPI
     ↓
Generate Images
     ↓
Single Image / ZIP
     ↓
Download
9. Performance

The application should remain lightweight and suitable for low-RAM hosting.

Recommended Practices
Resize large images early where possible.
Avoid unnecessary image copies.
Process files sequentially.
Avoid loading unnecessary files into memory.
Avoid large AI models unless required.
Avoid GPU dependencies.
Limit upload sizes where appropriate.
Use efficient image formats.
Release temporary objects when they are no longer required.
10. Dependencies

The main dependencies are:

Streamlit
Pillow
OpenCV
NumPy
PyMuPDF

Additional dependencies may be retained for future modules:

PyTesseract
Python-docx

All Python dependencies should be maintained in:

requirements.txt
11. Current Modules

The current application contains the following major modules:

Image → PDF
PDF → Image
Scan Anything
Compress Photo
PDF Tools
Scan Anything
Document Detection
├── Auto Crop
└── Perspective Correction

Filters
├── Document
├── Original
├── B&W
├── Gray
├── Light Enhancement
├── Outline
├── Color Tone
├── Brightness Tone
├── Blur Removal
├── Sharpen
├── Skin Tone Sharpen
└── Enhance
PDF Tools
PDF Tools
├── Merge
├── Compress
├── Split
├── Delete Pages
├── Reorder Pages
└── Rotate Pages
12. Security and Privacy Considerations

The application should avoid unnecessary permanent storage of uploaded documents and images.

Recommended practices:

Process uploaded files only when required.
Avoid logging sensitive document contents.
Avoid storing personal documents permanently.
Avoid exposing uploaded files through public paths.
Validate uploaded file types.
Apply reasonable upload-size limits.
Clean up temporary files when applicable.

Government forms and identity documents may contain sensitive personal information, so privacy should be considered when deploying the application publicly.

13. Deployment

The application can be deployed on Streamlit-compatible hosting.

Typical deployment structure:

GitHub Repository
       ↓
Streamlit Deployment
       ↓
app.py
       ↓
requirements.txt

When application code is updated:

git status
git add .
git commit -m "Update application"
git push origin main

If the deployment is connected to the GitHub repository, the deployment platform can detect the new commit and rebuild the application.

14. Testing Checklist

Before deployment, test the following:

Image → PDF
Single image
Multiple images
A4 size
Original size
Different quality settings
PDF → Image
Single-page PDF
Multi-page PDF
Different DPI settings
ZIP download
Scan Anything
Normal document
Angled document
Auto Crop enabled
Auto Crop disabled
Perspective Correction enabled
Perspective Correction disabled
Both enabled
Both disabled
Each available filter
Compress Photo
Small image
Large image
Different target sizes
Different maximum dimensions
Output file size
Downloaded image validity
PDF Tools
Merge
Compress
Split
Delete Pages
Reorder Pages
Rotate Pages
15. Future Modules

The following features are potential future additions:

OCR
PDF password protection
JPG/PNG conversion
Exact pixel resizing
Passport photo presets
Signature presets
Batch compression
Background removal
Government-form-specific presets
Advanced OCR-based document detection
Automatic document quality analysis
More image enhancement options
16. Development Guidelines

When adding a new feature:

Update app.py.
Test the feature locally.
Check existing features for regressions.
Update README.md if the feature is user-facing.
Update User_Manual.md if the feature changes the user workflow.
Update Developer_Documentation.md if the architecture or processing logic changes.
Update requirements.txt only when a new Python dependency is required.
Commit the changes to Git.
Push the changes to GitHub.
Verify the deployed Streamlit application.