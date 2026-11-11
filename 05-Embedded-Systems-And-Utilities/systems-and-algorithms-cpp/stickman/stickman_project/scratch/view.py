with open('scratch/last_raw_ds.txt', encoding='utf-8') as f:
    t = f.read()
print('LENGTH:', len(t))
print('TAIL 1200 CHARS:')
print(repr(t[-1200:]))
