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
#     layout="wide",
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


#     # Order points

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


#     # Resize further if quality alone
#     # cannot reach target size.

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
# # SIDEBAR
# # =========================================================

# st.title(
#     "📄 Smart Document & Image Toolkit"
# )

# st.caption(
#     "Image → PDF • PDF → Image • Scan • Auto Crop • Compress"
# )


# tool = st.sidebar.radio(
#     "Select Tool",
#     [
#         "Image → PDF",
#         "PDF → Image",
#         "Scan Anything",
#         "Compress Photo",
#     ],
# )


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


#         st.image(
#             images[0],
#             caption="Preview",
#             use_container_width=True,
#         )


#         if st.button(
#             "Create PDF",
#             type="primary",
#         ):

#             pdf = images_to_pdf(
#                 images,
#                 page_size,
#                 quality,
#             )


#             st.download_button(
#                 "Download PDF",
#                 pdf,
#                 "images.pdf",
#                 "application/pdf",
#             )


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


#         col1, col2 = st.columns(2)


#         with col1:

#             auto = st.checkbox(
#                 "Auto Crop + Perspective Correction",
#                 value=True,
#             )


#         with col2:

#             filter_name = st.selectbox(
#                 "Filter",
#                 [
#                     "Document",
#                     "Original",
#                     "B&W",
#                     "Gray",
#                     "Enhance",
#                 ],
#             )


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


#         before, after = st.columns(2)


#         with before:

#             st.subheader(
#                 "Before"
#             )

#             st.image(
#                 original,
#                 use_container_width=True,
#             )


#         with after:

#             st.subheader(
#                 "After"
#             )

#             st.image(
#                 processed,
#                 use_container_width=True,
#             )


#         jpg = image_to_jpeg(
#             processed,
#             92,
#         )


#         pdf = images_to_pdf(
#             [processed],
#             "A4",
#             92,
#         )


#         col1, col2 = st.columns(2)


#         with col1:

#             st.download_button(
#                 "Download JPG",
#                 jpg,
#                 "scanned_document.jpg",
#                 "image/jpeg",
#             )


#         with col2:

#             st.download_button(
#                 "Download PDF",
#                 pdf,
#                 "scanned_document.pdf",
#                 "application/pdf",
#             )


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
#             )


# # =========================================================
# # FOOTER
# # =========================================================

# st.divider()

# st.caption(
#     "Smart Document & Image Toolkit • "
#     "Lightweight Streamlit MVP"
# )


# # =========================================================
# # 2nd update file
# # =========================================================

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

#     /* Main content spacing */
#     .block-container {
#         padding-top: 1.2rem;
#         padding-bottom: 2rem;
#         padding-left: 1rem;
#         padding-right: 1rem;
#         max-width: 900px;
#     }

#     /* Main title */
#     h1 {
#         font-size: 2rem !important;
#         line-height: 1.2 !important;
#         margin-bottom: 0.3rem !important;
#     }

#     /* Section headings */
#     h2 {
#         font-size: 1.45rem !important;
#     }

#     h3 {
#         font-size: 1.15rem !important;
#     }

#     /* Buttons */
#     .stButton > button,
#     .stDownloadButton > button {
#         width: 100%;
#         min-height: 3rem;
#         border-radius: 10px;
#         font-size: 1rem;
#         font-weight: 600;
#     }

#     /* File uploader */
#     [data-testid="stFileUploader"] {
#         width: 100%;
#     }

#     [data-testid="stFileUploaderDropzone"] {
#         min-height: 120px;
#         border-radius: 12px;
#     }

#     /* Select boxes / sliders / checkboxes */
#     [data-testid="stSelectbox"],
#     [data-testid="stSlider"],
#     [data-testid="stSelectSlider"],
#     [data-testid="stCheckbox"] {
#         margin-bottom: 0.6rem;
#     }

#     /* Images */
#     [data-testid="stImage"] img {
#         border-radius: 10px;
#     }

#     /* Sidebar */
#     [data-testid="stSidebar"] {
#         min-width: 240px;
#     }

#     /* Mobile */
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

#         /* Keep content comfortable for touch */
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
# # HEADER
# # =========================================================

# st.title(
#     "📄 Smart Document & Image Toolkit"
# )

# st.caption(
#     "Image → PDF • PDF → Image • Scan • Auto Crop • Compress"
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

#         st.image(
#             images[0],
#             caption="Preview",
#             use_container_width=True,
#         )

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

#             st.download_button(
#                 "Download PDF",
#                 pdf,
#                 "images.pdf",
#                 "application/pdf",
#                 use_container_width=True,
#             )


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

#         # Mobile-friendly vertical controls
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

#         # Before
#         st.subheader(
#             "Before"
#         )

#         st.image(
#             original,
#             use_container_width=True,
#         )

#         # After
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
#     "Lightweight Streamlit MVP"
# )

# # =========================================================
# # 3rd update file
# # =========================================================

import io
import zipfile

import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageEnhance
import pymupdf


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Smart Document & Image Toolkit",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="auto",
)


# =========================================================
# MOBILE / RESPONSIVE UI
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 900px;
    }

    h1 {
        font-size: 2rem !important;
        line-height: 1.2 !important;
        margin-bottom: 0.3rem !important;
    }

    h2 {
        font-size: 1.45rem !important;
    }

    h3 {
        font-size: 1.15rem !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        width: 100%;
        min-height: 3rem;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 600;
    }

    [data-testid="stFileUploader"] {
        width: 100%;
    }

    [data-testid="stFileUploaderDropzone"] {
        min-height: 120px;
        border-radius: 12px;
    }

    [data-testid="stSelectbox"],
    [data-testid="stMultiSelect"],
    [data-testid="stSlider"],
    [data-testid="stSelectSlider"],
    [data-testid="stCheckbox"],
    [data-testid="stRadio"] {
        margin-bottom: 0.6rem;
    }

    [data-testid="stImage"] img {
        border-radius: 10px;
    }

    [data-testid="stSidebar"] {
        min-width: 240px;
    }

    .pdf-info-box {
        padding: 0.8rem;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 1rem;
    }

    @media (max-width: 640px) {

        .block-container {
            padding-top: 0.8rem;
            padding-left: 0.75rem;
            padding-right: 0.75rem;
            padding-bottom: 1.5rem;
        }

        h1 {
            font-size: 1.55rem !important;
        }

        h2 {
            font-size: 1.3rem !important;
        }

        h3 {
            font-size: 1.05rem !important;
        }

        p {
            font-size: 0.95rem;
        }

        .stButton > button,
        .stDownloadButton > button {
            min-height: 3.2rem;
            font-size: 1rem;
        }

        [data-testid="stFileUploaderDropzone"] {
            min-height: 110px;
        }

        input,
        select,
        textarea {
            font-size: 16px !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# IMAGE HELPERS
# =========================================================

def bytes_to_image(data):
    return Image.open(
        io.BytesIO(data)
    ).convert("RGB")


def image_to_jpeg(image, quality=90):
    buffer = io.BytesIO()

    image.convert("RGB").save(
        buffer,
        format="JPEG",
        quality=int(quality),
        optimize=True,
    )

    return buffer.getvalue()


def resize_max(image, max_dimension):

    width, height = image.size

    largest = max(width, height)

    if largest <= max_dimension:
        return image

    ratio = max_dimension / largest

    new_size = (
        int(width * ratio),
        int(height * ratio),
    )

    return image.resize(
        new_size,
        Image.Resampling.LANCZOS,
    )


# =========================================================
# OPENCV CONVERSION
# =========================================================

def pil_to_cv(image):

    return cv2.cvtColor(
        np.array(image),
        cv2.COLOR_RGB2BGR,
    )


def cv_to_pil(image):

    return Image.fromarray(
        cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB,
        )
    )


# =========================================================
# AUTO CROP
# =========================================================

def auto_crop(image):

    original = pil_to_cv(image)

    height, width = original.shape[:2]

    scale = 1

    if max(height, width) > 1200:

        scale = 1200 / max(height, width)

        small = cv2.resize(
            original,
            (
                int(width * scale),
                int(height * scale),
            ),
        )

    else:

        small = original.copy()

    gray = cv2.cvtColor(
        small,
        cv2.COLOR_BGR2GRAY,
    )

    blur = cv2.GaussianBlur(
        gray,
        (5, 5),
        0,
    )

    edges = cv2.Canny(
        blur,
        50,
        150,
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

    document = None

    image_area = (
        small.shape[0] *
        small.shape[1]
    )

    for contour in contours[:20]:

        perimeter = cv2.arcLength(
            contour,
            True,
        )

        approx = cv2.approxPolyDP(
            contour,
            0.02 * perimeter,
            True,
        )

        area = cv2.contourArea(
            contour
        )

        if (
            len(approx) == 4
            and area > image_area * 0.15
        ):

            document = approx.reshape(
                4,
                2,
            )

            break

    if document is None:
        return image

    document = document / scale

    result = np.zeros(
        (4, 2),
        dtype=np.float32,
    )

    sums = document.sum(axis=1)

    differences = np.diff(
        document,
        axis=1,
    ).reshape(-1)

    result[0] = document[
        np.argmin(sums)
    ]

    result[2] = document[
        np.argmax(sums)
    ]

    result[1] = document[
        np.argmin(differences)
    ]

    result[3] = document[
        np.argmax(differences)
    ]

    top_left = result[0]
    top_right = result[1]
    bottom_right = result[2]
    bottom_left = result[3]

    width1 = np.linalg.norm(
        bottom_right - bottom_left
    )

    width2 = np.linalg.norm(
        top_right - top_left
    )

    height1 = np.linalg.norm(
        top_right - bottom_right
    )

    height2 = np.linalg.norm(
        top_left - bottom_left
    )

    max_width = int(
        max(width1, width2)
    )

    max_height = int(
        max(height1, height2)
    )

    if max_width < 10 or max_height < 10:
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
        result,
        destination,
    )

    corrected = cv2.warpPerspective(
        original,
        matrix,
        (
            max_width,
            max_height,
        ),
    )

    return cv_to_pil(corrected)


# =========================================================
# SCAN FILTERS
# =========================================================

def apply_filter(
    image,
    filter_name,
    strength=50,
):

    cv = pil_to_cv(image)

    gray = cv2.cvtColor(
        cv,
        cv2.COLOR_BGR2GRAY,
    )

    if filter_name == "Original":
        return image

    if filter_name == "Gray":

        return Image.fromarray(
            gray
        ).convert("RGB")

    if filter_name == "B&W":

        blurred = cv2.GaussianBlur(
            gray,
            (3, 3),
            0,
        )

        _, result = cv2.threshold(
            blurred,
            0,
            255,
            cv2.THRESH_BINARY
            + cv2.THRESH_OTSU,
        )

        return Image.fromarray(
            result
        ).convert("RGB")

    if filter_name == "Document":

        denoised = cv2.fastNlMeansDenoising(
            gray,
            None,
            10,
            7,
            21,
        )

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8),
        )

        contrast = clahe.apply(
            denoised
        )

        result = cv2.adaptiveThreshold(
            contrast,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11,
        )

        return Image.fromarray(
            result
        ).convert("RGB")

    if filter_name == "Enhance":

        result = ImageEnhance.Contrast(
            image
        ).enhance(
            1 + strength / 100
        )

        result = ImageEnhance.Sharpness(
            result
        ).enhance(
            1 + strength / 100
        )

        return result

    return image


# =========================================================
# IMAGE TO PDF
# =========================================================

def images_to_pdf(
    images,
    page_size="A4",
    quality=85,
):

    pdf = pymupdf.open()

    for image in images:

        image = image.convert(
            "RGB"
        )

        width, height = image.size

        if page_size == "A4":

            page_width = 595
            page_height = 842

            margin = 20

            scale = min(
                (page_width - 2 * margin)
                / width,

                (page_height - 2 * margin)
                / height,
            )

            display_width = width * scale
            display_height = height * scale

            rect = pymupdf.Rect(
                (page_width - display_width) / 2,
                (page_height - display_height) / 2,
                (page_width + display_width) / 2,
                (page_height + display_height) / 2,
            )

            page = pdf.new_page(
                width=page_width,
                height=page_height,
            )

        else:

            rect = pymupdf.Rect(
                0,
                0,
                width * 72 / 96,
                height * 72 / 96,
            )

            page = pdf.new_page(
                width=rect.width,
                height=rect.height,
            )

        image_data = image_to_jpeg(
            image,
            quality,
        )

        page.insert_image(
            rect,
            stream=image_data,
        )

    result = pdf.tobytes(
        garbage=4,
        deflate=True,
    )

    pdf.close()

    return result


# =========================================================
# PDF TO IMAGE
# =========================================================

def pdf_to_images(
    pdf_bytes,
    dpi=150,
):

    document = pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf",
    )

    results = []

    for index, page in enumerate(
        document
    ):

        pixmap = page.get_pixmap(
            dpi=dpi,
            alpha=False,
        )

        image_data = pixmap.tobytes(
            "png"
        )

        results.append(
            (
                f"page_{index + 1}.png",
                image_data,
            )
        )

    document.close()

    return results


# =========================================================
# ZIP
# =========================================================

def create_zip(files):

    buffer = io.BytesIO()

    with zipfile.ZipFile(
        buffer,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as archive:

        for filename, data in files:

            archive.writestr(
                filename,
                data,
            )

    return buffer.getvalue()


# =========================================================
# PHOTO COMPRESSION
# =========================================================

def compress_photo(
    image,
    target_kb,
    max_dimension,
):

    image = resize_max(
        image,
        max_dimension,
    )

    low = 20
    high = 95

    best = None

    for _ in range(10):

        quality = (
            low + high
        ) // 2

        data = image_to_jpeg(
            image,
            quality,
        )

        if len(data) <= target_kb * 1024:

            best = data
            low = quality + 1

        else:

            high = quality - 1

    if best is not None:
        return best

    current = image

    for _ in range(8):

        current = resize_max(
            current,
            int(
                max(current.size)
                * 0.85
            ),
        )

        data = image_to_jpeg(
            current,
            55,
        )

        if len(data) <= target_kb * 1024:
            return data

    return image_to_jpeg(
        current,
        35,
    )


# =========================================================
# PDF HELPERS — BATCH 2
# =========================================================

def open_pdf(pdf_bytes):
    return pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf",
    )


def pdf_page_count(pdf_bytes):

    document = open_pdf(pdf_bytes)

    count = len(document)

    document.close()

    return count


def pdf_size_kb(pdf_bytes):
    return len(pdf_bytes) / 1024


# =========================================================
# PDF MERGE
# =========================================================

def merge_pdfs(pdf_files):

    output = pymupdf.open()

    for pdf_bytes in pdf_files:

        source = open_pdf(pdf_bytes)

        output.insert_pdf(
            source
        )

        source.close()

    result = output.tobytes(
        garbage=4,
        deflate=True,
    )

    output.close()

    return result


# =========================================================
# PDF COMPRESS
# =========================================================

def compress_pdf(pdf_bytes):

    document = open_pdf(pdf_bytes)

    result = document.tobytes(
        garbage=4,
        deflate=True,
        clean=True,
    )

    document.close()

    return result


# =========================================================
# PDF SPLIT
# =========================================================

def split_pdf(
    pdf_bytes,
    start_page,
    end_page,
):

    source = open_pdf(pdf_bytes)

    output = pymupdf.open()

    output.insert_pdf(
        source,
        from_page=start_page,
        to_page=end_page,
    )

    result = output.tobytes(
        garbage=4,
        deflate=True,
    )

    output.close()
    source.close()

    return result


# =========================================================
# PDF DELETE PAGES
# =========================================================

def delete_pdf_pages(
    pdf_bytes,
    pages_to_delete,
):

    document = open_pdf(pdf_bytes)

    for page_index in sorted(
        pages_to_delete,
        reverse=True,
    ):

        if (
            0 <= page_index
            < len(document)
        ):
            document.delete_page(
                page_index
            )

    if len(document) == 0:

        document.close()

        return None

    result = document.tobytes(
        garbage=4,
        deflate=True,
    )

    document.close()

    return result


# =========================================================
# PDF REORDER PAGES
# =========================================================

def reorder_pdf_pages(
    pdf_bytes,
    new_order,
):

    source = open_pdf(pdf_bytes)

    output = pymupdf.open()

    output.insert_pdf(
        source,
        from_page=0,
        to_page=-1,
        final=0,
    )

    # Remove all pages from temporary
    # document, then insert pages in
    # requested order.
    output.delete_pages(
        range(len(output))
    )

    for page_index in new_order:

        output.insert_pdf(
            source,
            from_page=page_index,
            to_page=page_index,
        )

    result = output.tobytes(
        garbage=4,
        deflate=True,
    )

    output.close()
    source.close()

    return result


# =========================================================
# PDF ROTATE
# =========================================================

def rotate_pdf_pages(
    pdf_bytes,
    rotation,
    selected_pages=None,
):

    document = open_pdf(pdf_bytes)

    if selected_pages is None:

        selected_pages = list(
            range(len(document))
        )

    for page_index in selected_pages:

        if (
            0 <= page_index
            < len(document)
        ):

            page = document[
                page_index
            ]

            page.set_rotation(
                (
                    page.rotation
                    + rotation
                ) % 360
            )

    result = document.tobytes(
        garbage=4,
        deflate=True,
    )

    document.close()

    return result


# =========================================================
# HEADER
# =========================================================

st.title(
    "📄 Smart Document & Image Toolkit"
)

st.caption(
    "Image → PDF • PDF Tools • PDF → Image • "
    "Scan • Auto Crop • Compress"
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.subheader("Select Tool")

    tool = st.radio(
        "",
        [
            "Image → PDF",
            "PDF Tools",
            "PDF → Image",
            "Scan Anything",
            "Compress Photo",
        ],
    )


# =========================================================
# IMAGE TO PDF
# =========================================================

if tool == "Image → PDF":

    st.header(
        "Image → PDF"
    )

    files = st.file_uploader(
        "Upload images",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
        ],
        accept_multiple_files=True,
    )

    page_size = st.selectbox(
        "Page Size",
        [
            "A4",
            "Original",
        ],
    )

    quality = st.slider(
        "Image Quality",
        50,
        95,
        85,
    )

    if files:

        images = [
            bytes_to_image(
                file.getvalue()
            )
            for file in files
        ]

        st.success(
            f"{len(images)} image(s) selected."
        )

        st.image(
            images[0],
            caption="Preview",
            use_container_width=True,
        )

        if len(images) > 1:

            st.caption(
                f"{len(images)} images will become "
                f"{len(images)} PDF pages."
            )

        if st.button(
            "Create PDF",
            type="primary",
            use_container_width=True,
        ):

            pdf = images_to_pdf(
                images,
                page_size,
                quality,
            )

            st.success(
                f"PDF created: {len(images)} page(s)"
            )

            st.download_button(
                "Download PDF",
                pdf,
                "images.pdf",
                "application/pdf",
                use_container_width=True,
            )


# =========================================================
# PDF TOOLS — BATCH 2
# =========================================================

elif tool == "PDF Tools":

    st.header(
        "PDF Tools"
    )

    operation = st.selectbox(
        "Choose PDF operation",
        [
            "Merge PDF",
            "Compress PDF",
            "Split PDF",
            "Delete PDF Pages",
            "Reorder PDF Pages",
            "Rotate PDF",
        ],
    )


    # =====================================================
    # PDF MERGE
    # =====================================================

    if operation == "Merge PDF":

        st.subheader(
            "Merge PDF"
        )

        files = st.file_uploader(
            "Upload PDF files in the order you want to merge",
            type=["pdf"],
            accept_multiple_files=True,
            key="merge_pdf_uploader",
        )

        if files:

            st.success(
                f"{len(files)} PDF file(s) selected."
            )

            for index, file in enumerate(
                files,
                start=1,
            ):

                page_count = pdf_page_count(
                    file.getvalue()
                )

                st.caption(
                    f"{index}. {file.name} — "
                    f"{page_count} page(s)"
                )

            if len(files) < 2:

                st.info(
                    "Select at least 2 PDF files to merge."
                )

            else:

                if st.button(
                    "Merge PDFs",
                    type="primary",
                    use_container_width=True,
                ):

                    pdf_files = [
                        file.getvalue()
                        for file in files
                    ]

                    merged = merge_pdfs(
                        pdf_files
                    )

                    st.success(
                        f"Merged {len(files)} PDF files "
                        f"into one PDF."
                    )

                    st.download_button(
                        "Download Merged PDF",
                        merged,
                        "merged.pdf",
                        "application/pdf",
                        use_container_width=True,
                    )


    # =====================================================
    # PDF COMPRESS
    # =====================================================

    elif operation == "Compress PDF":

        st.subheader(
            "Compress PDF"
        )

        file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            key="compress_pdf_uploader",
        )

        if file:

            original = file.getvalue()

            original_size = pdf_size_kb(
                original
            )

            st.info(
                f"Original size: "
                f"{original_size:.1f} KB"
            )

            if st.button(
                "Compress PDF",
                type="primary",
                use_container_width=True,
            ):

                compressed = compress_pdf(
                    original
                )

                compressed_size = pdf_size_kb(
                    compressed
                )

                reduction = 0

                if original_size > 0:

                    reduction = (
                        (
                            original_size
                            - compressed_size
                        )
                        / original_size
                    ) * 100

                if compressed_size < original_size:

                    st.success(
                        f"Compressed: "
                        f"{compressed_size:.1f} KB "
                        f"({reduction:.1f}% smaller)"
                    )

                else:

                    st.warning(
                        "This PDF could not be made smaller "
                        "with lossless compression."
                    )

                st.download_button(
                    "Download Compressed PDF",
                    compressed,
                    "compressed.pdf",
                    "application/pdf",
                    use_container_width=True,
                )


    # =====================================================
    # PDF SPLIT
    # =====================================================

    elif operation == "Split PDF":

        st.subheader(
            "Split PDF"
        )

        file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            key="split_pdf_uploader",
        )

        if file:

            pdf_bytes = file.getvalue()

            page_count = pdf_page_count(
                pdf_bytes
            )

            st.info(
                f"Total pages: {page_count}"
            )

            if page_count == 1:

                st.warning(
                    "A one-page PDF cannot be split into multiple parts."
                )

            else:

                start_page = st.number_input(
                    "Start page",
                    min_value=1,
                    max_value=page_count,
                    value=1,
                    step=1,
                )

                end_page = st.number_input(
                    "End page",
                    min_value=1,
                    max_value=page_count,
                    value=page_count,
                    step=1,
                )

                if start_page > end_page:

                    st.error(
                        "Start page must be less than or equal to end page."
                    )

                else:

                    selected_count = (
                        end_page
                        - start_page
                        + 1
                    )

                    st.caption(
                        f"Selected pages: "
                        f"{start_page}–{end_page} "
                        f"({selected_count} page(s))"
                    )

                    if st.button(
                        "Split PDF",
                        type="primary",
                        use_container_width=True,
                    ):

                        result = split_pdf(
                            pdf_bytes,
                            start_page - 1,
                            end_page - 1,
                        )

                        st.success(
                            f"Created PDF with "
                            f"{selected_count} page(s)."
                        )

                        st.download_button(
                            "Download Split PDF",
                            result,
                            "split.pdf",
                            "application/pdf",
                            use_container_width=True,
                        )


    # =====================================================
    # DELETE PDF PAGES
    # =====================================================

    elif operation == "Delete PDF Pages":

        st.subheader(
            "Delete PDF Pages"
        )

        file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            key="delete_pdf_uploader",
        )

        if file:

            pdf_bytes = file.getvalue()

            page_count = pdf_page_count(
                pdf_bytes
            )

            st.info(
                f"Total pages: {page_count}"
            )

            page_options = list(
                range(
                    1,
                    page_count + 1,
                )
            )

            pages_to_delete = st.multiselect(
                "Select pages to delete",
                page_options,
                format_func=lambda x:
                    f"Page {x}",
                key="pages_to_delete",
            )

            if pages_to_delete:

                remaining = (
                    page_count
                    - len(pages_to_delete)
                )

                st.warning(
                    f"{len(pages_to_delete)} page(s) "
                    f"will be deleted. "
                    f"{remaining} page(s) will remain."
                )

                if remaining == 0:

                    st.error(
                        "You cannot delete all pages."
                    )

                else:

                    if st.button(
                        "Delete Selected Pages",
                        type="primary",
                        use_container_width=True,
                    ):

                        zero_based_pages = [
                            page - 1
                            for page in pages_to_delete
                        ]

                        result = delete_pdf_pages(
                            pdf_bytes,
                            zero_based_pages,
                        )

                        if result is not None:

                            st.success(
                                f"Deleted "
                                f"{len(pages_to_delete)} page(s)."
                            )

                            st.download_button(
                                "Download Updated PDF",
                                result,
                                "pages_deleted.pdf",
                                "application/pdf",
                                use_container_width=True,
                            )


    # =====================================================
    # REORDER PDF PAGES
    # =====================================================

    elif operation == "Reorder PDF Pages":

        st.subheader(
            "Reorder PDF Pages"
        )

        file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            key="reorder_pdf_uploader",
        )

        if file:

            pdf_bytes = file.getvalue()

            page_count = pdf_page_count(
                pdf_bytes
            )

            st.info(
                f"Total pages: {page_count}"
            )

            if page_count < 2:

                st.warning(
                    "At least 2 pages are needed for reordering."
                )

            else:

                default_order = [
                    str(i)
                    for i in range(
                        1,
                        page_count + 1,
                    )
                ]

                order = st.multiselect(
                    "Select pages in the new order",
                    options=default_order,
                    default=default_order,
                    format_func=lambda x:
                        f"Page {x}",
                    key="reorder_pages",
                )

                if len(order) != page_count:

                    st.warning(
                        "Please include every page exactly once "
                        "in the new order."
                    )

                else:

                    st.caption(
                        "New order: "
                        + " → ".join(
                            f"Page {x}"
                            for x in order
                        )
                    )

                    if st.button(
                        "Reorder Pages",
                        type="primary",
                        use_container_width=True,
                    ):

                        new_order = [
                            int(page) - 1
                            for page in order
                        ]

                        result = reorder_pdf_pages(
                            pdf_bytes,
                            new_order,
                        )

                        st.success(
                            "PDF pages reordered successfully."
                        )

                        st.download_button(
                            "Download Reordered PDF",
                            result,
                            "reordered.pdf",
                            "application/pdf",
                            use_container_width=True,
                        )


    # =====================================================
    # ROTATE PDF
    # =====================================================

    elif operation == "Rotate PDF":

        st.subheader(
            "Rotate PDF"
        )

        file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            key="rotate_pdf_uploader",
        )

        if file:

            pdf_bytes = file.getvalue()

            page_count = pdf_page_count(
                pdf_bytes
            )

            st.info(
                f"Total pages: {page_count}"
            )

            rotation = st.selectbox(
                "Rotation",
                [
                    ("90° clockwise", 90),
                    ("180°", 180),
                    ("270° clockwise", 270),
                ],
                format_func=lambda x:
                    x[0],
            )

            page_mode = st.radio(
                "Apply rotation to",
                [
                    "All pages",
                    "Selected pages",
                ],
            )

            selected_pages = None

            if page_mode == "Selected pages":

                page_options = list(
                    range(
                        1,
                        page_count + 1,
                    )
                )

                selected = st.multiselect(
                    "Select pages",
                    page_options,
                    format_func=lambda x:
                        f"Page {x}",
                    key="rotate_pages",
                )

                if not selected:

                    st.warning(
                        "Select at least one page."
                    )

                else:

                    selected_pages = [
                        page - 1
                        for page in selected
                    ]

            can_rotate = (
                page_mode == "All pages"
                or (
                    selected_pages is not None
                    and len(selected_pages) > 0
                )
            )

            if can_rotate:

                if st.button(
                    "Rotate PDF",
                    type="primary",
                    use_container_width=True,
                ):

                    result = rotate_pdf_pages(
                        pdf_bytes,
                        rotation[1],
                        selected_pages,
                    )

                    st.success(
                        "PDF pages rotated successfully."
                    )

                    st.download_button(
                        "Download Rotated PDF",
                        result,
                        "rotated.pdf",
                        "application/pdf",
                        use_container_width=True,
                    )


# =========================================================
# PDF TO IMAGE
# =========================================================

elif tool == "PDF → Image":

    st.header(
        "PDF → Image"
    )

    file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
    )

    dpi = st.select_slider(
        "DPI",
        options=[
            96,
            120,
            150,
            200,
            250,
            300,
        ],
        value=150,
    )

    if file:

        if st.button(
            "Convert PDF",
            type="primary",
            use_container_width=True,
        ):

            pages = pdf_to_images(
                file.getvalue(),
                dpi,
            )

            st.success(
                f"{len(pages)} page(s) converted."
            )

            for name, data in pages[:3]:

                st.image(
                    data,
                    caption=name,
                    use_container_width=True,
                )

            if len(pages) == 1:

                st.download_button(
                    "Download Image",
                    pages[0][1],
                    pages[0][0],
                    "image/png",
                    use_container_width=True,
                )

            else:

                zip_data = create_zip(
                    pages
                )

                st.download_button(
                    "Download All Images ZIP",
                    zip_data,
                    "pdf_pages.zip",
                    "application/zip",
                    use_container_width=True,
                )


# =========================================================
# SCAN ANYTHING
# =========================================================

elif tool == "Scan Anything":

    st.header(
        "Scan Anything"
    )

    file = st.file_uploader(
        "Upload document/photo",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
        ],
    )

    if file:

        original = bytes_to_image(
            file.getvalue()
        )

        auto = st.checkbox(
            "Auto Crop + Perspective Correction",
            value=True,
        )

        filter_name = st.selectbox(
            "Filter",
            [
                "Document",
                "Original",
                "B&W",
                "Gray",
                "Enhance",
            ],
        )

        strength = st.slider(
            "Filter Strength",
            0,
            100,
            50,
        )

        processed = original

        if auto:

            processed = auto_crop(
                processed
            )

        processed = apply_filter(
            processed,
            filter_name,
            strength,
        )

        st.subheader(
            "Before"
        )

        st.image(
            original,
            use_container_width=True,
        )

        st.subheader(
            "After"
        )

        st.image(
            processed,
            use_container_width=True,
        )

        jpg = image_to_jpeg(
            processed,
            92,
        )

        pdf = images_to_pdf(
            [processed],
            "A4",
            92,
        )

        st.download_button(
            "Download JPG",
            jpg,
            "scanned_document.jpg",
            "image/jpeg",
            use_container_width=True,
        )

        st.download_button(
            "Download PDF",
            pdf,
            "scanned_document.pdf",
            "application/pdf",
            use_container_width=True,
        )


# =========================================================
# COMPRESS PHOTO
# =========================================================

elif tool == "Compress Photo":

    st.header(
        "Compress Photo"
    )

    file = st.file_uploader(
        "Upload Photo",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
        ],
    )

    target_kb = st.selectbox(
        "Maximum Target Size",
        [
            20,
            50,
            100,
            200,
            500,
            1000,
        ],
        index=2,
        format_func=lambda x:
            f"{x} KB",
    )

    max_dimension = st.select_slider(
        "Maximum Dimension",
        options=[
            800,
            1000,
            1200,
            1600,
            2000,
            2500,
            3000,
        ],
        value=1600,
    )

    if file:

        original = bytes_to_image(
            file.getvalue()
        )

        original_size = (
            len(file.getvalue())
            / 1024
        )

        st.image(
            original,
            caption=f"Original: {original_size:.1f} KB",
            use_container_width=True,
        )

        if st.button(
            "Compress Photo",
            type="primary",
            use_container_width=True,
        ):

            output = compress_photo(
                original,
                target_kb,
                max_dimension,
            )

            output_size = (
                len(output)
                / 1024
            )

            st.success(
                f"Output size: {output_size:.1f} KB"
            )

            st.download_button(
                "Download Compressed Photo",
                output,
                "compressed_photo.jpg",
                "image/jpeg",
                use_container_width=True,
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Smart Document & Image Toolkit • "
    "Lightweight Streamlit MVP • Batch 2"
)