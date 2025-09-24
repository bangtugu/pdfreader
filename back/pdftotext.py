import fitz  # pymupdf
from PIL import Image
import pytesseract
import io
import numpy as np
import cv2

# https://drpepper3.tistory.com/17 참고
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


def clean_ocr_text(raw_text):
    import re
    # 한글 사이 띄어쓰기 없애기 (예: '묘 구 사 항' → '묘구사항')
    raw_text = re.sub(r'(?<=[가-힣])\s(?=[가-힣])', '', raw_text)
    # 반복된 줄바꿈 및 공백 정리
    raw_text = re.sub(r'\n+', '\n', raw_text)
    raw_text = re.sub(r'[ ]{2,}', ' ', raw_text)
    return raw_text.strip()


# def 불필요문자제거():
#     pass


# def 띄어쓰기복구?():
#     pass


def pdf_to_text_with_ocr(pdf_bytes, lang='eng+kor'):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = []

    # 경계선 강조용 커널
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text").strip()
        blocks = page.get_text("blocks")    
        image_blocks = [b for b in blocks if b[6] == 1]

        # 이미지 없고 텍스트가 충분히 있으면 텍스트 그대로 사용
        if len(image_blocks) == 0 and len(text) > 10:
            full_text.append(text)
        else:
            # 페이지 전체를 이미지로 변환
            pix = page.get_pixmap(dpi=500)
            img_bytes = pix.tobytes(output="png")
            pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            target_img = pil_img

            # # PIL 이미지 → OpenCV 이미지 (NumPy 배열)
            # cv_img = np.array(pil_img)
            # cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
            
            # # 전처리: 그레이스케일, 노이즈 제거, 샤프닝
            # gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            # denoised = cv2.medianBlur(gray, 3)
            # sharpened = cv2.filter2D(denoised, -1, kernel)
            # target_img = sharpened

            # OCR 수행
            ocr_text = pytesseract.image_to_string(target_img, lang=lang)
            full_text.append(ocr_text)

    doc.close()

    # 텍스트 후처리
    for i in range(len(full_text)):
        full_text[i] = clean_ocr_text(full_text[i])

    return "\n\n".join(full_text)