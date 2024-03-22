# <div align="left">Cài đặt mô hình V8</div>

Hướng dẫn cài đặt đầy đủ chi tiết được viết trong file word hướng dẫn nằm tại thư mục `doc`.
## <div align="left">Tạo file info.json</div>
Tạo file info.json trong thư mục `evn-nano` với nội dung mẫu sau:

```sh
{
     "ip_edgecom": "",
     "ip_camera": "",
     "user_camera": "",
     "password_camera": "",
     "port_camera": "",
     "rtsp_format": ""
}
```

Với:
```sh
    - ip_edgecom là địa chỉ IP tĩnh của máy tĩnh đã đổi trước đó
    - ip_camera là địa chỉ IP tĩnh của camera đã đổi trước đó
    - user_camera là tài khoản của camera
    - password_camera là mật khẩu của camera
    - port_camera là port của camera 
    - rtsp_format là định dạng của rtsp tương ứng với hãng và mẫu camera sử dụng
```

Một số  ví dụ cho `rtsp_format`:
```sh
    - Hikvision: Streaming/channels/101
    - Dahua: cam/realmonitor?channel=1&subtype=1
    - Ezviz: onvif1
    - KBVision: cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif
    - Imou: cam/realmonitor?channel=1&subtype=1&unicast=true&proto=Onvif
```

## <div align="left">Sửa User và Password VPN</div>
Vào thư mục  `evn-nano/vpn` mở file `login.conf` và lần lượt sửa tương ứng user và password. 


## <div align="left">Tải mô hình AI</div>
Vào thư mục  `evn-nano`, tạo thư mục `resources`.

Trong thư mục `resources`, tạo tiếp hai thư mục con với tên `weight_init`, `images`.

Tải files mô hình AI với <a href="https://drive.google.com/drive/folders/1y9OA35H9LJ_9PNXCawJvHUDhaPX8-3d2?usp=sharing">link</a> này. Tên mô hình là `best.pt`.

File mô hình sẽ nằm trong thư mục Downloads, di chuyển file mô hình vào thư mục `evn-nano/resources/weight_init`.

## <div align="left">Sửa thông số độ chính xác từng đối tượng (Nếu muốn)</div>
Vào thư mục  `evn-nano` và mở file `object.json`. Độ chính xác từng đối tượng có tên là `"conf_thres"`. Lưu ý độ chính xác là số dạng thập phân, ví dụ `0.5` hoặc `0.98`.