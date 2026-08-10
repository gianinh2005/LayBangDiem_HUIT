from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from config import LOGIN_URL
from config import GRADE_URL
from config import HEADLESS
from config import BROWSER_CHANNEL

def get_grade_table():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=HEADLESS,
            channel=BROWSER_CHANNEL
        )

        context = browser.new_context()

        page = context.new_page()

        print("Mở website...")

        page.goto(LOGIN_URL)

        page.goto(GRADE_URL)

        input(
            "\nĐăng nhập.\n"
            "Mở trang Kết quả học tập.\n"
            "Khi bảng điểm hiện đầy đủ nhấn ENTER..."
        )

        page.wait_for_selector("table", timeout=60000)

        soup = BeautifulSoup(
            page.content(),
            "html.parser"
        )

        browser.close()


        tables = soup.find_all("table")


        grade_table = None
        summary_table = None


        for table in tables:

            txt = table.get_text(" ", strip=True)


            if "Mã môn học" in txt:

                grade_table = table


            if "Tổng tín chỉ" in txt and "Trung bình chung tích luỹ" in txt:

                summary_table = table



        if grade_table is None:

            raise Exception(
                "Không tìm thấy bảng điểm"
            )


        return {
            "grade": grade_table,
            "summary": summary_table
        }

# def get_grade_table():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=HEADLESS,
            channel=BROWSER_CHANNEL
        )

        context = browser.new_context()

        page = context.new_page()

        print("Mở website...")

        page.goto(LOGIN_URL)

        page.goto(GRADE_URL)

        input(
            "\nĐăng nhập.\n"
            "Mở trang Kết quả học tập.\n"
            "Khi bảng điểm hiện đầy đủ nhấn ENTER..."
        )

        page.wait_for_selector("table")

        soup = BeautifulSoup(page.content(), "html.parser")

        browser.close()

        tables = soup.find_all("table")

        if not tables:
            raise Exception("Không tìm thấy bảng.")

        for table in tables:

            txt = table.get_text()

            if "Mã môn học" in txt:

                with open("debug_table.html", "w", encoding="utf-8") as f:
                    f.write(str(table))

                return table

        return tables[-1]