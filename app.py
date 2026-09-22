# import io
# import zipfile

# import cv2
# import numpy as np
# import streamlit as st
# from PIL import Image, ImageEnhance
# import pymupdf


# # =========================================================
# # PAGE CONFIG
# # =========================================================

# st.set_page_config(
#     page_title="Smart Document & Image Toolkit",
#     page_icon="📄",
#     layout="centered",
#     initial_sidebar_state="auto",
# )


# # =========================================================
# # MOBILE / RESPONSIVE UI
# # =========================================================

# st.markdown(
#     """
#     <style>

#     .block-container {
#         padding-top: 1.2rem;
#         padding-bottom: 2rem;
#         padding-left: 1rem;
#         padding-right: 1rem;
#         max-width: 900px;
#     }

#     h1 {
#         font-size: 2rem !important;
#         line-height: 1.2 !important;
#         margin-bottom: 0.3rem !important;
#     }

#     h2 {
#         font-size: 1.45rem !important;
#     }

#     h3 {
#         font-size: 1.15rem !important;
#     }

#     .stButton > button,
#     .stDownloadButton > button {
#         width: 100%;
#         min-height: 3rem;
#         border-radius: 10px;
#         font-size: 1rem;
#         font-weight: 600;
#     }

#     [data-testid="stFileUploader"] {
#         width: 100%;
#     }

#     [data-testid="stFileUploaderDropzone"] {
#         min-height: 120px;
#         border-radius: 12px;
#     }

#     [data-testid="stSelectbox"],
#     [data-testid="stMultiSelect"],
#     [data-testid="stSlider"],
#     [data-testid="stSelectSlider"],
#     [data-testid="stCheckbox"],
#     [data-testid="stRadio"] {
#         margin-bottom: 0.6rem;
#     }

#     [data-testid="stImage"] img {
#         border-radius: 10px;
#     }

#     [data-testid="stSidebar"] {
#         min-width: 240px;
#     }

#     .pdf-info-box {
#         padding: 0.8rem;
#         border-radius: 10px;
#         border: 1px solid rgba(128, 128, 128, 0.25);
#         margin-bottom: 1rem;
#     }

#     @media (max-width: 640px) {

#         .block-container {
#             padding-top: 0.8rem;
#             padding-left: 0.75rem;
#             padding-right: 0.75rem;
#             padding-bottom: 1.5rem;
#         }

#         h1 {
#             font-size: 1.55rem !important;
#         }

#         h2 {
#             font-size: 1.3rem !important;
#         }

#         h3 {
#             font-size: 1.05rem !important;
#         }

#         p {
#             font-size: 0.95rem;
#         }

#         .stButton > button,
#         .stDownloadButton > button {
#             min-height: 3.2rem;
#             font-size: 1rem;
#         }

#         [data-testid="stFileUploaderDropzone"] {
#             min-height: 110px;
#         }

#         input,
#         select,
#         textarea {
#             font-size: 16px !important;
#         }
#     }

#     </style>
#     """,
#     unsafe_allow_html=True,
# )


# # =========================================================
# # IMAGE HELPERS
# # =========================================================

# def bytes_to_image(data):
#     return Image.open(
#         io.BytesIO(data)
#     ).convert("RGB")


# def image_to_jpeg(image, quality=90):
#     buffer = io.BytesIO()

#     image.convert("RGB").save(
#         buffer,
#         format="JPEG",
#         quality=int(quality),
#         optimize=True,
#     )

#     return buffer.getvalue()


# def resize_max(image, max_dimension):

#     width, height = image.size

#     largest = max(width, height)

#     if largest <= max_dimension:
#         return image

#     ratio = max_dimension / largest

#     new_size = (
#         int(width * ratio),
#         int(height * ratio),
#     )

#     return image.resize(
#         new_size,
#         Image.Resampling.LANCZOS,
#     )


# # =========================================================
# # OPENCV CONVERSION
# # =========================================================

# def pil_to_cv(image):

#     return cv2.cvtColor(
#         np.array(image),
#         cv2.COLOR_RGB2BGR,
#     )


# def cv_to_pil(image):

#     return Image.fromarray(
#         cv2.cvtColor(
#             image,
#             cv2.COLOR_BGR2RGB,
#         )
#     )


# # =========================================================
# # AUTO CROP
# # =========================================================

# def auto_crop(image):

#     original = pil_to_cv(image)

#     height, width = original.shape[:2]

#     scale = 1

#     if max(height, width) > 1200:

#         scale = 1200 / max(height, width)

#         small = cv2.resize(
#             original,
#             (
#                 int(width * scale),
#                 int(height * scale),
#             ),
#         )

#     else:

#         small = original.copy()

#     gray = cv2.cvtColor(
#         small,
#         cv2.COLOR_BGR2GRAY,
#     )

#     blur = cv2.GaussianBlur(
#         gray,
#         (5, 5),
#         0,
#     )

#     edges = cv2.Canny(
#         blur,
#         50,
#         150,
#     )

#     contours, _ = cv2.findContours(
#         edges,
#         cv2.RETR_EXTERNAL,
#         cv2.CHAIN_APPROX_SIMPLE,
#     )

#     contours = sorted(
#         contours,
#         key=cv2.contourArea,
#         reverse=True,
#     )

#     document = None

#     image_area = (
#         small.shape[0] *
#         small.shape[1]
#     )

#     for contour in contours[:20]:

#         perimeter = cv2.arcLength(
#             contour,
#             True,
#         )

#         approx = cv2.approxPolyDP(
#             contour,
#             0.02 * perimeter,
#             True,
#         )

#         area = cv2.contourArea(
#             contour
#         )

#         if (
#             len(approx) == 4
#             and area > image_area * 0.15
#         ):

#             document = approx.reshape(
#                 4,
#                 2,
#             )

#             break

#     if document is None:
#         return image

#     document = document / scale

#     result = np.zeros(
#         (4, 2),
#         dtype=np.float32,
#     )

#     sums = document.sum(axis=1)

#     differences = np.diff(
#         document,
#         axis=1,
#     ).reshape(-1)

#     result[0] = document[
#         np.argmin(sums)
#     ]

#     result[2] = document[
#         np.argmax(sums)
#     ]

#     result[1] = document[
#         np.argmin(differences)
#     ]

#     result[3] = document[
#         np.argmax(differences)
#     ]

#     top_left = result[0]
#     top_right = result[1]
#     bottom_right = result[2]
#     bottom_left = result[3]

#     width1 = np.linalg.norm(
#         bottom_right - bottom_left
#     )

#     width2 = np.linalg.norm(
#         top_right - top_left
#     )

#     height1 = np.linalg.norm(
#         top_right - bottom_right
#     )

#     height2 = np.linalg.norm(
#         top_left - bottom_left
#     )

#     max_width = int(
#         max(width1, width2)
#     )

#     max_height = int(
#         max(height1, height2)
#     )

#     if max_width < 10 or max_height < 10:
#         return image

#     destination = np.array(
#         [
#             [0, 0],
#             [max_width - 1, 0],
#             [max_width - 1, max_height - 1],
#             [0, max_height - 1],
#         ],
#         dtype=np.float32,
#     )

#     matrix = cv2.getPerspectiveTransform(
#         result,
#         destination,
#     )

#     corrected = cv2.warpPerspective(
#         original,
#         matrix,
#         (
#             max_width,
#             max_height,
#         ),
#     )

#     return cv_to_pil(corrected)


# # =========================================================
# # SCAN FILTERS
# # =========================================================

# def apply_filter(
#     image,
#     filter_name,
#     strength=50,
# ):

#     cv = pil_to_cv(image)

#     gray = cv2.cvtColor(
#         cv,
#         cv2.COLOR_BGR2GRAY,
#     )

#     if filter_name == "Original":
#         return image

#     if filter_name == "Gray":

#         return Image.fromarray(
#             gray
#         ).convert("RGB")

#     if filter_name == "B&W":

#         blurred = cv2.GaussianBlur(
#             gray,
#             (3, 3),
#             0,
#         )

#         _, result = cv2.threshold(
#             blurred,
#             0,
#             255,
#             cv2.THRESH_BINARY
#             + cv2.THRESH_OTSU,
#         )

#         return Image.fromarray(
#             result
#         ).convert("RGB")

#     if filter_name == "Document":

#         denoised = cv2.fastNlMeansDenoising(
#             gray,
#             None,
#             10,
#             7,
#             21,
#         )

#         clahe = cv2.createCLAHE(
#             clipLimit=2.0,
#             tileGridSize=(8, 8),
#         )

#         contrast = clahe.apply(
#             denoised
#         )

#         result = cv2.adaptiveThreshold(
#             contrast,
#             255,
#             cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#             cv2.THRESH_BINARY,
#             31,
#             11,
#         )

#         return Image.fromarray(
#             result
#         ).convert("RGB")

#     if filter_name == "Enhance":

#         result = ImageEnhance.Contrast(
#             image
#         ).enhance(
#             1 + strength / 100
#         )

#         result = ImageEnhance.Sharpness(
#             result
#         ).enhance(
#             1 + strength / 100
#         )

#         return result

#     return image


# # =========================================================
# # IMAGE TO PDF
# # =========================================================

# def images_to_pdf(
#     images,
#     page_size="A4",
#     quality=85,
# ):

#     pdf = pymupdf.open()

#     for image in images:

#         image = image.convert(
#             "RGB"
#         )

#         width, height = image.size

#         if page_size == "A4":

#             page_width = 595
#             page_height = 842

#             margin = 20

#             scale = min(
#                 (page_width - 2 * margin)
#                 / width,

#                 (page_height - 2 * margin)
#                 / height,
#             )

#             display_width = width * scale
#             display_height = height * scale

#             rect = pymupdf.Rect(
#                 (page_width - display_width) / 2,
#                 (page_height - display_height) / 2,
#                 (page_width + display_width) / 2,
#                 (page_height + display_height) / 2,
#             )

#             page = pdf.new_page(
#                 width=page_width,
#                 height=page_height,
#             )

#         else:

#             rect = pymupdf.Rect(
#                 0,
#                 0,
#                 width * 72 / 96,
#                 height * 72 / 96,
#             )

#             page = pdf.new_page(
#                 width=rect.width,
#                 height=rect.height,
#             )

#         image_data = image_to_jpeg(
#             image,
#             quality,
#         )

#         page.insert_image(
#             rect,
#             stream=image_data,
#         )

#     result = pdf.tobytes(
#         garbage=4,
#         deflate=True,
#     )

#     pdf.close()

#     return result


# # =========================================================
# # PDF TO IMAGE
# # =========================================================

# def pdf_to_images(
#     pdf_bytes,
#     dpi=150,
# ):

#     document = pymupdf.open(
#         stream=pdf_bytes,
#         filetype="pdf",
#     )

#     results = []

#     for index, page in enumerate(
#         document
#     ):

#         pixmap = page.get_pixmap(
#             dpi=dpi,
#             alpha=False,
#         )

#         image_data = pixmap.tobytes(
#             "png"
#         )

#         results.append(
#             (
#                 f"page_{index + 1}.png",
#                 image_data,
#             )
#         )

#     document.close()

#     return results


# # =========================================================
# # ZIP
# # =========================================================

# def create_zip(files):

#     buffer = io.BytesIO()

#     with zipfile.ZipFile(
#         buffer,
#         "w",
#         zipfile.ZIP_DEFLATED,
#     ) as archive:

#         for filename, data in files:

#             archive.writestr(
#                 filename,
#                 data,
#             )

#     return buffer.getvalue()


# # =========================================================
# # PHOTO COMPRESSION
# # =========================================================

# def compress_photo(
#     image,
#     target_kb,
#     max_dimension,
# ):

#     image = resize_max(
#         image,
#         max_dimension,
#     )

#     low = 20
#     high = 95

#     best = None

#     for _ in range(10):

#         quality = (
#             low + high
#         ) // 2

#         data = image_to_jpeg(
#             image,
#             quality,
#         )

#         if len(data) <= target_kb * 1024:

#             best = data
#             low = quality + 1

#         else:

#             high = quality - 1

#     if best is not None:
#         return best

#     current = image

#     for _ in range(8):

#         current = resize_max(
#             current,
#             int(
#                 max(current.size)
#                 * 0.85
#             ),
#         )

#         data = image_to_jpeg(
#             current,
#             55,
#         )

#         if len(data) <= target_kb * 1024:
#             return data

#     return image_to_jpeg(
#         current,
#         35,
#     )


# # =========================================================
# # PDF HELPERS — BATCH 2
# # =========================================================

# def open_pdf(pdf_bytes):
#     return pymupdf.open(
#         stream=pdf_bytes,
#         filetype="pdf",
#     )


# def pdf_page_count(pdf_bytes):

#     document = open_pdf(pdf_bytes)

#     count = len(document)

#     document.close()

#     return count


# def pdf_size_kb(pdf_bytes):
#     return len(pdf_bytes) / 1024


# # =========================================================
# # PDF MERGE
# # =========================================================

# def merge_pdfs(pdf_files):

#     output = pymupdf.open()

#     for pdf_bytes in pdf_files:

#         source = open_pdf(pdf_bytes)

#         output.insert_pdf(
#             source
#         )

#         source.close()

#     result = output.tobytes(
#         garbage=4,
#         deflate=True,
#     )

#     output.close()

#     return result


# # =========================================================
# # PDF COMPRESS
# # =========================================================

# def compress_pdf(pdf_bytes):

#     document = open_pdf(pdf_bytes)

#     result = document.tobytes(
#         garbage=4,
#         deflate=True,
#         clean=True,
#     )

#     document.close()

#     return result


# # =========================================================
# # PDF SPLIT
# # =========================================================

# def split_pdf(
#     pdf_bytes,
#     start_page,
#     end_page,
# ):

#     source = open_pdf(pdf_bytes)

#     output = pymupdf.open()

#     output.insert_pdf(
#         source,
#         from_page=start_page,
#         to_page=end_page,
#     )

#     result = output.tobytes(
#         garbage=4,
#         deflate=True,
#     )

#     output.close()
#     source.close()

#     return result


# # =========================================================
# # PDF DELETE PAGES
# # =========================================================

# def delete_pdf_pages(
#     pdf_bytes,
#     pages_to_delete,
# ):

#     document = open_pdf(pdf_bytes)

#     for page_index in sorted(
#         pages_to_delete,
#         reverse=True,
#     ):

#         if (
#             0 <= page_index
#             < len(document)
#         ):
#             document.delete_page(
#                 page_index
#             )

#     if len(document) == 0:

#         document.close()

#         return None

#     result = document.tobytes(
#         garbage=4,
#         deflate=True,
#     )

#     document.close()

#     return result


# # =========================================================
# # PDF REORDER PAGES
# # =========================================================

# def reorder_pdf_pages(
#     pdf_bytes,
#     new_order,
# ):

#     source = open_pdf(pdf_bytes)

#     output = pymupdf.open()

#     output.insert_pdf(
#         source,
#         from_page=0,
#         to_page=-1,
#         final=0,
#     )

#     # Remove all pages from temporary
#     # document, then insert pages in
#     # requested order.
#     output.delete_pages(
#         range(len(output))
#     )

#     for page_index in new_order:

#         output.insert_pdf(
#             source,
#             from_page=page_index,
#             to_page=page_index,
#         )

#     result = output.tobytes(
#         garbage=4,
#         deflate=True,
#     )

#     output.close()
#     source.close()

#     return result


# # =========================================================
# # PDF ROTATE
# # =========================================================

# def rotate_pdf_pages(
#     pdf_bytes,
#     rotation,
#     selected_pages=None,
# ):

#     document = open_pdf(pdf_bytes)

#     if selected_pages is None:

#         selected_pages = list(
#             range(len(document))
#         )

#     for page_index in selected_pages:

#         if (
#             0 <= page_index
#             < len(document)
#         ):

#             page = document[
#                 page_index
#             ]

#             page.set_rotation(
#                 (
#                     page.rotation
#                     + rotation
#                 ) % 360
#             )

#     result = document.tobytes(
#         garbage=4,
#         deflate=True,
#     )

#     document.close()

#     return result


# # =========================================================
# # HEADER
# # =========================================================

# st.title(
#     "📄 Smart Document & Image Toolkit"
# )

# st.caption(
#     "Image → PDF • PDF Tools • PDF → Image • "
#     "Scan • Auto Crop • Compress"
# )


# # =========================================================
# # SIDEBAR
# # =========================================================

# with st.sidebar:

#     st.subheader("Select Tool")

#     tool = st.radio(
#         "",
#         [
#             "Image → PDF",
#             "PDF Tools",
#             "PDF → Image",
#             "Scan Anything",
#             "Compress Photo",
#         ],
#     )


# # =========================================================
# # IMAGE TO PDF
# # =========================================================

# if tool == "Image → PDF":

#     st.header(
#         "Image → PDF"
#     )

#     files = st.file_uploader(
#         "Upload images",
#         type=[
#             "jpg",
#             "jpeg",
#             "png",
#             "webp",
#         ],
#         accept_multiple_files=True,
#     )

#     page_size = st.selectbox(
#         "Page Size",
#         [
#             "A4",
#             "Original",
#         ],
#     )

#     quality = st.slider(
#         "Image Quality",
#         50,
#         95,
#         85,
#     )

#     if files:

#         images = [
#             bytes_to_image(
#                 file.getvalue()
#             )
#             for file in files
#         ]

#         st.success(
#             f"{len(images)} image(s) selected."
#         )

#         st.image(
#             images[0],
#             caption="Preview",
#             use_container_width=True,
#         )

#         if len(images) > 1:

#             st.caption(
#                 f"{len(images)} images will become "
#                 f"{len(images)} PDF pages."
#             )

#         if st.button(
#             "Create PDF",
#             type="primary",
#             use_container_width=True,
#         ):

#             pdf = images_to_pdf(
#                 images,
#                 page_size,
#                 quality,
#             )

#             st.success(
#                 f"PDF created: {len(images)} page(s)"
#             )

#             st.download_button(
#                 "Download PDF",
#                 pdf,
#                 "images.pdf",
#                 "application/pdf",
#                 use_container_width=True,
#             )


# # =========================================================
# # PDF TOOLS — BATCH 2
# # =========================================================

# elif tool == "PDF Tools":

#     st.header(
#         "PDF Tools"
#     )

#     operation = st.selectbox(
#         "Choose PDF operation",
#         [
#             "Merge PDF",
#             "Compress PDF",
#             "Split PDF",
#             "Delete PDF Pages",
#             "Reorder PDF Pages",
#             "Rotate PDF",
#         ],
#     )


#     # =====================================================
#     # PDF MERGE
#     # =====================================================

#     if operation == "Merge PDF":

#         st.subheader(
#             "Merge PDF"
#         )

#         files = st.file_uploader(
#             "Upload PDF files in the order you want to merge",
#             type=["pdf"],
#             accept_multiple_files=True,
#             key="merge_pdf_uploader",
#         )

#         if files:

#             st.success(
#                 f"{len(files)} PDF file(s) selected."
#             )

#             for index, file in enumerate(
#                 files,
#                 start=1,
#             ):

#                 page_count = pdf_page_count(
#                     file.getvalue()
#                 )

#                 st.caption(
#                     f"{index}. {file.name} — "
#                     f"{page_count} page(s)"
#                 )

#             if len(files) < 2:

#                 st.info(
#                     "Select at least 2 PDF files to merge."
#                 )

#             else:

#                 if st.button(
#                     "Merge PDFs",
#                     type="primary",
#                     use_container_width=True,
#                 ):

#                     pdf_files = [
#                         file.getvalue()
#                         for file in files
#                     ]

#                     merged = merge_pdfs(
#                         pdf_files
#                     )

#                     st.success(
#                         f"Merged {len(files)} PDF files "
#                         f"into one PDF."
#                     )

#                     st.download_button(
#                         "Download Merged PDF",
#                         merged,
#                         "merged.pdf",
#                         "application/pdf",
#                         use_container_width=True,
#                     )


#     # =====================================================
#     # PDF COMPRESS
#     # =====================================================

#     elif operation == "Compress PDF":

#         st.subheader(
#             "Compress PDF"
#         )

#         file = st.file_uploader(
#             "Upload PDF",
#             type=["pdf"],
#             key="compress_pdf_uploader",
#         )

#         if file:

#             original = file.getvalue()

#             original_size = pdf_size_kb(
#                 original
#             )

#             st.info(
#                 f"Original size: "
#                 f"{original_size:.1f} KB"
#             )

#             if st.button(
#                 "Compress PDF",
#                 type="primary",
#                 use_container_width=True,
#             ):

#                 compressed = compress_pdf(
#                     original
#                 )

#                 compressed_size = pdf_size_kb(
#                     compressed
#                 )

#                 reduction = 0

#                 if original_size > 0:

#                     reduction = (
#                         (
#                             original_size
#                             - compressed_size
#                         )
#                         / original_size
#                     ) * 100

#                 if compressed_size < original_size:

#                     st.success(
#                         f"Compressed: "
#                         f"{compressed_size:.1f} KB "
#                         f"({reduction:.1f}% smaller)"
#                     )

#                 else:

#                     st.warning(
#                         "This PDF could not be made smaller "
#                         "with lossless compression."
#                     )

#                 st.download_button(
#                     "Download Compressed PDF",
#                     compressed,
#                     "compressed.pdf",
#                     "application/pdf",
#                     use_container_width=True,
#                 )


#     # =====================================================
#     # PDF SPLIT
#     # =====================================================

#     elif operation == "Split PDF":

#         st.subheader(
#             "Split PDF"
#         )

#         file = st.file_uploader(
#             "Upload PDF",
#             type=["pdf"],
#             key="split_pdf_uploader",
#         )

#         if file:

#             pdf_bytes = file.getvalue()

#             page_count = pdf_page_count(
#                 pdf_bytes
#             )

#             st.info(
#                 f"Total pages: {page_count}"
#             )

#             if page_count == 1:

#                 st.warning(
#                     "A one-page PDF cannot be split into multiple parts."
#                 )

#             else:

#                 start_page = st.number_input(
#                     "Start page",
#                     min_value=1,
#                     max_value=page_count,
#                     value=1,
#                     step=1,
#                 )

#                 end_page = st.number_input(
#                     "End page",
#                     min_value=1,
#                     max_value=page_count,
#                     value=page_count,
#                     step=1,
#                 )

#                 if start_page > end_page:

#                     st.error(
#                         "Start page must be less than or equal to end page."
#                     )

#                 else:

#                     selected_count = (
#                         end_page
#                         - start_page
#                         + 1
#                     )

#                     st.caption(
#                         f"Selected pages: "
#                         f"{start_page}–{end_page} "
#                         f"({selected_count} page(s))"
#                     )

#                     if st.button(
#                         "Split PDF",
#                         type="primary",
#                         use_container_width=True,
#                     ):

#                         result = split_pdf(
#                             pdf_bytes,
#                             start_page - 1,
#                             end_page - 1,
#                         )

#                         st.success(
#                             f"Created PDF with "
#                             f"{selected_count} page(s)."
#                         )

#                         st.download_button(
#                             "Download Split PDF",
#                             result,
#                             "split.pdf",
#                             "application/pdf",
#                             use_container_width=True,
#                         )


#     # =====================================================
#     # DELETE PDF PAGES
#     # =====================================================

#     elif operation == "Delete PDF Pages":

#         st.subheader(
#             "Delete PDF Pages"
#         )

#         file = st.file_uploader(
#             "Upload PDF",
#             type=["pdf"],
#             key="delete_pdf_uploader",
#         )

#         if file:

#             pdf_bytes = file.getvalue()

#             page_count = pdf_page_count(
#                 pdf_bytes
#             )

#             st.info(
#                 f"Total pages: {page_count}"
#             )

#             page_options = list(
#                 range(
#                     1,
#                     page_count + 1,
#                 )
#             )

#             pages_to_delete = st.multiselect(
#                 "Select pages to delete",
#                 page_options,
#                 format_func=lambda x:
#                     f"Page {x}",
#                 key="pages_to_delete",
#             )

#             if pages_to_delete:

#                 remaining = (
#                     page_count
#                     - len(pages_to_delete)
#                 )

#                 st.warning(
#                     f"{len(pages_to_delete)} page(s) "
#                     f"will be deleted. "
#                     f"{remaining} page(s) will remain."
#                 )

#                 if remaining == 0:

#                     st.error(
#                         "You cannot delete all pages."
#                     )

#                 else:

#                     if st.button(
#                         "Delete Selected Pages",
#                         type="primary",
#                         use_container_width=True,
#                     ):

#                         zero_based_pages = [
#                             page - 1
#                             for page in pages_to_delete
#                         ]

#                         result = delete_pdf_pages(
#                             pdf_bytes,
#                             zero_based_pages,
#                         )

#                         if result is not None:

#                             st.success(
#                                 f"Deleted "
#                                 f"{len(pages_to_delete)} page(s)."
#                             )

#                             st.download_button(
#                                 "Download Updated PDF",
#                                 result,
#                                 "pages_deleted.pdf",
#                                 "application/pdf",
#                                 use_container_width=True,
#                             )


#     # =====================================================
#     # REORDER PDF PAGES
#     # =====================================================

#     elif operation == "Reorder PDF Pages":

#         st.subheader(
#             "Reorder PDF Pages"
#         )

#         file = st.file_uploader(
#             "Upload PDF",
#             type=["pdf"],
#             key="reorder_pdf_uploader",
#         )

#         if file:

#             pdf_bytes = file.getvalue()

#             page_count = pdf_page_count(
#                 pdf_bytes
#             )

#             st.info(
#                 f"Total pages: {page_count}"
#             )

#             if page_count < 2:

#                 st.warning(
#                     "At least 2 pages are needed for reordering."
#                 )

#             else:

#                 default_order = [
#                     str(i)
#                     for i in range(
#                         1,
#                         page_count + 1,
#                     )
#                 ]

#                 order = st.multiselect(
#                     "Select pages in the new order",
#                     options=default_order,
#                     default=default_order,
#                     format_func=lambda x:
#                         f"Page {x}",
#                     key="reorder_pages",
#                 )

#                 if len(order) != page_count:

#                     st.warning(
#                         "Please include every page exactly once "
#                         "in the new order."
#                     )

#                 else:

#                     st.caption(
#                         "New order: "
#                         + " → ".join(
#                             f"Page {x}"
#                             for x in order
#                         )
#                     )

#                     if st.button(
#                         "Reorder Pages",
#                         type="primary",
#                         use_container_width=True,
#                     ):

#                         new_order = [
#                             int(page) - 1
#                             for page in order
#                         ]

#                         result = reorder_pdf_pages(
#                             pdf_bytes,
#                             new_order,
#                         )

#                         st.success(
#                             "PDF pages reordered successfully."
#                         )

#                         st.download_button(
#                             "Download Reordered PDF",
#                             result,
#                             "reordered.pdf",
#                             "application/pdf",
#                             use_container_width=True,
#                         )


#     # =====================================================
#     # ROTATE PDF
#     # =====================================================

#     elif operation == "Rotate PDF":

#         st.subheader(
#             "Rotate PDF"
#         )

#         file = st.file_uploader(
#             "Upload PDF",
#             type=["pdf"],
#             key="rotate_pdf_uploader",
#         )

#         if file:

#             pdf_bytes = file.getvalue()

#             page_count = pdf_page_count(
#                 pdf_bytes
#             )

#             st.info(
#                 f"Total pages: {page_count}"
#             )

#             rotation = st.selectbox(
#                 "Rotation",
#                 [
#                     ("90° clockwise", 90),
#                     ("180°", 180),
#                     ("270° clockwise", 270),
#                 ],
#                 format_func=lambda x:
#                     x[0],
#             )

#             page_mode = st.radio(
#                 "Apply rotation to",
#                 [
#                     "All pages",
#                     "Selected pages",
#                 ],
#             )

#             selected_pages = None

#             if page_mode == "Selected pages":

#                 page_options = list(
#                     range(
#                         1,
#                         page_count + 1,
#                     )
#                 )

#                 selected = st.multiselect(
#                     "Select pages",
#                     page_options,
#                     format_func=lambda x:
#                         f"Page {x}",
#                     key="rotate_pages",
#                 )

#                 if not selected:

#                     st.warning(
#                         "Select at least one page."
#                     )

#                 else:

#                     selected_pages = [
#                         page - 1
#                         for page in selected
#                     ]

#             can_rotate = (
#                 page_mode == "All pages"
#                 or (
#                     selected_pages is not None
#                     and len(selected_pages) > 0
#                 )
#             )

#             if can_rotate:

#                 if st.button(
#                     "Rotate PDF",
#                     type="primary",
#                     use_container_width=True,
#                 ):

#                     result = rotate_pdf_pages(
#                         pdf_bytes,
#                         rotation[1],
#                         selected_pages,
#                     )

#                     st.success(
#                         "PDF pages rotated successfully."
#                     )

#                     st.download_button(
#                         "Download Rotated PDF",
#                         result,
#                         "rotated.pdf",
#                         "application/pdf",
#                         use_container_width=True,
#                     )


# # =========================================================
# # PDF TO IMAGE
# # =========================================================

# elif tool == "PDF → Image":

#     st.header(
#         "PDF → Image"
#     )

#     file = st.file_uploader(
#         "Upload PDF",
#         type=["pdf"],
#     )

#     dpi = st.select_slider(
#         "DPI",
#         options=[
#             96,
#             120,
#             150,
#             200,
#             250,
#             300,
#         ],
#         value=150,
#     )

#     if file:

#         if st.button(
#             "Convert PDF",
#             type="primary",
#             use_container_width=True,
#         ):

#             pages = pdf_to_images(
#                 file.getvalue(),
#                 dpi,
#             )

#             st.success(
#                 f"{len(pages)} page(s) converted."
#             )

#             for name, data in pages[:3]:

#                 st.image(
#                     data,
#                     caption=name,
#                     use_container_width=True,
#                 )

#             if len(pages) == 1:

#                 st.download_button(
#                     "Download Image",
#                     pages[0][1],
#                     pages[0][0],
#                     "image/png",
#                     use_container_width=True,
#                 )

#             else:

#                 zip_data = create_zip(
#                     pages
#                 )

#                 st.download_button(
#                     "Download All Images ZIP",
#                     zip_data,
#                     "pdf_pages.zip",
#                     "application/zip",
#                     use_container_width=True,
#                 )


# # =========================================================
# # SCAN ANYTHING
# # =========================================================

# elif tool == "Scan Anything":

#     st.header(
#         "Scan Anything"
#     )

#     file = st.file_uploader(
#         "Upload document/photo",
#         type=[
#             "jpg",
#             "jpeg",
#             "png",
#             "webp",
#         ],
#     )

#     if file:

#         original = bytes_to_image(
#             file.getvalue()
#         )

#         auto = st.checkbox(
#             "Auto Crop + Perspective Correction",
#             value=True,
#         )

#         filter_name = st.selectbox(
#             "Filter",
#             [
#                 "Document",
#                 "Original",
#                 "B&W",
#                 "Gray",
#                 "Enhance",
#             ],
#         )

#         strength = st.slider(
#             "Filter Strength",
#             0,
#             100,
#             50,
#         )

#         processed = original

#         if auto:

#             processed = auto_crop(
#                 processed
#             )

#         processed = apply_filter(
#             processed,
#             filter_name,
#             strength,
#         )

#         st.subheader(
#             "Before"
#         )

#         st.image(
#             original,
#             use_container_width=True,
#         )

#         st.subheader(
#             "After"
#         )

#         st.image(
#             processed,
#             use_container_width=True,
#         )

#         jpg = image_to_jpeg(
#             processed,
#             92,
#         )

#         pdf = images_to_pdf(
#             [processed],
#             "A4",
#             92,
#         )

#         st.download_button(
#             "Download JPG",
#             jpg,
#             "scanned_document.jpg",
#             "image/jpeg",
#             use_container_width=True,
#         )

#         st.download_button(
#             "Download PDF",
#             pdf,
#             "scanned_document.pdf",
#             "application/pdf",
#             use_container_width=True,
#         )


# # =========================================================
# # COMPRESS PHOTO
# # =========================================================

# elif tool == "Compress Photo":

#     st.header(
#         "Compress Photo"
#     )

#     file = st.file_uploader(
#         "Upload Photo",
#         type=[
#             "jpg",
#             "jpeg",
#             "png",
#             "webp",
#         ],
#     )

#     target_kb = st.selectbox(
#         "Maximum Target Size",
#         [
#             20,
#             50,
#             100,
#             200,
#             500,
#             1000,
#         ],
#         index=2,
#         format_func=lambda x:
#             f"{x} KB",
#     )

#     max_dimension = st.select_slider(
#         "Maximum Dimension",
#         options=[
#             800,
#             1000,
#             1200,
#             1600,
#             2000,
#             2500,
#             3000,
#         ],
#         value=1600,
#     )

#     if file:

#         original = bytes_to_image(
#             file.getvalue()
#         )

#         original_size = (
#             len(file.getvalue())
#             / 1024
#         )

#         st.image(
#             original,
#             caption=f"Original: {original_size:.1f} KB",
#             use_container_width=True,
#         )

#         if st.button(
#             "Compress Photo",
#             type="primary",
#             use_container_width=True,
#         ):

#             output = compress_photo(
#                 original,
#                 target_kb,
#                 max_dimension,
#             )

#             output_size = (
#                 len(output)
#                 / 1024
#             )

#             st.success(
#                 f"Output size: {output_size:.1f} KB"
#             )

#             st.download_button(
#                 "Download Compressed Photo",
#                 output,
#                 "compressed_photo.jpg",
#                 "image/jpeg",
#                 use_container_width=True,
#             )


# # =========================================================
# # FOOTER
# # =========================================================

# st.divider()

# st.caption(
#     "Smart Document & Image Toolkit • "
#     "Lightweight Streamlit MVP • Batch 2"
# )


import io
import zipfile

import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pymupdf


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Smart Document & Image Toolkit",
    page_icon="📄",
    layout="wide",
)


# ============================================================
# MOBILE / UI CSS
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        h1 {
            font-size: 2rem !important;
        }

        h2 {
            font-size: 1.5rem !important;
        }

        h3 {
            font-size: 1.2rem !important;
        }
    }

    .tool-card {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 1rem;
    }

    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        opacity: 0.7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# IMAGE HELPERS
# ============================================================

def bytes_to_image(file_bytes):
    """Convert uploaded bytes to PIL Image."""
    return Image.open(io.BytesIO(file_bytes)).convert("RGB")


def image_to_jpeg(image, quality=95):
    """Convert PIL image to JPEG bytes."""
    buffer = io.BytesIO()
    image.convert("RGB").save(
        buffer,
        format="JPEG",
        quality=quality,
        optimize=True,
    )
    return buffer.getvalue()


def resize_max(image, max_width=2000, max_height=2000):
    """Resize image while preserving aspect ratio."""
    img = image.copy()
    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return img


# ============================================================
# OPENCV CONVERSION
# ============================================================

def pil_to_cv(image):
    """PIL RGB -> OpenCV BGR."""
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def cv_to_pil(image):
    """OpenCV BGR/GRAY -> PIL RGB."""
    if len(image.shape) == 2:
        return Image.fromarray(image).convert("RGB")

    return Image.fromarray(
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    ).convert("RGB")


# ============================================================
# DOCUMENT DETECTION
# ============================================================

def detect_document_corners(image):
    """
    Detect the largest rectangular document-like contour.
    Returns four corner points or None.
    """
    cv_image = pil_to_cv(image)

    original_height, original_width = cv_image.shape[:2]

    scale = 1.0

    max_dimension = 1200

    if max(original_width, original_height) > max_dimension:
        scale = max_dimension / max(original_width, original_height)

        resized = cv2.resize(
            cv_image,
            (
                int(original_width * scale),
                int(original_height * scale),
            ),
        )
    else:
        resized = cv_image.copy()

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(gray, 50, 150)

    kernel = np.ones((5, 5), np.uint8)

    edges = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel,
    )

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    contours = sorted(
        contours,
        key=cv2.contourArea,
        reverse=True,
    )

    image_area = resized.shape[0] * resized.shape[1]

    for contour in contours[:20]:
        area = cv2.contourArea(contour)

        if area < image_area * 0.15:
            continue

        perimeter = cv2.arcLength(contour, True)

        approximation = cv2.approxPolyDP(
            contour,
            0.02 * perimeter,
            True,
        )

        if len(approximation) == 4:
            points = approximation.reshape(4, 2).astype(np.float32)

            if scale != 1.0:
                points /= scale

            return points

    return None


def order_points(points):
    """Order points as top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype=np.float32)

    total = points.sum(axis=1)

    rect[0] = points[np.argmin(total)]
    rect[2] = points[np.argmax(total)]

    difference = np.diff(points, axis=1)

    rect[1] = points[np.argmin(difference)]
    rect[3] = points[np.argmax(difference)]

    return rect


def auto_crop(image):
    """Crop image to detected document rectangle."""
    points = detect_document_corners(image)

    if points is None:
        return image

    points = order_points(points)

    x_min = int(max(0, np.min(points[:, 0])))
    y_min = int(max(0, np.min(points[:, 1])))

    x_max = int(min(image.width, np.max(points[:, 0])))
    y_max = int(min(image.height, np.max(points[:, 1])))

    if x_max <= x_min or y_max <= y_min:
        return image

    cropped = image.crop(
        (
            x_min,
            y_min,
            x_max,
            y_max,
        )
    )

    return cropped


def perspective_correct(image):
    """Apply perspective correction to detected document."""
    points = detect_document_corners(image)

    if points is None:
        return image

    points = order_points(points)

    top_left, top_right, bottom_right, bottom_left = points

    width_top = np.linalg.norm(top_right - top_left)
    width_bottom = np.linalg.norm(bottom_right - bottom_left)

    max_width = int(max(width_top, width_bottom))

    height_left = np.linalg.norm(bottom_left - top_left)
    height_right = np.linalg.norm(bottom_right - top_right)

    max_height = int(max(height_left, height_right))

    if max_width < 100 or max_height < 100:
        return image

    destination = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype=np.float32,
    )

    matrix = cv2.getPerspectiveTransform(
        points,
        destination,
    )

    cv_image = pil_to_cv(image)

    warped = cv2.warpPerspective(
        cv_image,
        matrix,
        (max_width, max_height),
    )

    return cv_to_pil(warped)


# ============================================================
# IMAGE FILTERS
# ============================================================

def apply_filter(image, filter_name):
    """Apply selected image filter."""

    img = image.convert("RGB")

    # --------------------------------------------------------
    # ORIGINAL
    # --------------------------------------------------------

    if filter_name == "Original":
        return img

    # --------------------------------------------------------
    # GRAY
    # --------------------------------------------------------

    if filter_name == "Gray":
        return img.convert("L").convert("RGB")

    # --------------------------------------------------------
    # B&W
    # --------------------------------------------------------

    if filter_name == "B&W":
        gray = np.array(img.convert("L"))

        _, result = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )

        return Image.fromarray(result).convert("RGB")

    # --------------------------------------------------------
    # DOCUMENT
    # --------------------------------------------------------

    if filter_name == "Document":
        cv_image = pil_to_cv(img)

        gray = cv2.cvtColor(
            cv_image,
            cv2.COLOR_BGR2GRAY,
        )

        gray = cv2.GaussianBlur(
            gray,
            (5, 5),
            0,
        )

        result = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            15,
        )

        return Image.fromarray(result).convert("RGB")

    # --------------------------------------------------------
    # ENHANCE
    # --------------------------------------------------------

    if filter_name == "Enhance":
        result = ImageEnhance.Contrast(img).enhance(1.35)
        result = ImageEnhance.Sharpness(result).enhance(1.5)
        result = ImageEnhance.Color(result).enhance(1.1)

        return result

    # --------------------------------------------------------
    # LIGHT ENHANCEMENT
    # --------------------------------------------------------

    if filter_name == "Light Enhancement":
        result = ImageEnhance.Brightness(img).enhance(1.12)
        result = ImageEnhance.Contrast(result).enhance(1.12)

        return result

    # --------------------------------------------------------
    # OUTLINE
    # White background + black outline
    # --------------------------------------------------------

    if filter_name == "Outline":
        cv_image = pil_to_cv(img)

        gray = cv2.cvtColor(
            cv_image,
            cv2.COLOR_BGR2GRAY,
        )

        gray = cv2.GaussianBlur(
            gray,
            (5, 5),
            0,
        )

        edges = cv2.Canny(
            gray,
            50,
            150,
        )

        # Remove small noise
        kernel = np.ones(
            (2, 2),
            np.uint8,
        )

        edges = cv2.morphologyEx(
            edges,
            cv2.MORPH_OPEN,
            kernel,
        )

        # White background + black lines
        result = 255 - edges

        # Make the background clean white
        _, result = cv2.threshold(
            result,
            220,
            255,
            cv2.THRESH_BINARY,
        )

        return Image.fromarray(result).convert("RGB")

    # --------------------------------------------------------
    # COLOR TONE
    # --------------------------------------------------------

    if filter_name == "Color Tone":
        cv_image = pil_to_cv(img)

        b, g, r = cv2.split(
            cv_image.astype(np.float32)
        )

        r = np.clip(r * 1.08 + 5, 0, 255)
        g = np.clip(g * 1.02, 0, 255)
        b = np.clip(b * 0.92, 0, 255)

        result = cv2.merge(
            [
                b.astype(np.uint8),
                g.astype(np.uint8),
                r.astype(np.uint8),
            ]
        )

        return cv_to_pil(result)

    # --------------------------------------------------------
    # BRIGHTNESS TONE
    # --------------------------------------------------------

    if filter_name == "Brightness Tone":
        result = ImageEnhance.Brightness(
            img
        ).enhance(1.20)

        result = ImageEnhance.Contrast(
            result
        ).enhance(1.10)

        return result

    # --------------------------------------------------------
    # BLUR REMOVAL
    # --------------------------------------------------------

    if filter_name == "Blur Removal":
        cv_image = pil_to_cv(img)

        blurred = cv2.GaussianBlur(
            cv_image,
            (0, 0),
            3,
        )

        result = cv2.addWeighted(
            cv_image,
            1.7,
            blurred,
            -0.7,
            0,
        )

        return cv_to_pil(result)

    # --------------------------------------------------------
    # SHARPEN
    # --------------------------------------------------------

    if filter_name == "Sharpen":
        return ImageEnhance.Sharpness(
            img
        ).enhance(2.0)

    # --------------------------------------------------------
    # SKIN TONE SHARPEN
    # --------------------------------------------------------

    if filter_name == "Skin Tone Sharpen":
        cv_image = pil_to_cv(img)

        hsv = cv2.cvtColor(
            cv_image,
            cv2.COLOR_BGR2HSV,
        )

        lower_skin = np.array(
            [0, 20, 50],
            dtype=np.uint8,
        )

        upper_skin = np.array(
            [25, 255, 255],
            dtype=np.uint8,
        )

        mask = cv2.inRange(
            hsv,
            lower_skin,
            upper_skin,
        )

        mask = cv2.GaussianBlur(
            mask,
            (5, 5),
            0,
        )

        sharpened = cv2.detailEnhance(
            cv_image,
            sigma_s=10,
            sigma_r=0.15,
        )

        mask_3 = cv2.cvtColor(
            mask,
            cv2.COLOR_GRAY2BGR,
        )

        result = np.where(
            mask_3 > 0,
            sharpened,
            cv_image,
        )

        return cv_to_pil(result.astype(np.uint8))

    # --------------------------------------------------------
    # SEPIA
    # --------------------------------------------------------

    if filter_name == "Sepia":
        cv_image = pil_to_cv(img)

        kernel = np.array(
            [
                [0.272, 0.534, 0.131],
                [0.349, 0.686, 0.168],
                [0.393, 0.769, 0.189],
            ]
        )

        result = cv2.transform(
            cv_image,
            kernel,
        )

        result = np.clip(
            result,
            0,
            255,
        ).astype(np.uint8)

        return cv_to_pil(result)

    # --------------------------------------------------------
    # WARM TONE
    # --------------------------------------------------------

    if filter_name == "Warm Tone":
        cv_image = pil_to_cv(img).astype(
            np.float32
        )

        b, g, r = cv2.split(cv_image)

        b *= 0.88
        g *= 1.02
        r *= 1.10

        result = cv2.merge(
            [
                np.clip(b, 0, 255),
                np.clip(g, 0, 255),
                np.clip(r, 0, 255),
            ]
        )

        return cv_to_pil(
            result.astype(np.uint8)
        )

    # --------------------------------------------------------
    # COOL TONE
    # --------------------------------------------------------

    if filter_name == "Cool Tone":
        cv_image = pil_to_cv(img).astype(
            np.float32
        )

        b, g, r = cv2.split(cv_image)

        b *= 1.10
        g *= 1.02
        r *= 0.90

        result = cv2.merge(
            [
                np.clip(b, 0, 255),
                np.clip(g, 0, 255),
                np.clip(r, 0, 255),
            ]
        )

        return cv_to_pil(
            result.astype(np.uint8)
        )

    # --------------------------------------------------------
    # NEGATIVE
    # --------------------------------------------------------

    if filter_name == "Negative":
        return Image.fromarray(
            255 - np.array(img)
        ).convert("RGB")

    # --------------------------------------------------------
    # HIGH CONTRAST
    # --------------------------------------------------------

    if filter_name == "High Contrast":
        result = ImageEnhance.Contrast(
            img
        ).enhance(2.0)

        result = ImageEnhance.Sharpness(
            result
        ).enhance(1.4)

        return result

    # --------------------------------------------------------
    # SOFT
    # --------------------------------------------------------

    if filter_name == "Soft":
        result = img.filter(
            ImageFilter.GaussianBlur(
                radius=1.2
            )
        )

        result = ImageEnhance.Contrast(
            result
        ).enhance(0.95)

        return result

    return img


# ============================================================
# IMAGE -> PDF
# ============================================================

def images_to_pdf(images):
    """Convert multiple images into a single PDF."""
    if not images:
        return None

    processed_images = []

    for image in images:
        processed_images.append(
            image.convert("RGB")
        )

    output = io.BytesIO()

    first = processed_images[0]

    if len(processed_images) > 1:
        first.save(
            output,
            format="PDF",
            save_all=True,
            append_images=processed_images[1:],
        )
    else:
        first.save(
            output,
            format="PDF",
        )

    return output.getvalue()


# ============================================================
# PDF -> IMAGES
# ============================================================

def pdf_to_images(pdf_bytes, dpi=150):
    """Convert PDF pages into PIL images."""
    document = pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf",
    )

    images = []

    zoom = dpi / 72

    matrix = pymupdf.Matrix(
        zoom,
        zoom,
    )

    for page in document:
        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False,
        )

        image = Image.frombytes(
            "RGB",
            [
                pixmap.width,
                pixmap.height,
            ],
            pixmap.samples,
        )

        images.append(image)

    document.close()

    return images


# ============================================================
# ZIP CREATION
# ============================================================

def create_zip(files):
    """Create ZIP archive from list of (filename, bytes)."""
    output = io.BytesIO()

    with zipfile.ZipFile(
        output,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as zip_file:

        for filename, file_bytes in files:
            zip_file.writestr(
                filename,
                file_bytes,
            )

    return output.getvalue()


# ============================================================
# PHOTO COMPRESSION
# ============================================================

def compress_photo(
    image,
    target_kb,
    min_quality=20,
    max_quality=95,
):
    """
    Compress image close to target KB.
    Uses JPEG quality + resizing when necessary.
    """

    target_bytes = target_kb * 1024

    working_image = image.convert("RGB")

    # First attempt: quality search
    low = min_quality
    high = max_quality

    best_bytes = None

    for _ in range(10):
        quality = (low + high) // 2

        data = image_to_jpeg(
            working_image,
            quality=quality,
        )

        if len(data) <= target_bytes:
            best_bytes = data
            low = quality + 1
        else:
            high = quality - 1

    if best_bytes is not None:
        return best_bytes

    # If image is still too large at low quality,
    # progressively resize it.
    width, height = working_image.size

    for _ in range(10):
        working_image = working_image.resize(
            (
                max(1, int(width * 0.85)),
                max(1, int(height * 0.85)),
            ),
            Image.Resampling.LANCZOS,
        )

        width, height = working_image.size

        data = image_to_jpeg(
            working_image,
            quality=min_quality,
        )

        if len(data) <= target_bytes:
            return data

    return data


# ============================================================
# PDF HELPERS
# ============================================================

def open_pdf(pdf_bytes):
    """Open PDF from bytes."""
    return pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf",
    )


def pdf_page_count(pdf_bytes):
    """Return PDF page count."""
    document = open_pdf(pdf_bytes)

    count = len(document)

    document.close()

    return count


def pdf_size_kb(pdf_bytes):
    """Return PDF size in KB."""
    return len(pdf_bytes) / 1024


# ============================================================
# PDF MERGE
# ============================================================

def merge_pdfs(pdf_files):
    """Merge multiple PDFs."""
    output = pymupdf.open()

    for pdf_bytes in pdf_files:
        source = open_pdf(pdf_bytes)

        output.insert_pdf(source)

        source.close()

    result = output.tobytes(
        garbage=4,
        deflate=True,
    )

    output.close()

    return result


# ============================================================
# PDF COMPRESS
# ============================================================

def compress_pdf(pdf_bytes):
    """Compress PDF using PyMuPDF optimization."""
    document = open_pdf(pdf_bytes)

    result = document.tobytes(
        garbage=4,
        clean=True,
        deflate=True,
    )

    document.close()

    return result


# ============================================================
# PDF SPLIT
# ============================================================

def split_pdf(pdf_bytes, page_number):
    """Extract one page from PDF."""
    source = open_pdf(pdf_bytes)

    output = pymupdf.open()

    output.insert_pdf(
        source,
        from_page=page_number,
        to_page=page_number,
    )

    result = output.tobytes(
        garbage=4,
        deflate=True,
    )

    source.close()
    output.close()

    return result


# ============================================================
# PDF DELETE PAGES
# ============================================================

def delete_pdf_pages(pdf_bytes, pages_to_delete):
    """Delete selected pages from PDF."""
    document = open_pdf(pdf_bytes)

    pages_to_delete = sorted(
        set(pages_to_delete),
        reverse=True,
    )

    for page_number in pages_to_delete:
        if 0 <= page_number < len(document):
            document.delete_page(page_number)

    result = document.tobytes(
        garbage=4,
        deflate=True,
    )

    document.close()

    return result


# ============================================================
# PDF REORDER
# ============================================================

def reorder_pdf_pages(pdf_bytes, new_order):
    """Reorder PDF pages."""
    source = open_pdf(pdf_bytes)

    output = pymupdf.open()

    for page_number in new_order:
        if 0 <= page_number < len(source):
            output.insert_pdf(
                source,
                from_page=page_number,
                to_page=page_number,
            )

    result = output.tobytes(
        garbage=4,
        deflate=True,
    )

    source.close()
    output.close()

    return result


# ============================================================
# PDF ROTATE
# ============================================================

def rotate_pdf_pages(
    pdf_bytes,
    rotation,
    selected_pages=None,
):
    """Rotate selected or all PDF pages."""
    document = open_pdf(pdf_bytes)

    if selected_pages is None:
        selected_pages = list(
            range(len(document))
        )

    for page_number in selected_pages:
        if 0 <= page_number < len(document):
            page = document[page_number]

            page.set_rotation(
                (
                    page.rotation + rotation
                ) % 360
            )

    result = document.tobytes(
        garbage=4,
        deflate=True,
    )

    document.close()

    return result


# ============================================================
# HEADER
# ============================================================

st.title("Smart Document & Image Toolkit")

st.caption(
    "Image processing, document scanning, PDF conversion, "
    "PDF management and photo compression."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Tools")

tool = st.sidebar.radio(
    "Select Tool",
    [
        "Image → PDF",
        "PDF Tools",
        "PDF → Image",
        "Scan Anything",
        "Compress Photo",
    ],
)


# ============================================================
# IMAGE → PDF
# ============================================================

if tool == "Image → PDF":

    st.header("Image → PDF")

    uploaded_files = st.file_uploader(
        "Upload images",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
            "bmp",
            "tiff",
        ],
        accept_multiple_files=True,
    )

    if uploaded_files:

        images = []

        for uploaded_file in uploaded_files:

            image = bytes_to_image(
                uploaded_file.getvalue()
            )

            images.append(image)

        st.write(
            f"Selected images: {len(images)}"
        )

        cols = st.columns(
            min(4, len(images))
        )

        for index, image in enumerate(images):
            with cols[index % len(cols)]:
                st.image(
                    image,
                    caption=f"Image {index + 1}",
                    use_container_width=True,
                )

        if st.button(
            "Create PDF",
            type="primary",
        ):

            pdf_bytes = images_to_pdf(
                images
            )

            st.success(
                "PDF created successfully."
            )

            st.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name="images.pdf",
                mime="application/pdf",
            )


# ============================================================
# PDF TOOLS
# ============================================================

elif tool == "PDF Tools":

    st.header("PDF Tools")

    pdf_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
    )

    if pdf_file:

        pdf_bytes = pdf_file.getvalue()

        page_count = pdf_page_count(
            pdf_bytes
        )

        size_kb = pdf_size_kb(
            pdf_bytes
        )

        st.info(
            f"Pages: {page_count} | "
            f"Size: {size_kb:.2f} KB"
        )

        pdf_action = st.selectbox(
            "Select PDF operation",
            [
                "Merge PDF",
                "Compress PDF",
                "Split PDF",
                "Delete PDF Pages",
                "Reorder PDF Pages",
                "Rotate PDF",
            ],
        )

        # ----------------------------------------------------
        # MERGE
        # ----------------------------------------------------

        if pdf_action == "Merge PDF":

            st.subheader("Merge PDF")

            merge_files = st.file_uploader(
                "Upload PDFs to merge",
                type=["pdf"],
                accept_multiple_files=True,
                key="merge_pdf_files",
            )

            if merge_files:

                if st.button(
                    "Merge PDFs",
                    type="primary",
                ):

                    merge_bytes = merge_pdfs(
                        [
                            file.getvalue()
                            for file in merge_files
                        ]
                    )

                    st.success(
                        "PDFs merged successfully."
                    )

                    st.download_button(
                        "Download Merged PDF",
                        data=merge_bytes,
                        file_name="merged.pdf",
                        mime="application/pdf",
                    )

        # ----------------------------------------------------
        # COMPRESS
        # ----------------------------------------------------

        elif pdf_action == "Compress PDF":

            st.subheader("Compress PDF")

            if st.button(
                "Compress PDF",
                type="primary",
            ):

                compressed = compress_pdf(
                    pdf_bytes
                )

                original_size = len(
                    pdf_bytes
                ) / 1024

                compressed_size = len(
                    compressed
                ) / 1024

                st.success(
                    "PDF compression completed."
                )

                st.write(
                    f"Original: {original_size:.2f} KB"
                )

                st.write(
                    f"Compressed: {compressed_size:.2f} KB"
                )

                st.download_button(
                    "Download Compressed PDF",
                    data=compressed,
                    file_name="compressed.pdf",
                    mime="application/pdf",
                )

        # ----------------------------------------------------
        # SPLIT
        # ----------------------------------------------------

        elif pdf_action == "Split PDF":

            st.subheader("Split PDF")

            page_number = st.number_input(
                "Page number",
                min_value=1,
                max_value=page_count,
                value=1,
                step=1,
            )

            if st.button(
                "Extract Page",
                type="primary",
            ):

                result = split_pdf(
                    pdf_bytes,
                    page_number - 1,
                )

                st.success(
                    "Page extracted successfully."
                )

                st.download_button(
                    "Download Page PDF",
                    data=result,
                    file_name=f"page_{page_number}.pdf",
                    mime="application/pdf",
                )

        # ----------------------------------------------------
        # DELETE PAGES
        # ----------------------------------------------------

        elif pdf_action == "Delete PDF Pages":

            st.subheader("Delete PDF Pages")

            pages = st.multiselect(
                "Select pages to delete",
                options=list(
                    range(1, page_count + 1)
                ),
            )

            if st.button(
                "Delete Selected Pages",
                type="primary",
            ):

                if not pages:
                    st.warning(
                        "Select at least one page."
                    )
                elif len(pages) >= page_count:
                    st.error(
                        "At least one page must remain."
                    )
                else:

                    result = delete_pdf_pages(
                        pdf_bytes,
                        [
                            page - 1
                            for page in pages
                        ],
                    )

                    st.success(
                        "Selected pages deleted."
                    )

                    st.download_button(
                        "Download Updated PDF",
                        data=result,
                        file_name="pages_deleted.pdf",
                        mime="application/pdf",
                    )

        # ----------------------------------------------------
        # REORDER
        # ----------------------------------------------------

        elif pdf_action == "Reorder PDF Pages":

            st.subheader(
                "Reorder PDF Pages"
            )

            st.caption(
                "Enter page numbers in the required "
                "order, separated by commas."
            )

            default_order = ", ".join(
                str(i)
                for i in range(
                    1,
                    page_count + 1,
                )
            )

            order_text = st.text_input(
                "Page order",
                value=default_order,
            )

            if st.button(
                "Reorder PDF",
                type="primary",
            ):

                try:

                    order = [
                        int(value.strip())
                        for value in order_text.split(
                            ","
                        )
                        if value.strip()
                    ]

                    if len(order) != page_count:
                        st.error(
                            "Enter every page number exactly once."
                        )
                    elif sorted(order) != list(
                        range(1, page_count + 1)
                    ):
                        st.error(
                            "Page numbers must contain "
                            "every page exactly once."
                        )
                    else:

                        result = reorder_pdf_pages(
                            pdf_bytes,
                            [
                                page - 1
                                for page in order
                            ],
                        )

                        st.success(
                            "Pages reordered successfully."
                        )

                        st.download_button(
                            "Download Reordered PDF",
                            data=result,
                            file_name="reordered.pdf",
                            mime="application/pdf",
                        )

                except ValueError:
                    st.error(
                        "Use only numbers separated by commas."
                    )

        # ----------------------------------------------------
        # ROTATE
        # ----------------------------------------------------

        elif pdf_action == "Rotate PDF":

            st.subheader("Rotate PDF")

            rotation = st.selectbox(
                "Rotation",
                [
                    90,
                    180,
                    270,
                ],
            )

            rotate_scope = st.radio(
                "Apply rotation to",
                [
                    "All pages",
                    "Selected pages",
                ],
            )

            selected_pages = None

            if rotate_scope == "Selected pages":

                selected = st.multiselect(
                    "Select pages",
                    options=list(
                        range(
                            1,
                            page_count + 1,
                        )
                    ),
                )

                selected_pages = [
                    page - 1
                    for page in selected
                ]

            if st.button(
                "Rotate PDF",
                type="primary",
            ):

                if (
                    rotate_scope
                    == "Selected pages"
                    and not selected_pages
                ):
                    st.warning(
                        "Select at least one page."
                    )
                else:

                    result = rotate_pdf_pages(
                        pdf_bytes,
                        rotation,
                        selected_pages,
                    )

                    st.success(
                        "PDF pages rotated successfully."
                    )

                    st.download_button(
                        "Download Rotated PDF",
                        data=result,
                        file_name="rotated.pdf",
                        mime="application/pdf",
                    )


# ============================================================
# PDF → IMAGE
# ============================================================

elif tool == "PDF → Image":

    st.header("PDF → Image")

    pdf_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
    )

    dpi = st.slider(
        "Image quality / DPI",
        min_value=72,
        max_value=300,
        value=150,
        step=12,
    )

    if pdf_file:

        pdf_bytes = pdf_file.getvalue()

        if st.button(
            "Convert PDF",
            type="primary",
        ):

            images = pdf_to_images(
                pdf_bytes,
                dpi=dpi,
            )

            st.success(
                f"{len(images)} page(s) converted."
            )

            files = []

            for index, image in enumerate(
                images
            ):

                image_bytes = image_to_jpeg(
                    image,
                    quality=95,
                )

                files.append(
                    (
                        f"page_{index + 1}.jpg",
                        image_bytes,
                    )
                )

                st.image(
                    image,
                    caption=f"Page {index + 1}",
                    use_container_width=True,
                )

            zip_bytes = create_zip(
                files
            )

            st.download_button(
                "Download All Images (ZIP)",
                data=zip_bytes,
                file_name="pdf_images.zip",
                mime="application/zip",
            )


# ============================================================
# SCAN ANYTHING
# ============================================================

elif tool == "Scan Anything":

    st.header("Scan Anything")

    uploaded_file = st.file_uploader(
        "Upload document image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
            "bmp",
            "tiff",
        ],
    )

    if uploaded_file:

        original_image = bytes_to_image(
            uploaded_file.getvalue()
        )

        st.subheader("Scan Settings")

        auto_crop_enabled = st.checkbox(
            "Auto Crop",
            value=True,
            help=(
                "Automatically crop the detected "
                "document area."
            ),
        )

        perspective_enabled = st.checkbox(
            "Perspective Correction",
            value=True,
            help=(
                "Correct the angle/perspective "
                "of the document."
            ),
        )

        filter_options = [
            "Document",
            "Original",
            "B&W",
            "Gray",
            "Light Enhancement",
            "Outline",
            "Color Tone",
            "Brightness Tone",
            "Blur Removal",
            "Sharpen",
            "Skin Tone Sharpen",
            "Enhance",
            "Sepia",
            "Warm Tone",
            "Cool Tone",
            "Negative",
            "High Contrast",
            "Soft",
        ]

        selected_filter = st.selectbox(
            "Filter",
            filter_options,
        )

        if st.button(
            "Process Scan",
            type="primary",
        ):

            processed_image = original_image.copy()

            # Auto Crop and Perspective Correction
            # are intentionally independent.

            if auto_crop_enabled:
                processed_image = auto_crop(
                    processed_image
                )

            if perspective_enabled:
                processed_image = perspective_correct(
                    processed_image
                )

            processed_image = apply_filter(
                processed_image,
                selected_filter,
            )

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Original")

                st.image(
                    original_image,
                    use_container_width=True,
                )

            with col2:
                st.subheader("Processed")

                st.image(
                    processed_image,
                    use_container_width=True,
                )

            processed_jpeg = image_to_jpeg(
                processed_image,
                quality=95,
            )

            st.download_button(
                "Download Scanned Image",
                data=processed_jpeg,
                file_name="scanned_document.jpg",
                mime="image/jpeg",
            )

            scanned_pdf = images_to_pdf(
                [processed_image]
            )

            st.download_button(
                "Download as PDF",
                data=scanned_pdf,
                file_name="scanned_document.pdf",
                mime="application/pdf",
            )


# ============================================================
# COMPRESS PHOTO
# ============================================================

elif tool == "Compress Photo":

    st.header("Compress Photo")

    uploaded_file = st.file_uploader(
        "Upload photo",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
            "bmp",
            "tiff",
        ],
    )

    if uploaded_file:

        original_image = bytes_to_image(
            uploaded_file.getvalue()
        )

        original_size_kb = (
            len(uploaded_file.getvalue())
            / 1024
        )

        st.info(
            f"Original size: "
            f"{original_size_kb:.2f} KB"
        )

        # 20 KB, then 50 KB, 100 KB, 150 KB...
        # up to 1000 KB.
        target_sizes = [
            20
        ] + list(
            range(
                50,
                1001,
                50,
            )
        )

        target_size = st.selectbox(
            "Target file size",
            target_sizes,
            format_func=lambda x: f"{x} KB",
        )

        if st.button(
            "Compress Photo",
            type="primary",
        ):

            compressed_bytes = compress_photo(
                original_image,
                target_size,
            )

            compressed_size_kb = (
                len(compressed_bytes)
                / 1024
            )

            st.success(
                "Photo compression completed."
            )

            st.write(
                f"Target: {target_size} KB"
            )

            st.write(
                f"Result: {compressed_size_kb:.2f} KB"
            )

            st.image(
                compressed_bytes,
                caption="Compressed Photo",
                use_container_width=True,
            )

            st.download_button(
                "Download Compressed Photo",
                data=compressed_bytes,
                file_name="compressed_photo.jpg",
                mime="image/jpeg",
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Smart Document & Image Toolkit
    </div>
    """,
    unsafe_allow_html=True,
)