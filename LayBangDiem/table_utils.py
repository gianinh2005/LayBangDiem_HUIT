from bs4 import Tag
import re


def html_table_to_matrix(table: Tag):
    """
    Chuyển bảng HTML thành ma trận 2 chiều.
    Xử lý colspan.
    Rowspan chỉ giữ vị trí, không nhân bản dữ liệu
    để tránh lỗi lặp Học kỳ.
    """

    rows = table.find_all("tr")

    matrix = []

    # lưu vị trí rowspan đang chờ
    rowspan_map = {}

    max_cols = 0

    for row in rows:

        result = []

        cells = row.find_all(["td", "th"])

        col = 0

        for cell in cells:

            # bỏ qua vị trí rowspan cũ
            while col in rowspan_map:
                result.append("")
                col += 1

            text = cell.get_text(" ", strip=True)
            if cell.find("div", class_="check"):
                text = "X"

            colspan = int(cell.get("colspan", 1))
            rowspan = int(cell.get("rowspan", 1))

            for i in range(colspan):

                result.append(text)

                # chỉ đánh dấu vị trí,
                # không copy giá trị xuống các dòng sau
                if rowspan > 1:
                    rowspan_map[col] = rowspan - 1

                col += 1


        # giảm rowspan sau mỗi dòng
        remove = []

        for key in rowspan_map:

            rowspan_map[key] -= 1

            if rowspan_map[key] <= 0:
                remove.append(key)

        for key in remove:
            del rowspan_map[key]


        max_cols = max(max_cols, len(result))

        matrix.append(result)


    # chuẩn hóa số cột
    for row in matrix:

        while len(row) < max_cols:
            row.append("")


    return matrix



def is_semester_row(row):

    text = " ".join(row)

    return re.search(
        r"HK\d+\s*\(\d{4}\s*-\s*\d{4}\)",
        text
    ) is not None



def is_summary_row(row):

    text = " ".join(row)

    keywords = [

        "Điểm trung bình",

        "Điểm trung bình học kỳ",

        "Điểm trung bình tích lũy",

        "Tổng số tín chỉ",

        "Xử lý học vụ"

    ]

    return any(
        text.startswith(k)
        for k in keywords
    )



def clean_text(text):

    if text is None:
        return ""

    text = str(text)

    text = text.replace("\xa0", " ")

    text = " ".join(text.split())

    return text.strip()



def clean_matrix(matrix):

    cleaned = []

    for row in matrix:

        cleaned.append(
            [
                clean_text(cell)
                for cell in row
            ]
        )

    return cleaned