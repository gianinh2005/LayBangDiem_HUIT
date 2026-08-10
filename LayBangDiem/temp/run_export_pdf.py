import os
import pandas as pd
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==========================================
# 1. THUẬT TOÁN BÓC TÁCH BẢNG ĐIỂM CHUẨN HUIT
# ==========================================
def scrape_and_parse_huit():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context()
        page = context.new_page()

        print("1. Đang mở trang web HUIT...")
        page.goto("https://sinhvien.huit.edu.vn/")
        page.goto("https://sinhvien.huit.edu.vn/ket-qua-hoc-tap.html")

        print("\n👉 Hãy đăng nhập và chuyển tới trang KẾT QUẢ HỌC TẬP.")
        input("👉 Khi bảng điểm môn học đã hiển thị, nhấn ENTER tại đây để cào: ")

        page.wait_for_selector("table")
        soup = BeautifulSoup(page.content(), 'html.parser')
        browser.close()

        tables = soup.find_all('table')
        if not tables:
            print("❌ Không tìm thấy bảng nào!")
            return None

        # Tìm bảng điểm môn học (chứa thông tin điểm chi tiết)
        target_table = None
        for table in tables:
            t_text = table.get_text()
            if "Mã môn học" in t_text or "Số tín chỉ" in t_text or "Thường xuyên" in t_text:
                target_table = table
                break
        if not target_table:
            target_table = tables[-1]

        rows = target_table.find_all('tr')

        # ----------------------------------------------------
        # BƯỚC A: TÌM CÁC DÒNG HEADER CHÍNH THỨC (TRƯỚC HK1)
        # ----------------------------------------------------
        header_rows = []
        data_start_idx = 0
        for idx, row in enumerate(rows):
            r_text = row.get_text(strip=True)
            # Ngừng thu thập Header khi gặp dòng Học kỳ đầu tiên (VD: HK1 (2023 - 2024))
            if "HK" in r_text and ("20" in r_text or "-" in r_text):
                data_start_idx = idx
                break
            header_rows.append(row)

        if not header_rows:
            header_rows = rows[:2]
            data_start_idx = 2

        # Xác định số cột
        num_cols = max(sum(int(cell.get('colspan', 1)) for cell in r.find_all(['td', 'th'])) for r in rows)

        # Bóc tách Header sạch
        h_matrix = [[None for _ in range(num_cols)] for _ in range(len(header_rows))]
        for r_idx, row in enumerate(header_rows):
            c_idx = 0
            for cell in row.find_all(['td', 'th']):
                while c_idx < num_cols and h_matrix[r_idx][c_idx] is not None:
                    c_idx += 1
                if c_idx >= num_cols: break
                text = cell.get_text(strip=True)
                rowspan, colspan = int(cell.get('rowspan', 1)), int(cell.get('colspan', 1))
                for r_off in range(rowspan):
                    for c_off in range(colspan):
                        if r_idx + r_off < len(header_rows) and c_idx + c_off < num_cols:
                            h_matrix[r_idx + r_off][c_idx + c_off] = text
                c_idx += colspan

        clean_headers = []
        for col_idx in range(num_cols):
            parts = [h_matrix[r][col_idx] for r in range(len(header_rows)) if h_matrix[r][col_idx]]
            unique_parts = list(dict.fromkeys(parts))
            h_name = " ".join(unique_parts).strip()
            clean_headers.append(h_name if h_name else f"Cột {col_idx+1}")

        # Đặt cột "Học kỳ" lên đầu tiên
        final_headers = ["Học kỳ"] + clean_headers

        # ----------------------------------------------------
        # BƯỚC B: BÓC TÁCH DỮ LIỆU CÁC MÔN HỌC THEO HỌC KỲ
        # ----------------------------------------------------
        parsed_data = []
        current_hk = "Khác"

        for r_idx in range(data_start_idx, len(rows)):
            row = rows[r_idx]
            cells = row.find_all(['td', 'th'])
            row_text = row.get_text(strip=True)

            if not row_text:
                continue

            # Nếu là dòng Tiêu đề Học Kỳ (như HK1 (2023 - 2024))
            if "HK" in row_text and ("20" in row_text or "-" in row_text) and len(cells) <= 3:
                current_hk = row_text
                continue

            # Lấy dữ liệu từng cell của dòng môn học
            row_vals = [current_hk]
            for cell in cells:
                row_vals.append(cell.get_text(strip=True))

            # Bỏ qua các dòng tổng kết / điểm trung bình tích lũy nếu muốn, hoặc căn chuẩn cột
            if len(row_vals) > 1:
                # Padding cho đủ số cột
                while len(row_vals) < len(final_headers):
                    row_vals.append("")
                parsed_data.append(row_vals[:len(final_headers)])

        df = pd.DataFrame(parsed_data, columns=final_headers)

        # Bỏ các cột hoàn toàn trống
        df = df.dropna(how='all', axis=1)

        print(f"🎉 Đã bóc tách thành công {len(df)} môn học với Header sạch vẽ!")
        return df

# ==========================================
# 2. XUẤT RA EXCEL VÀ PDF
# ==========================================
def export_files(df):
    if df is None or df.empty:
        print("❌ Không có dữ liệu để xuất!")
        return

    # 1. File Excel
    excel_name = "BangDiem_HUIT_Chuan.xlsx"
    df.to_excel(excel_name, index=False)
    print(f"🎉 ĐÃ XUẤT FILE EXCEL: {excel_name}")

    # 2. File PDF
    pdf_filename = "BangDiem_HUIT_Chuan.pdf"
    font_name = 'Helvetica'
    possible_fonts = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf", "arial.ttf"]
    for fp in possible_fonts:
        if os.path.exists(fp):
            pdfmetrics.registerFont(TTFont('VietnameseFont', fp))
            font_name = 'VietnameseFont'
            break

    page_width, page_height = landscape(letter)
    avail_width = page_width - 20
    col_count = len(df.columns)
    col_width = avail_width / col_count

    doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(letter), rightMargin=10, leftMargin=10, topMargin=15, bottomMargin=15)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName=font_name, fontSize=13, alignment=1, spaceAfter=8)
    header_style = ParagraphStyle('HeaderStyle', fontName=font_name, fontSize=5, leading=6, alignment=1, textColor=colors.whitesmoke)
    cell_style = ParagraphStyle('CellStyle', fontName=font_name, fontSize=5, leading=6, alignment=1)

    elements.append(Paragraph("<b>BẢNG ĐIỂM CHI TIẾT SINH VIÊN HUIT</b>", title_style))
    elements.append(Spacer(1, 4))

    table_data = [[Paragraph(f"<b>{col}</b>", header_style) for col in df.columns]]
    for _, row in df.iterrows():
        table_data.append([Paragraph(str(cell or ''), cell_style) for cell in row])

    table = Table(table_data, colWidths=[col_width] * col_count)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0056B3")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))

    elements.append(table)
    doc.build(elements)
    print(f"🎉 ĐÃ XUẤT FILE PDF SẠCH: {pdf_filename}")

if __name__ == "__main__":
    df_grades = scrape_and_parse_huit()
    if df_grades is not None:
        export_files(df_grades)