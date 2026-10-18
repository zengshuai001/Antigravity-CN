import json
import os

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    keys_path = os.path.join(project_root, 'source', 'nls.keys.original.json')
    messages_path = os.path.join(project_root, 'source', 'nls.messages.original.json')
    
    temp_dir = os.environ.get('TEMP', '')
    lang_pack_path = os.path.join(temp_dir, 'vscode-zh-hans', 'extension', 'translations', 'main.i18n.json')
    
    output_untranslated_path = os.path.join(project_root, 'source', 'untranslated.json')
    
    with open(keys_path, 'r', encoding='utf-8') as f:
        keys_data = json.load(f)
        
    with open(messages_path, 'r', encoding='utf-8') as f:
        messages_data = json.load(f)
        
    with open(lang_pack_path, 'r', encoding='utf-8') as f:
        lang_pack_data = json.load(f)
        
    lang_contents = lang_pack_data.get('contents', {})
    
    untranslated_items = []
    global_index = 0
    
    for group in keys_data:
        module_path = group[0]
        key_list = group[1]
        
        module_translations = lang_contents.get(module_path, {})
        
        for key in key_list:
            original_msg = messages_data[global_index]
            
            # Check if key is not translated in lang pack
            if key not in module_translations:
                untranslated_items.append({
                    "index": global_index,
                    "module": module_path,
                    "key": key,
                    "english": original_msg
                })
                
            global_index += 1
            
    # Sort untranslated items by module
    untranslated_items.sort(key=lambda x: x['module'])
    
    print(f"Total untranslated items: {len(untranslated_items)}")
    
    # Save the output
    with open(output_untranslated_path, 'w', encoding='utf-8') as f:
        json.dump(untranslated_items, f, ensure_ascii=False, indent=2)
        
    print(f"Saved list to {output_untranslated_path}")

if __name__ == '__main__':
    main()
