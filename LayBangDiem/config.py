from pathlib import Path

PDF_FILE = "output/BangDiem_HUIT.pdf"
# URL
LOGIN_URL = "https://sinhvien.huit.edu.vn/"
GRADE_URL = "https://sinhvien.huit.edu.vn/ket-qua-hoc-tap.html"

# Output
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

EXCEL_FILE = OUTPUT_DIR / "BangDiem_HUIT.xlsx"
# PDF_FILE = OUTPUT_DIR / "BangDiem_HUIT.pdf"

# Browser
HEADLESS = False
BROWSER_CHANNEL = "chrome"

# Font PDF
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "arial.ttf"
]