import os
import sys
import pandas as pd
import numpy as np
import logging
import argparse
import json
import hashlib
from pathlib import Path
from tqdm import tqdm

# Import các module đã tách
from helpers.config import *
from helpers.utils import *
from helpers.data_cleaner import clean_single_ticker
from helpers.pipeline import pipeline_clean_all
from helpers.interactive import get_user_input, interactive_input, use_default_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def parse_arguments():
    """Phân tích các tham số dòng lệnh với thông điệp tiếng Việt"""
    parser = argparse.ArgumentParser(
        description="🚀 Pipeline làm sạch dữ liệu cổ phiếu - Công cụ xử lý và làm sạch dữ liệu chứng khoán",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
📋 CÁC VÍ DỤ SỬ DỤNG:

1️⃣ Chế độ tự động (sử dụng cấu hình mặc định):
   python main.py --auto

2️⃣ Chế độ tương tác (nhập từng thông số):
   python main.py --interactive

3️⃣ Chỉ định thư mục dữ liệu và đầu ra:
   python main.py --data-dir "./raw_data" --output-dir "./cleaned_data"

4️⃣ Thiết lập ngưỡng chất lượng dữ liệu:
   python main.py --min-obs 100 --missing-threshold 0.2

5️⃣ Lọc theo khối lượng giao dịch:
   python main.py --volume-threshold 50000 --data-dir "./data"

6️⃣ Gộp tất cả dữ liệu vào một file:
   python main.py --combine-all --unique-format filename

7️⃣ Xử lý dữ liệu với thiết lập tùy chỉnh đầy đủ:
   python main.py --data-dir "./stocks" --output-dir "./output" \\
                  --min-obs 200 --missing-threshold 0.1 \\
                  --volume-threshold 100000 --fill-limit 3 \\
                  --combine-all --unique-format hash

💡 MẸO SỬ DỤNG:
- Sử dụng --auto cho xử lý nhanh với cài đặt mặc định
- Sử dụng --interactive để được hướng dẫn từng bước
- Kết hợp nhiều tùy chọn để tùy chỉnh theo nhu cầu
- Kiểm tra file cleaning_report.json để xem kết quả chi tiết
        """
    )
    
    # Các tùy chọn chế độ hoạt động
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--auto', 
        action='store_true',
        help='🤖 Chế độ tự động: Sử dụng cấu hình mặc định từ config.py, không cần nhập thông số'
    )
    mode_group.add_argument(
        '--interactive', 
        action='store_true',
        help='💬 Chế độ tương tác: Hướng dẫn từng bước nhập thông số với giải thích chi tiết'
    )
    
    # Đường dẫn file và thư mục
    parser.add_argument(
        '--data-dir', 
        type=str, 
        default=DEFAULT_DATA_DIR,
        help=f'📁 Đường dẫn thư mục chứa file CSV đầu vào (mặc định: {DEFAULT_DATA_DIR}). '
             'Có thể là thư mục chứa nhiều file CSV hoặc đường dẫn đến một file CSV duy nhất'
    )
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default=DEFAULT_OUTPUT_DIR,
        help=f'📤 Đường dẫn thư mục lưu kết quả (mặc định: {DEFAULT_OUTPUT_DIR}). '
             'Thư mục sẽ được tạo tự động nếu chưa tồn tại'
    )
    
    # Các thiết lập chất lượng dữ liệu
    parser.add_argument(
        '--min-obs', 
        type=int, 
        default=MIN_OBSERVATIONS,
        help=f'📊 Số quan sát (ngày giao dịch) tối thiểu (mặc định: {MIN_OBSERVATIONS}). '
             'Các mã cổ phiếu có ít hơn số ngày này sẽ bị loại bỏ'
    )
    parser.add_argument(
        '--missing-threshold', 
        type=float, 
        default=MISSING_THRESHOLD,
        help=f'🕳️ Ngưỡng dữ liệu thiếu cho phép (mặc định: {MISSING_THRESHOLD}). '
             'Tỷ lệ dữ liệu thiếu tối đa (0.0-1.0) mà vẫn giữ lại mã cổ phiếu'
    )
    parser.add_argument(
        '--volume-threshold', 
        type=float,
        help='📈 Ngưỡng khối lượng giao dịch tối thiểu. '
             'Các mã có median volume thấp hơn ngưỡng này sẽ bị loại bỏ (không giới hạn nếu không chỉ định)'
    )
    parser.add_argument(
        '--fill-limit', 
        type=int, 
        default=FILL_LIMIT,
        help=f'🔄 Số ngày tối đa cho phép điền dữ liệu thiếu (mặc định: {FILL_LIMIT}). '
             'Sử dụng giá trị 0 để không điền dữ liệu thiếu'
    )
    
    # Các tùy chọn đầu ra
    parser.add_argument(
        '--combine-all', 
        action='store_true',
        help='🗂️ Chỉ tạo một file đầu ra duy nhất chứa tất cả dữ liệu. '
             'Mặc định là tạo file riêng cho mỗi mã + file tổng hợp'
    )
    parser.add_argument(
        '--unique-format', 
        choices=['ticker', 'filename', 'index', 'hash'],
        default=UNIQUE_ID_FORMAT,
        help=f'🔑 Định dạng mã định danh duy nhất (mặc định: {UNIQUE_ID_FORMAT}). '
             'ticker: dùng ký hiệu mã, filename: dùng tên file, '
             'index: dùng số thứ tự, hash: dùng mã băm'
    )
    
    return parser.parse_args()


def main():
    """Hàm chính của chương trình"""
    
    # Kiểm tra arguments
    args = parse_arguments()
    
    # Xác định chế độ hoạt động
    if args.auto:
        # Chế độ tự động
        params = use_default_config()
        print("🤖 Chạy ở chế độ tự động với cấu hình mặc định")
        
    elif args.interactive:
        # Chế độ tương tác
        params = interactive_input()
        
    elif len(sys.argv) > 1:
        # Có arguments từ command line
        params = {
            'data_dir': args.data_dir,
            'out_dir': args.output_dir,
            'min_observations': args.min_obs,
            'missing_threshold': args.missing_threshold,
            'median_volume_threshold': args.volume_threshold,
            'fill_limit': args.fill_limit,
            'combine_all_data': args.combine_all,
            'unique_id_format': args.unique_format
        }
        print("⌨️ Sử dụng thông số từ command line arguments")
        
    else:
        # Không có arguments - chế độ tương tác mặc định
        choice = get_user_input()
        
        if choice == 1:
            params = interactive_input()
        elif choice == 2:
            params = use_default_config()
        else:
            print("❌ Lựa chọn không hợp lệ, sử dụng cấu hình mặc định")
            params = use_default_config()
    
    # Xác nhận trước khi chạy
    print(f"\n🔍 KIỂM TRA THÔNG SỐ:")
    print(f"   📁 Dữ liệu từ: {params['data_dir']}")
    print(f"   📤 Kết quả tại: {params['out_dir']}")
    print(f"   📊 Tối thiểu: {params['min_observations']} quan sát")
    print(f"   🕳️ Ngưỡng thiếu: {params['missing_threshold']*100:.1f}%")
    print(f"   📈 Ngưỡng volume: {params['median_volume_threshold'] or 'Không giới hạn'}")
    print(f"   🔄 Fill limit: {params['fill_limit']} ngày")
    print(f"   🗂️ Chế độ: {'Gom tất cả' if params['combine_all_data'] else 'File riêng'}")
    print(f"   🔑 ID format: {params['unique_id_format']}")
    
    confirm = input(f"\n✅ Tiếp tục với các thiết lập trên? (y/n) [y]: ").strip().lower()
    if confirm and confirm not in ['y', 'yes']:
        print("👋 Đã hủy thực thi.")
        return
    
    # Chạy pipeline
    print(f"\n🚀 BẮT ĐẦU XỬ LÝ...")
    pipeline_clean_all(**params)
    print(f"\n🎉 HOÀN THÀNH!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⛔ Người dùng đã dừng chương trình.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 LỖI NGHIÊM TRỌNG: {e}")
        logging.exception("Chi tiết lỗi:")
        sys.exit(1)