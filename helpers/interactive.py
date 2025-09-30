"""
interactive.py
Module chứa các hàm giao diện tương tác với người dùng
"""

import os
import sys
from .config import *


def get_user_input():
    """Lấy input từ người dùng theo chế độ tương tác"""
    print("=" * 60)
    print("🚀 PIPELINE LÀM SẠCH DỮ LIỆU CỔ PHIẾU")
    print("=" * 60)
    print("Chọn chế độ nhập thông số:")
    print("1. Nhập từng thông số (Interactive)")
    print("2. Sử dụng giá trị mặc định từ config")
    print("3. Sử dụng command line arguments")
    
    while True:
        try:
            choice = input("\nNhập lựa chọn (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return int(choice)
            print("❌ Vui lòng nhập 1, 2 hoặc 3")
        except KeyboardInterrupt:
            print("\n👋 Thoát chương trình.")
            exit(0)


def interactive_input():
    """Nhập thông số theo chế độ tương tác"""
    print("\n📋 NHẬP THÔNG SỐ PIPELINE")
    print("-" * 40)
    
    # Data directory
    print("📁 Thư mục dữ liệu đầu vào:")
    print("   • Chứa các file CSV dữ liệu cổ phiếu (AAPL.csv, GOOGL.csv, ...)")
    print("   • Mỗi file nên có các cột: Date, Open, High, Low, Close, Volume")
    print("   • Có thể là thư mục hoặc file CSV đơn lẻ")
    while True:
        data_dir = input(f"   Nhập đường dẫn [{DEFAULT_DATA_DIR}]: ").strip()
        if not data_dir:
            data_dir = DEFAULT_DATA_DIR
        
        if os.path.exists(data_dir) or data_dir.lower().endswith('.csv'):
            break
        
        print(f"❌ Không tìm thấy đường dẫn: {data_dir}")
        create_dir = input("   Có muốn tạo thư mục này không? (y/n): ").strip().lower()
        if create_dir in ['y', 'yes']:
            try:
                os.makedirs(data_dir, exist_ok=True)
                print(f"✅ Đã tạo thư mục: {data_dir}")
                break
            except Exception as e:
                print(f"❌ Không thể tạo thư mục: {e}")
    
    # Output directory
    print(f"\n📤 Thư mục lưu kết quả:")
    print("   • Nơi lưu các file CSV đã được làm sạch")
    print("   • Kèm file báo cáo JSON chi tiết")
    print("   • Tự động tạo nếu chưa tồn tại")
    out_dir = input(f"   Nhập đường dẫn [{DEFAULT_OUTPUT_DIR}]: ").strip()
    if not out_dir:
        out_dir = DEFAULT_OUTPUT_DIR
    
    # Minimum observations
    print(f"\n📊 Số quan sát (ngày giao dịch) tối thiểu:")
    print("   • Mã cổ phiếu phải có ít nhất bao nhiêu ngày dữ liệu")
    print("   • Lọc bỏ các mã có quá ít dữ liệu (không đáng tin cậy)")
    print("   • Khuyến nghị: 100-252 ngày (4 tháng - 1 năm)")
    print("   • Giá trị cao hơn = chất lượng tốt hơn nhưng ít mã hơn")
    while True:
        try:
            min_obs_input = input(f"   Nhập số ngày tối thiểu [{MIN_OBSERVATIONS}]: ").strip()
            min_obs = int(min_obs_input) if min_obs_input else MIN_OBSERVATIONS
            if min_obs > 0:
                break
            print("❌ Số quan sát phải lớn hơn 0")
        except ValueError:
            print("❌ Vui lòng nhập số nguyên hợp lệ")
    
    # Missing threshold
    print(f"\n🕳️ Ngưỡng dữ liệu thiếu cho phép:")
    print("   • Tỉ lệ dữ liệu thiếu tối đa mà vẫn giữ lại mã cổ phiếu")
    print("   • Ví dụ: 0.3 = chấp nhận thiếu tối đa 30% dữ liệu")
    print("   • Giá trị thấp (0.1-0.2) = chất lượng cao, ít mã hơn")
    print("   • Giá trị cao (0.4-0.5) = nhiều mã hơn, chất lượng thấp hơn")
    while True:
        try:
            missing_input = input(f"   Nhập ngưỡng (0.0-1.0) [{MISSING_THRESHOLD}]: ").strip()
            missing_threshold = float(missing_input) if missing_input else MISSING_THRESHOLD
            if 0 <= missing_threshold <= 1:
                break
            print("❌ Ngưỡng phải từ 0 đến 1")
        except ValueError:
            print("❌ Vui lòng nhập số thực hợp lệ")
    
    # Volume threshold
    print(f"\n📈 Ngưỡng khối lượng giao dịch tối thiểu:")
    print("   • Lọc bỏ các mã có thanh khoản kém (khối lượng giao dịch thấp)")
    print("   • Dựa trên giá trị trung vị (median) của khối lượng")
    print("   • Ví dụ: 100000 = chỉ giữ mã có median volume ≥ 100,000")
    print("   • Để trống = không lọc theo khối lượng")
    vol_input = input(f"   Nhập ngưỡng khối lượng (để trống = không giới hạn): ").strip()
    try:
        volume_threshold = float(vol_input) if vol_input else None
    except ValueError:
        print("❌ Giá trị không hợp lệ, sử dụng mặc định (không giới hạn)")
        volume_threshold = None
    
    # Fill limit
    print(f"\n🔄 Giới hạn điền dữ liệu thiếu (Forward-fill):")
    print("   • Số ngày tối đa được điền dữ liệu từ ngày trước")
    print("   • Khi thiếu dữ liệu ngày nghỉ lễ, sẽ dùng giá ngày gần nhất")
    print("   • Ví dụ: 5 = chỉ điền tối đa 5 ngày liên tiếp")
    print("   • Giá trị 0 = không điền dữ liệu thiếu")
    while True:
        try:
            fill_input = input(f"   Nhập số ngày tối đa [{FILL_LIMIT}]: ").strip()
            fill_limit = int(fill_input) if fill_input else FILL_LIMIT
            if fill_limit >= 0:
                break
            print("❌ Giới hạn fill phải >= 0")
        except ValueError:
            print("❌ Vui lòng nhập số nguyên hợp lệ")
    
    # Combine all data
    print(f"\n🗂️ Chế độ xuất dữ liệu:")
    print("\n   1️⃣ File riêng cho mỗi mã:")
    print("      • AAPL.cleaned.csv, GOOGL.cleaned.csv, ...")
    print("      • + file cleaned_all.csv (tổng hợp tất cả)")
    print("      • Tiện cho phân tích từng mã riêng biệt")
    print("\n   2️⃣ Một file duy nhất:")
    print("      • all_stocks_combined.csv (chứa tất cả)")
    print("      • Có cột stock_id để phân biệt các mã")
    print("      • Tiện cho machine learning, phân tích đa biến")
    
    while True:
        combine_choice = input(f"\n   Chọn chế độ (1-2) [{'2' if COMBINE_ALL_DATA else '1'}]: ").strip()
        if not combine_choice:
            combine_all = COMBINE_ALL_DATA
            break
        elif combine_choice in ['1', '2']:
            combine_all = (combine_choice == '2')
            break
        print("❌ Vui lòng nhập 1 hoặc 2")
    
    # Unique ID format
    print(f"\n🔑 Định dạng mã định danh duy nhất (Unique ID):")
    print("   (Dùng để phân biệt các mã cổ phiếu khi gom chung)")
    
    formats = {
        '1': ('ticker', 'Dùng ký hiệu mã (AAPL, GOOGL) - dễ đọc'),
        '2': ('filename', 'Dùng tên file (AAAU.csv → AAAU) - khuyến nghị'),
        '3': ('index', 'Dùng số thứ tự (0, 1, 2, ...) - tối giản'),
        '4': ('hash', 'Dùng mã hash (4f3b2a1c) - độc đáo')
    }
    
    for key, (value, desc) in formats.items():
        status = " ✅" if value == UNIQUE_ID_FORMAT else ""
        print(f"   {key}. {value}: {desc}{status}")
    
    while True:
        format_choice = input(f"\n   Chọn định dạng (1-4) [{'2' if UNIQUE_ID_FORMAT == 'filename' else '1'}]: ").strip()
        if not format_choice:
            unique_format = UNIQUE_ID_FORMAT
            break
        elif format_choice in formats:
            unique_format = formats[format_choice][0]
            break
        print("❌ Vui lòng nhập 1, 2, 3 hoặc 4")
    
    # Tóm tắt các thiết lập
    print(f"\n📋 TÓM TẮT THIẾT LẬP:")
    print(f"   📁 Dữ liệu từ: {data_dir}")
    print(f"   📤 Kết quả tại: {out_dir}")
    print(f"   📊 Tối thiểu {min_obs} ngày dữ liệu")
    print(f"   🕳️ Chấp nhận thiếu tối đa {missing_threshold*100:.1f}% dữ liệu")
    print(f"   📈 Ngưỡng volume: {volume_threshold or 'Không giới hạn'}")
    print(f"   🔄 Điền tối đa {fill_limit} ngày liên tiếp")
    print(f"   🗂️ {'Gom tất cả vào 1 file' if combine_all else 'File riêng cho mỗi mã'}")
    print(f"   🔑 Định dạng ID: {unique_format}")
    
    return {
        'data_dir': data_dir,
        'out_dir': out_dir,
        'min_observations': min_obs,
        'missing_threshold': missing_threshold,
        'median_volume_threshold': volume_threshold,
        'fill_limit': fill_limit,
        'combine_all_data': combine_all,
        'unique_id_format': unique_format
    }


def use_default_config():
    """Sử dụng giá trị mặc định từ config"""
    print("\n⚙️ Sử dụng cấu hình mặc định từ config.py")
    return {
        'data_dir': DEFAULT_DATA_DIR,
        'out_dir': DEFAULT_OUTPUT_DIR,
        'min_observations': MIN_OBSERVATIONS,
        'missing_threshold': MISSING_THRESHOLD,
        'median_volume_threshold': MEDIAN_VOLUME_THRESHOLD,
        'fill_limit': FILL_LIMIT,
        'combine_all_data': COMBINE_ALL_DATA,
        'unique_id_format': UNIQUE_ID_FORMAT
    }