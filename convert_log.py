try:
    with open('etl_output_fixed_3.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('etl_debug_output_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Conversion successful")
except Exception as e:
    print(f"Error: {e}")
