"""V1-C7 -- Dich bi bao kin (khong co duong).

Du lieu case thuần (khong co logic). Chay: python main.py V1-C7 [--gif]
"""

CASE = {'id': 'V1-C7',
 'title': 'Dich bi bao kin (khong co duong)',
 'purpose': "Kiem tra tinh day du: thuat toan phai DUNG va bao 'khong co duong'.",
 'expect': 'A va B + closed dung voi NO_PATH (duyet het vung toi duoc). B standard khong bao gio '
           'dung (CAP_REACHED). Nhan manh: closed set cho B khong chi de nhanh hon ma de dung '
           'duoc.',
 'map': ['S..........#...',
         '...........#...',
         '...........#G..',
         '..........T#...',
         '....T.T.T..#...',
         '...........#...',
         '...........#...']}
