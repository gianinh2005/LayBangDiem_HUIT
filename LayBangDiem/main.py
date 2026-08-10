from scraper import get_grade_table
from parser import parse_grade_table
from exporter_excel import export_excel
def main():

    try:
        print("=" * 50)
        print("HUIT GRADE EXPORTER")
        print("=" * 50)

        tables = get_grade_table()

        print("Đã lấy được bảng điểm.")

        df = parse_grade_table(
            tables["grade"]
        )

        summary = tables["summary"]

        print(f"Tìm thấy {len(df)} môn học.")

        export_excel(
            df,
            summary
        )

        print("\nHoàn thành!")

    except Exception:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()