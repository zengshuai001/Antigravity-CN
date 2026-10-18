import json
import os
import sys

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    keys_path = os.path.join(project_root, 'source', 'nls.keys.original.json')
    messages_path = os.path.join(project_root, 'source', 'nls.messages.original.json')
    
    # Path to downloaded VS Code language pack
    temp_dir = os.environ.get('TEMP', '')
    lang_pack_path = os.path.join(temp_dir, 'vscode-zh-hans', 'extension', 'translations', 'main.i18n.json')
    
    output_path = os.path.join(project_root, 'translations', 'nls.messages.zh-CN.json')
    
    if not os.path.exists(keys_path) or not os.path.exists(messages_path):
        print("Error: Source files keys or messages not found in source/", file=sys.stderr)
        sys.exit(1)
        
    if not os.path.exists(lang_pack_path):
        print(f"Error: Language pack main.i18n.json not found at {lang_pack_path}", file=sys.stderr)
        sys.exit(1)
        
    print("Loading source keys and messages...")
    with open(keys_path, 'r', encoding='utf-8') as f:
        keys_data = json.load(f)
        
    with open(messages_path, 'r', encoding='utf-8') as f:
        messages_data = json.load(f)
        
    print("Loading VS Code official language pack...")
    with open(lang_pack_path, 'r', encoding='utf-8') as f:
        lang_pack_data = json.load(f)
    
    lang_contents = lang_pack_data.get('contents', {})
    
    translated_messages = []
    matched_count = 0
    unmatched_count = 0
    
    # Global index to align with original messages
    global_index = 0
    
    print("Mapping translations...")
    for group in keys_data:
        module_path = group[0]
        key_list = group[1]
        
        module_translations = lang_contents.get(module_path, {})
        
        for key in key_list:
            original_msg = messages_data[global_index]
            
            # Check if translation exists in language pack
            if key in module_translations:
                translated_msg = module_translations[key]
                translated_messages.append(translated_msg)
                matched_count += 1
            else:
                # Fallback to English
                translated_messages.append(original_msg)
                unmatched_count += 1
                
            global_index += 1
            
    print(f"\nResults:")
    print(f"Total messages: {len(messages_data)}")
    print(f"Matched & Translated: {matched_count} ({matched_count / len(messages_data) * 100:.2f}%)")
    print(f"Unmatched (Kept English): {unmatched_count} ({unmatched_count / len(messages_data) * 100:.2f}%)")
    
    # Save the output
    print(f"Saving merged translations to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(translated_messages, f, ensure_ascii=False, indent=2)
        
    print("Done!")

if __name__ == '__main__':
    main()
