import json
import os
import sys
import time
import urllib.request
import urllib.parse
import re

def translate_text(text, target_lang='zh-CN', source_lang='en'):
    if not text or not isinstance(text, str) or not text.strip():
        return text
        
    # Check if the string is just formatting/placeholders/numbers
    if re.match(r'^[\d\s\{\}\(\)\[\]\.\,\:\;\-\+\*\/\#\&\!\?\_\|\\><\=\%\$]+$', text):
        return text

    # Handle VS Code extension specific markups, e.g. markdown links, bold, etc.
    # We will just translate it directly via API
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q=" + urllib.parse.quote(text)
    
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                translated_parts = []
                for sentence in data[0]:
                    if sentence[0]:
                        translated_parts.append(sentence[0])
                translated = "".join(translated_parts)
                # Cleanup spaces in markdown formatting
                translated = re.sub(r'\[\s*(.*?)\s*\]\(\s*(.*?)\s*\)', r'[\1](\2)', translated)
                return translated
        except Exception as e:
            print(f"\n[Warning] Attempt {attempt+1} failed for: '{text[:20]}...'. Error: {e}")
            time.sleep(2 ** attempt)
            
    return text

def translate_json_recursive(obj, keys_to_translate):
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if k in keys_to_translate and isinstance(v, str):
                print(f"  Translating key '{k}': {v[:30]}...")
                new_dict[k] = translate_text(v)
                time.sleep(0.05)
            else:
                new_dict[k] = translate_json_recursive(v, keys_to_translate)
        return new_dict
    elif isinstance(obj, list):
        return [translate_json_recursive(item, keys_to_translate) for item in obj]
    else:
        return obj

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_exts_dir = os.path.join(project_root, 'source', 'extensions')
    trans_exts_dir = os.path.join(project_root, 'translations', 'extensions')
    
    if not os.path.exists(source_exts_dir):
        print(f"Error: Source extensions folder not found: {source_exts_dir}")
        sys.exit(1)
        
    keys_to_translate = {
        'displayName', 'description', 'title', 'label', 'markdownDescription', 'name'
    }
    
    extensions = [d for d in os.listdir(source_exts_dir) if os.path.isdir(os.path.join(source_exts_dir, d))]
    
    print(f"Found {len(extensions)} extensions to translate: {extensions}")
    
    for ext in extensions:
        src_pkg_path = os.path.join(source_exts_dir, ext, 'package.json')
        dest_dir = os.path.join(trans_exts_dir, ext)
        dest_pkg_path = os.path.join(dest_dir, 'package.json')
        
        if not os.path.exists(src_pkg_path):
            continue
            
        print(f"\nProcessing extension: {ext}...")
        with open(src_pkg_path, 'r', encoding='utf-8') as f:
            pkg_data = json.load(f)
            
        translated_pkg = translate_json_recursive(pkg_data, keys_to_translate)
        
        os.makedirs(dest_dir, exist_ok=True)
        with open(dest_pkg_path, 'w', encoding='utf-8') as f:
            json.dump(translated_pkg, f, ensure_ascii=False, indent=2)
            
        print(f"Saved translated package.json to {dest_pkg_path}")
        
    print("\nExtension translation complete!")

if __name__ == '__main__':
    main()
