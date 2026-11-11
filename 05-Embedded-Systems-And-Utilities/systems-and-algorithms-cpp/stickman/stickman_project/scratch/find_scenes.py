with open('scratch/last_raw_ds.txt', encoding='utf-8') as f:
    t = f.read()

# Let's find "scenes" in t
idx = t.rfind('"scenes"')
print("Index of 'scenes':", idx)
if idx != -1:
    # Look backwards from 'scenes' to find the opening '{' of the object
    snippet = t[max(0, idx-500):idx+100]
    print("Snippet around 'scenes':")
    print(repr(snippet))
