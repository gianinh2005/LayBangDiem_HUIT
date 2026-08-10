import re
import pandas as pd

from table_utils import (
    html_table_to_matrix,
    clean_matrix,
    is_semester_row,
    is_summary_row,
)


# ==========================================================
# Xác định header
# ==========================================================
def detect_header_rows(matrix):

    header_rows = []

    found = False

    for row in matrix:

        text = " ".join(row)

        if not found:

            if "STT" in text and ("Mã môn" in text or "Mã môn học" in text):
                found = True

        if found:

            if is_semester_row(row):
                break

            header_rows.append(row)

    return header_rows



# ==========================================================
# Chuẩn hóa tên cột
# ==========================================================
def normalize_header(parts):

    text = " ".join(parts)

    text = re.sub(r"\s+", " ", text).strip()


    mapping = {

        "STT": "STT",

        "Mã môn học": "Mã môn",

        "Mã môn": "Mã môn",

        "Tên môn học": "Tên môn",

        "Tên môn": "Tên môn",

        "Lớp dự kiến": "Lớp",

        "Lớp": "Lớp",

        "Số tín chỉ": "Số TC",

        "Số tín": "Số TC",

        "TB thường kỳ": "TB thường kỳ",

        "Cuối kỳ": "Cuối kỳ",

        "Điểm tổng kết": "Điểm tổng kết",

        "Thang điểm 4": "Thang điểm 4",

        "Điểm chữ": "Điểm chữ",

        "Xếp loại": "Xếp loại",

        "Đạt chuẩn đầu ra": "Chuẩn đầu ra",

        "Chuẩn đầu ra": "Chuẩn đầu ra",

        "Ghi chú": "Ghi chú",

    }


    for key, value in mapping.items():

        if key in text:
            return value


    if "Giữa kỳ" in text:

        nums = re.findall(r"\d+", text)

        return (
            f"Giữa kỳ {nums[-1]}"
            if nums else
            "Giữa kỳ"
        )


    if "Thường xuyên" in text:

        nums = re.findall(r"\d+", text)

        return (
            f"Thường xuyên {nums[-1]}"
            if nums else
            "Thường xuyên"
        )


    if "Tiểu luận" in text:

        nums = re.findall(r"\d+", text)

        return (
            f"Tiểu luận {nums[-1]}"
            if nums else
            "Tiểu luận"
        )


    if text == "Đạt":
        return "Đạt"


    return ""



# ==========================================================
# Ghép header nhiều tầng
# ==========================================================
def build_headers(header_rows):

    if not header_rows:
        raise Exception("Không tìm thấy header.")


    col_count = max(
        len(row)
        for row in header_rows
    )


    result = []


    for c in range(col_count):

        parts = []

        for row in header_rows:

            if c < len(row):

                value = row[c]

                if value and value not in parts:

                    parts.append(value)


        name = normalize_header(parts)

        result.append(name)



    # bỏ cột rỗng
    result = [
        x for x in result
        if x
    ]


    # bỏ trùng tên
    final = []

    for name in result:

        if name in final:

            count = final.count(name) + 1

            final.append(
                f"{name} {count}"
            )

        else:

            final.append(name)


    return final



# ==========================================================
# Tìm dòng dữ liệu
# ==========================================================
def find_data_start(matrix):

    for i, row in enumerate(matrix):

        if is_semester_row(row):

            return i


    raise Exception(
        "Không tìm thấy học kỳ."
    )



# ==========================================================
# Parse
# ==========================================================
def parse_grade_table(table):

    matrix = html_table_to_matrix(table)

    matrix = clean_matrix(matrix)


    header_rows = detect_header_rows(matrix)

    headers = build_headers(header_rows)


    # thêm học kỳ
    headers.insert(
        0,
        "Học kỳ"
    )


    start = find_data_start(matrix)


    data = []

    current_semester = ""


    for row in matrix[start:]:


        if is_semester_row(row):

            current_semester = " ".join(
                x for x in row
                if x
            )

            continue



        if is_summary_row(row):

            continue



        if not any(row):

            continue



        values = [
            current_semester
        ] + row



        values = values[:len(headers)]



        # if data and values[0] == data[-1][0]:

        #     values[0] = ""



        data.append(values)



    # nếu thiếu cột thì thêm rỗng
    for row in data:

        while len(row) < len(headers):

            row.append("")



    df = pd.DataFrame(
        data,
        columns=headers
    )


    # giới hạn đúng bảng HUIT
    keep_columns = [

        "Học kỳ",
        "STT",
        "Mã môn",
        "Tên môn",
        "Lớp",
        "Số TC",

        "Giữa kỳ 1",
        "Giữa kỳ 2",

        "Thường xuyên 1",
        "Thường xuyên 6",
        "Thường xuyên 7",
        "Thường xuyên 8",
        "Thường xuyên 9",

        "Tiểu luận",
        "Tiểu luận 2",

        "TB thường kỳ",

        "Cuối kỳ",

        "Điểm tổng kết",
        "Thang điểm 4",
        "Điểm chữ",
        "Xếp loại",
        "Đạt",
        "Chuẩn đầu ra",
        "Ghi chú",
    ]


    for col in keep_columns:

        if col not in df.columns:

            df[col] = ""


    df = df[keep_columns]


    print(df.head(5).to_string())

    print("\nCOLUMNS:")
    print(df.columns.tolist())


    print("\nDUPLICATE COLUMNS:")
    print(
        df.columns[df.columns.duplicated()].tolist()
    )


    return df