# DM-BTL
Source BTL Data Mining


# Các trường dẫn xuất
## 1. return: tỉ lệ biến động giá 
 công thức Return = (Close_today - Close_yesterday) / Close_yesterday

## 2. Lag Features – Ghi nhớ giá trong quá khứ
Close_lag1 = giá đóng cửa 1 ngày trước
Close_lag2 = giá đóng cửa 2 ngày trước
Close_lag3 = giá đóng cửa 3 ngày trước
Volume_lag1 = volume 1 ngày trước

👉 Ý nghĩa:

Mô hình machine learning không tự hiểu rằng dữ liệu có thứ tự thời gian.

Do đó ta phải đưa thông tin quá khứ vào qua "lag".

💡 Ví dụ:

Nếu Close_lag1 < Close_lag2 < Close_lag3 → xu hướng tăng mạnh

Volume_lag1 cao bất thường → dòng tiền đổ vào, thường báo hiệu biến động tiếp theo

👉 Lag features là yếu tố quan trọng nhất trong Time Series Prediction.

## 3. Moving Average (MA) – Trung bình động

MA5  = trung bình Close 5 ngày gần nhất
MA10 = trung bình Close 10 ngày gần nhất
MA20 = trung bình Close 20 ngày gần nhất

👉 Ý nghĩa:

MA thể hiện xu hướng (trend) của giá.

MA5 (ngắn hạn) nhạy với biến động → bắt xu hướng nhanh

MA20 (dài hạn) mượt → biểu hiện trend lớn

💡 Tình huống điển hình:

Close > MA5 > MA20 ⇒ Uptrend mạnh

Close < MA5 < MA20 ⇒ Downtrend

👉 Mô hình ML rất thích MA vì nó mô tả xu hướng rõ ràng.


## 4. STD5 và STD10 – Volatility (biến động)

STD5  = độ lệch chuẩn giá trong 5 ngày
STD10 = độ lệch chuẩn giá trong 10 ngày

👉 Ý nghĩa:

Đo mức độ biến động của giá.

Volatility cao → ngày mai giá thường dao động mạnh.

Volatility thấp → giá ổn định, xu hướng rõ ràng hơn.

💡 Thực tế thị trường:

Nếu STD tăng → thị trường sắp có chuyển động mạnh.

Nếu STD thấp → sắp có break-out hoặc tiếp tục nằm ngang.

## 5. TR (True Range) và ATR14 – Mức biến động thực
công thức TR = max(High_today, Close_yesterday) 
     - min(Low_today, Close_yesterday)

 👉 Ý nghĩa:
Đo biên độ thực sự của thị trường, vượt qua giới hạn High–Low đơn thuần.

## 6.Average True Range (ATR14)
ATR14 = trung bình TR trong 14 ngày
👉 Ý nghĩa:

Đo độ biến động ổn định của cổ phiếu trong 14 ngày.

ATR cao ⇒ giá biến động mạnh, rủi ro cao nhưng cơ hội lớn.

ATR thấp ⇒ thị trường đang nén, dễ xuất hiện cú break-out.

## 7. DayOfWeek – Ảnh hưởng theo ngày trong tuần

DayOfWeek = 0 (Thứ 2) → 6 (Chủ nhật)


Ý tưởng:
Thị trường tài chính thường có pattern theo ngày trong tuần.

Ví dụ hay gặp:

Thứ 2:

Nhiều tin tức tích luỹ cuối tuần → dễ có gap mạnh khi mở cửa

Thứ 6:

Nhiều người chốt lời / giảm vị thế để tránh rủi ro cuối tuần → giá có thể dễ điều chỉnh

Một số nghiên cứu còn chỉ ra:

Một vài thị trường có xu hướng xanh nhiều hơn vào giữa tuần, đỏ nhiều hơn đầu/ cuối tuần.

## 8. Target_Close – Mục tiêu dự đoán
Target_Close = Close ngày hôm sau


