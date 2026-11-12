"""V2-C8 -- Quet he so K: duong ngan hay duong an toan.

Du lieu case thuan (khong co logic). Chay: python main.py V2-C8 [--gif] [--paths]
"""

CASE = {'id': 'V2-C8',
 'title': 'Quet he so K: duong ngan hay duong an toan',
 'purpose': 'Cung mot ban do, doi he so quy doi mau -> chi phi K. K nho: di xuyen 3 bay cho nhanh. '
            'K lon: di vong an toan.',
 'expect': 'A2 doi lua chon khi K vuot nguong: K = 0 va 1 di thang (mat 3 mau), K >= 2 di vong (0 '
           'sat thuong, chi phi 13). Cot Oracle phai KHOP o moi K.',
 'params': {'b0': 5, 'q': 1, 'P': 1, 'ON': 1, 'K': 1},
 'k_sweep': [0, 1, 2, 4],
 'map': ['############', 'S..HHH...G..', '.########.##', '............']}
