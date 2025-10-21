# orangepi-oled-monitor

## Các bước thực hiện

1. Kết nối màn hình i2c vào Orange Pi của bạn, enable I2C lên trong orangepi-config hoặc armbian-config

2. Kiểm tra xem đã enable i2c chưa, đánh lệnh `ls /dev/i2c-*` xem có bao nhiêu i2c đã enable. Chọn đúng i2c của màn hình bạn bằng lệnh 
```
sudo i2cdetect -y 5
```

trong đó 5 là bus i2c đang cần check, nếu trả về địa chi 3c như hình là đúng

```bash
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

3. cài các phụ thuộc, dùng sudo pip để cài
```
sudo pip install luma.core luma.oled psutil
```

4. Chạy thử
```
sudo python oled-monitor-12864.py
```
hoặc
```
sudo python oled-monitor-12832.py
```

Màn hình hiện các thông số CPU, RAM, IP là ok

5. Cài thành service chạy mỗi khi khởi động
```bash
sudo cp oled-monitor.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable --now oled-monitor.service
```
