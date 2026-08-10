from playwright.sync_api import sync_playwright

def test_huit_access():
    with sync_playwright() as p:
        # Mở trình duyệt Chrome (hiện giao diện)
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context()
        page = context.new_page()

        print("1. Đang mở trang chủ HUIT...")
        page.goto("https://sinhvien.huit.edu.vn/")

        print("2. Tự động điều hướng sang trang Kết Quả Học Tập...")
        page.goto("https://sinhvien.huit.edu.vn/ket-qua-hoc-tap.html")

        print("\n👉 BẠN HÃY ĐĂNG NHẬP TRÊN TRÌNH DUYỆT VỪA MỞ.")
        input("👉 Sau khi thấy BẢNG ĐIỂM xuất hiện trên màn hình, nhấn ENTER tại đây để kiểm tra: ")

        # Kiểm tra xem có lấy được thẻ table không
        tables = page.locator("table").all()
        print(f"\n==========================================")
        print(f"✅ XÁC NHẬN: Đã tìm thấy {len(tables)} bảng (table) trên trang web!")

        if len(tables) > 0:
            # In thử 3 dòng đầu tiên của bảng điểm để kiểm tra
            first_rows = page.locator("table tr").first.text_content()
            print(f"Dữ liệu mẫu từ bảng: {first_rows.strip()[:100]}...")
            print("=> ĐÃ VÀO WEB VÀ LẤY DỮ LIỆU THÀNH CÔNG!")
        else:
            print("❌ Chưa tìm thấy bảng điểm. Kiểm tra lại xem bạn đã vào đúng trang chứa bảng điểm chưa.")

        print(f"==========================================\n")
        browser.close()

if __name__ == "__main__":
    test_huit_access()