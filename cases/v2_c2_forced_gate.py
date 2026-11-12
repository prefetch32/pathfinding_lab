"""V2-C2 -- Ngo ket buoc qua bay (bai hoc Dumbledore).

Du lieu case thuan (khong co logic). Chay: python main.py V2-C2 [--gif] [--paths]
"""

CASE = {'id': 'V2-C2',
 'title': 'Ngo ket buoc qua bay (bai hoc Dumbledore)',
 'purpose': 'Phong cua start chi co mot loi ra la mot o bay sat thuong: tac nhan PHAI tra gia. '
            'Kiem tra thuat toan khong bo cuoc khi moi duong deu qua bay.',
 'expect': 'Moi thuat toan deu tim duoc duong (chi phi 8, mat 1 mau). A2 (h=relaxed) va A2 '
           '(h=damage) mo rong 7 nut vi h biet truoc phai chiu 1 sat thuong; A2 (h=Manhattan) mo '
           'rong 9 nut.',
 'params': {'b0': 3, 'q': 1, 'P': 1, 'ON': 1, 'K': 1},
 'map': ['#########', '#S..#...#', '#...H..G#', '#...#...#', '#########']}
