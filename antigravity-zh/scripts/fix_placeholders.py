import json
import os
import re

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    orig_path = os.path.join(project_root, 'source', 'nls.messages.original.json')
    trans_path = os.path.join(project_root, 'translations', 'nls.messages.zh-CN.json')
    
    with open(orig_path, 'r', encoding='utf-8') as f:
        original = json.load(f)
        
    with open(trans_path, 'r', encoding='utf-8') as f:
        translated = json.load(f)
        
    fixed_count = 0
    
    for i in range(len(original)):
        orig_msg = original[i]
        trans_msg = translated[i]
        
        orig_placeholders = sorted(re.findall(r'\{\d+\}', orig_msg))
        trans_placeholders = sorted(re.findall(r'\{\d+\}', trans_msg))
        
        if orig_placeholders != trans_placeholders:
            print(f"Index {i} placeholder mismatch:")
            print(f"  Orig : '{orig_msg}' -> {orig_placeholders}")
            print(f"  Trans: '{trans_msg}' -> {trans_placeholders}")
            print(f"  --> Falling back to English.")
            
            translated[i] = orig_msg
            fixed_count += 1
            
    print(f"\nFixed {fixed_count} mismatching translation items.")
    
    with open(trans_path, 'w', encoding='utf-8') as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)
        
    print("Saved fixed translations.")

if __name__ == '__main__':
    main()
