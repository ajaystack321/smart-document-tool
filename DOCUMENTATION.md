# Developer Documentation

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
- image background removal