"""
高级文档提取工具模块

支持OCR识别扫描件PDF和图片中的文字。
需要安装: pip install paddlepaddle paddleocr
"""

import os
import tempfile
import uuid
from typing import Optional

# 尝试导入，失败时提供友好的错误信息
try:
    import fitz
except ImportError:
    fitz = None
    print("提示: 请安装 PyMuPDF: pip install pymupdf")

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None
    print("提示: 请安装 PaddleOCR: pip install paddlepaddle paddleocr")


# OCR缓存（避免重复初始化）
_ocr_cache = None
OCR_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "ocr_cache")
TEMP_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "temp")


def get_ocr():
    """单例获取PaddleOCR对象"""
    global _ocr_cache
    if PaddleOCR is None:
        raise ImportError("PaddleOCR未安装，请运行: pip install paddlepaddle paddleocr")

    if _ocr_cache is None:
        # 确保缓存目录存在
        os.makedirs(OCR_CACHE_DIR, exist_ok=True)
        _ocr_cache = PaddleOCR(
            use_angle_cls=True,
            lang="ch",
            rec_model_dir=os.path.join(OCR_CACHE_DIR, "rec_model"),
            det_model_dir=os.path.join(OCR_CACHE_DIR, "det_model"),
            cls_model_dir=os.path.join(OCR_CACHE_DIR, "cls_model"),
        )
    return _ocr_cache


def cleanup_temp_file(file_path: str):
    """清理临时文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass


def save_temp_file(file_storage, suffix: str = "") -> str:
    """保存上传文件到临时目录"""
    os.makedirs(TEMP_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{suffix}"
    file_path = os.path.join(TEMP_DIR, filename)
    file_storage.save(file_path)
    return file_path


def extract_text_with_ocr(image_path: str) -> str | None:
    """使用PaddleOCR从图片提取文字"""
    if PaddleOCR is None:
        raise ImportError("PaddleOCR未安装")

    try:
        ocr = get_ocr()
        result = ocr.ocr(image_path, cls=True)

        if result and result[0]:
            text_lines = []
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0]  # 识别出的文字
                    confidence = line[1][1]  # 置信度
                    if confidence > 0.5:  # 只保留置信度>0.5的结果
                        text_lines.append(text)
            return "\n".join(text_lines)
        return ""
    except Exception as e:
        print(f"OCR识别失败: {e}")
        return None


def extract_text_from_image(image_path: str) -> str | None:
    """从图片文件提取文字（通用接口）"""
    ext = os.path.splitext(image_path)[1].lower()
    supported = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"]

    if ext not in supported:
        return None

    return extract_text_with_ocr(image_path)


def extract_text_from_pdf_with_ocr(pdf_path: str) -> str | None:
    """PDF转图片后OCR识别（扫描件PDF专用）"""
    if fitz is None:
        raise ImportError("PyMuPDF未安装，请运行: pip install pymupdf")

    try:
        ocr = get_ocr()

        text_lines = []
        doc = fitz.open(pdf_path)
        temp_images = []
        page_count = int(getattr(doc, "page_count", 0))

        for page_num in range(page_count):
            page = doc.load_page(page_num)
            # 将PDF页面转为图片
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 提高分辨率
            img_filename = f"ocr_page_{page_num}_{uuid.uuid4().hex}.png"
            img_path = os.path.join(TEMP_DIR, img_filename)
            pix.save(img_path)
            temp_images.append(img_path)

            # OCR识别
            result = ocr.ocr(img_path, cls=True)
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        text_lines.append(line[1][0])

        doc.close()

        # 清理临时图片
        for img_path in temp_images:
            cleanup_temp_file(img_path)

        return "\n".join(map(str, text_lines)).strip()
    except Exception as e:
        print(f"PDF OCR识别失败: {e}")
        return None


def smart_extract_from_pdf(pdf_path: str) -> dict[str, object]:
    """
    智能PDF提取：自动判断是否需要OCR

    Returns:
        {
            'text': str,  # 提取的文本
            'method': str,  # 'text' 或 'ocr'
            'is_scanned': bool  # 是否为扫描件
        }
    """
    if fitz is None:
        raise ImportError("PyMuPDF未安装")

    try:
        # 1. 先尝试直接提取文本（针对文字型PDF）
        doc = fitz.open(pdf_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        text = "".join(map(str, text_parts))

        # 判断是否为扫描件：如果提取的文本少于50字符，认为是扫描件
        if len(text.strip()) > 50:
            return {"text": text.strip(), "method": "text", "is_scanned": False}

        # 2. 扫描件PDF，使用OCR
        print("检测到扫描件PDF，使用OCR识别...")
        ocr_text = extract_text_from_pdf_with_ocr(pdf_path)

        if ocr_text:
            return {"text": ocr_text, "method": "ocr", "is_scanned": True}

        # OCR也失败了
        return {
            "text": text.strip(),
            "method": "text" if text.strip() else "failed",
            "is_scanned": True,
        }

    except Exception as e:
        print(f"智能PDF提取失败: {e}")
        return {"text": None, "method": "failed", "is_scanned": False}


def smart_extract_from_upload(file_storage) -> dict[str, object]:
    """
    智能提取：自动判断文件类型和提取方式

    Args:
        file_storage: Flask上传文件对象

    Returns:
        {
            'text': str,  # 提取的文本
            'method': str,  # 'text' / 'ocr' / 'failed' / 'unsupported'
            'is_scanned': bool,  # 是否为扫描件
            'word_count': int  # 字数
        }
    """
    filename = file_storage.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if not ext:
        return {
            "text": None,
            "method": "unsupported",
            "is_scanned": False,
            "word_count": 0,
        }

    # 支持的图片格式
    image_exts = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"]

    # 保存临时文件处理
    temp_path = None
    try:
        # 根据文件类型选择提取方式
        if ext == ".pdf":
            # 先尝试普通文本提取
            from .document_extract import extract_from_pdf_memory

            file_storage.seek(0)
            text = extract_from_pdf_memory(file_storage)

            if text and len(text.strip()) > 50:
                return {
                    "text": text,
                    "method": "text",
                    "is_scanned": False,
                    "word_count": len(text),
                }

            # 扫描件，使用OCR
            temp_path = save_temp_file(file_storage, ".pdf")
            result = smart_extract_from_pdf(temp_path)
            text_value = result.get("text")
            result["word_count"] = len(text_value) if isinstance(text_value, str) else 0
            return result

        elif ext in [".docx", ".doc"]:
            from .document_extract import extract_from_word_memory

            file_storage.seek(0)
            text = extract_from_word_memory(file_storage)
            return {
                "text": text,
                "method": "text",
                "is_scanned": False,
                "word_count": len(text) if text else 0,
            }

        elif ext in [".txt", ".md"]:
            file_storage.seek(0)
            text = file_storage.read().decode("utf-8").strip()
            return {
                "text": text,
                "method": "text",
                "is_scanned": False,
                "word_count": len(text),
            }

        elif ext in image_exts:
            # 图片直接OCR
            temp_path = save_temp_file(file_storage, ext)
            text = extract_text_from_image(temp_path)
            return {
                "text": text,
                "method": "ocr" if text else "failed",
                "is_scanned": True,
                "word_count": len(text) if text else 0,
            }

        else:
            return {
                "text": None,
                "method": "unsupported",
                "is_scanned": False,
                "word_count": 0,
            }

    except Exception as e:
        print(f"文档提取失败: {e}")
        return {"text": None, "method": "failed", "is_scanned": False, "word_count": 0}
    finally:
        # 清理临时文件
        if temp_path:
            cleanup_temp_file(temp_path)


def get_ocr_status_label(method: str) -> str:
    """获取提取方式的显示标签"""
    labels = {
        "text": "文本提取",
        "ocr": "OCR识别",
        "failed": "提取失败",
        "unsupported": "不支持",
        "pending": "待处理",
    }
    return labels.get(method, "未知")


if __name__ == "__main__":
    # 测试
    import sys

    if len(sys.argv) > 1:
        # 模拟文件上传测试
        class MockFile:
            def __init__(self, path):
                self.path = path
                self.filename = os.path.basename(path)

            def save(self, p):
                import shutil

                shutil.copy(self.path, p)

            def read(self, n=-1):
                with open(self.path, "rb") as f:
                    return f.read()

            def seek(self, n=0):
                pass

        mock_file = MockFile(sys.argv[1])
        result = smart_extract_from_upload(mock_file)
        print(f"提取方式: {result.get('method')}")
        print(f"是否为扫描件: {result.get('is_scanned')}")
        print(f"字数: {result.get('word_count')}")
        text_value = result.get("text")
        if isinstance(text_value, str) and text_value:
            preview = text_value[:200]
            print(f"预览: {preview}...")
        else:
            print("无文本内容")
