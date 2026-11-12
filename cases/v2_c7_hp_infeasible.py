"""V2-C7 -- Gioi han: mau khong du de qua rao bay.

Du lieu case thuan (khong co logic). Chay: python main.py V2-C7 [--gif] [--paths]
"""

CASE = {'id': 'V2-C7',
 'title': 'Gioi han: mau khong du de qua rao bay',
 'purpose': 'Rao bay day 3 o, moi o mat 1 mau, b0 = 3: qua duoc rao se ve 0 mau nen KHONG CO '
            'DUONG. Mo ta gioi han: h bo rang buoc mau nen khong thay duoc dieu nay truoc khi '
            'duyet.',
 'expect': 'Moi thuat toan dung voi NO_PATH. A2 va B2 phai duyet het khong gian (b, pha) -> so nut '
           'mo rong lon hon A1/B1 (A1, B1 bo cuoc som nhung vi ly do sai: ho khong thay mau).',
 'params': {'b0': 3, 'q': 1, 'P': 1, 'ON': 1, 'K': 1},
 'map': ['...........HHH....',
         '...........HHH....',
         'S..........HHH...G',
         '...........HHH....',
         '...........HHH....']}
