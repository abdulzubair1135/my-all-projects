with open('C:/Users/abdul/.gemini/antigravity/brain/a28b7e23-4a1d-490e-86cb-c5a75cf0dcb2/.system_generated/tasks/task-4341.log', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
    print('Total lines:', len(lines))
    print('Last 5 lines:', lines[-5:] if lines else 'empty')
