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

    /* Main content spacing */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 900px;
    }

    /* Main title */
    h1 {
        font-size: 2rem !important;
        line-height: 1.2 !important;
        margin-bottom: 0.3rem !important;
    }

    /* Section headings */
    h2 {
        font-size: 1.45rem !important;
    }

    h3 {
        font-size: 1.15rem !important;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        width: 100%;
        min-height: 3rem;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 600;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        width: 100%;
    }

    [data-testid="stFileUploaderDropzone"] {
        min-height: 120px;
        border-radius: 12px;
    }

    /* Select boxes / sliders / checkboxes */
    [data-testid="stSelectbox"],
    [data-testid="stSlider"],
    [data-testid="stSelectSlider"],
    [data-testid="stCheckbox"] {
        margin-bottom: 0.6rem;
    }

    /* Images */
    [data-testid="stImage"] img {
        border-radius: 10px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        min-width: 240px;
    }

    /* Mobile */
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

        /* Keep content comfortable for touch */
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
# HEADER
# =========================================================

st.title(
    "📄 Smart Document & Image Toolkit"
)

st.caption(
    "Image → PDF • PDF → Image • Scan • Auto Crop • Compress"
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

        st.image(
            images[0],
            caption="Preview",
            use_container_width=True,
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

            st.download_button(
                "Download PDF",
                pdf,
                "images.pdf",
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

        # Mobile-friendly vertical controls
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

        # Before
        st.subheader(
            "Before"
        )

        st.image(
            original,
            use_container_width=True,
        )

        # After
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
    "Lightweight Streamlit MVP"
)

