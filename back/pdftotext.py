import fitz  # pymupdf
from PIL import Image
import pytesseract
import io

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


# def 띄어쓰기복구?():
#     라이브러리있는듯


def pdf_to_text_with_ocr(pdf_bytes, lang='eng+kor'):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text").strip()
        blocks = page.get_text("blocks")
        image_blocks = [b for b in blocks if b[6] == 1]

        if len(image_blocks) == 0 and len(text) > 10:
            full_text.append(text)
        else:
            pix = page.get_pixmap(dpi=500) #dpi 올라갈수록 정확도 올라감. 하지만 느려짐
            img_bytes = pix.tobytes(output="png")
            img = Image.open(io.BytesIO(img_bytes))
            ocr_text = pytesseract.image_to_string(img, lang=lang)
            full_text.append(ocr_text)

    doc.close()
    for i in range(len(full_text)):
        full_text[i] = clean_ocr_text(full_text[i])
    return "\n\n".join(full_text)