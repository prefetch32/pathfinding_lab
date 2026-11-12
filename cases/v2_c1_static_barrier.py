"""V2-C1 -- Bay sat thuong co dinh chan duong (xuyen hay vong).

Du lieu case thuan (khong co logic). Chay: python main.py V2-C1 [--gif] [--paths]
"""

CASE = {'id': 'V2-C1',
 'title': 'Bay sat thuong co dinh chan duong (xuyen hay vong)',
 'purpose': 'Mau chua rang buoc (b0 lon): the hien V1.A* van dung khi mau khong la van de, va GBFS '
            'khong toi uu khi bay lam chi phi khac khoang cach.',
 'expect': 'A1 va A2 deu toi uu (chi phi 11, di vong, 0 sat thuong). B1 chi phi 13 (di xuyen bay, '
           'mat 4 mau), B2 chi phi 12. Bai hoc: sat thuong da lam B cao hon A, dung nhu V1.',
 'params': {'b0': 6, 'q': 1, 'P': 1, 'ON': 1, 'K': 1},
 'map': ['..........', '..........', 'S..HHHH..G', '..........', '..........']}
