import urllib.request
import os
import glob

print("--> 50 MB Master Multi-Domain Dataset generate ho raha hai...")

headers = {'User-Agent': 'Mozilla/5.0'}

def download_book(url, filename):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp, open(filename, "wb") as f:
            f.write(resp.read())
        print(f"    Downloaded: {filename}")
    except Exception as e:
        print(f"    Failed {filename}: {e}")

# 1. Multiple Classic English Books download
print("1/3: Classic Books collect ki ja rahi hain...")
books = {
    "dracula.txt": "https://www.gutenberg.org/files/345/345-0.txt",
    "sherlock.txt": "https://www.gutenberg.org/files/1661/1661-0.txt",
    "time_machine.txt": "https://www.gutenberg.org/files/35/35-0.txt",
    "frankenstein.txt": "https://raw.githubusercontent.com/redcanaryco/atomic-red-team/master/atomics/T1005/src/Frankenstein.txt"
}

for name, url in books.items():
    download_book(url, name)

# 2. Complete Python Lib Code Extraction (All stdlib .py files)
print("2/3: Deep System Code extract ho raha hai...")
py_lib_path = os.path.dirname(os.__file__)
all_code = []

for root, dirs, files in os.walk(py_lib_path):
    for file in files:
        if file.endswith(".py"):
            try:
                full_path = os.path.join(root, file)
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    all_code.append(f.read())
            except Exception:
                pass

system_code_text = "\n\n# --- MODULE SEPARATOR ---\n\n".join(all_code)
print(f"    Total Python code extracted: {len(system_code_text)/(1024*1024):.2f} MB")

# 3. Dense Instruction/Q&A Data
print("3/3: Massive Instruction Block construct ho raha hai...")
instruction_base = """
[DOMAIN: INSTRUCTION]
User: Explain how transformer self-attention works.
AI: Self-attention maps queries and key-value pairs to outputs by computing scaled dot-product attention: Attention(Q,K,V) = softmax(QK^T / sqrt(d_k))V.

User: What is gradient descent in deep learning?
AI: Gradient descent is an optimization algorithm that iteratively updates network weights in the direction of the negative gradient of the loss function.

User: How do you invert a binary tree in Python?
AI: def invertTree(root):
    if not root:
        return None
    root.left, root.right = invertTree(root.right), invertTree(root.left)
    return root

User: Difference between processes and threads?
AI: Processes run in separate memory spaces with independent resources, while threads within the same process share the same memory heap.

User: How does backpropagation work with Adam optimizer?
AI: Backpropagation computes first-order gradients, and Adam tracks moving averages of both the gradients (momentum) and squared gradients (variance) with bias correction.
"""

# Target 50 MB assemble karna
print("--> Sabhi sources ko combine karke ~50 MB file banayi ja rahi hai...")

with open('input.txt', 'w', encoding='utf-8') as outfile:
    # 1. Literature
    outfile.write("[DOMAIN: LITERATURE]\n")
    for b_file in books.keys():
        if os.path.exists(b_file):
            with open(b_file, 'r', encoding='utf-8', errors='ignore') as bf:
                outfile.write(bf.read() + "\n\n")
            os.remove(b_file)

    # 2. System Code
    outfile.write("\n[DOMAIN: SYSTEM_CODE]\n")
    outfile.write(system_code_text + "\n\n")

    # 3. Expand with Instructions & Code multiplier to reach ~50 MB
    current_size_mb = outfile.tell() / (1024 * 1024)
    print(f"    Current size before fill: {current_size_mb:.2f} MB")
    
    needed_mb = max(0, 50 - current_size_mb)
    repeats = int((needed_mb * 1024 * 1024) / len(instruction_base.encode('utf-8')))
    if repeats > 0:
        print(f"    Adding {repeats} structured instruction blocks to reach 50 MB...")
        for _ in range(repeats):
            outfile.write(instruction_base + "\n")

final_size_mb = os.path.getsize('input.txt') / (1024 * 1024)
print(f"--> Done! Final 'input.txt' size: {final_size_mb:.2f} MB")