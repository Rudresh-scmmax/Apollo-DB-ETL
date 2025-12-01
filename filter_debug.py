with open('debug_output_utf8.txt', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if '[DEBUG]' in line or 'Rows:' in line or 'Count' in line:
            print(line.strip())
