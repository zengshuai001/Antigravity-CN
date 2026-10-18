import json
import os
import sys
import time
import urllib.request
import urllib.parse
import re

def translate_text(text, target_lang='zh-CN', source_lang='en'):
    if not text.strip():
        return text
        
    # Check if the string is just formatting/placeholders/numbers
    if re.match(r'^[\d\s\{\}\(\)\[\]\.\,\:\;\-\+\*\/\#\@\&\!\?\_\|\\><\=]+$', text):
        return text

    # Protect placeholders like {0}, {1} by replacing them with temporary tokens
    # {0} -> _P_0_
    placeholders = re.findall(r'\{\d+\}', text)
    temp_text = text
    for i, p in enumerate(placeholders):
        temp_text = temp_text.replace(p, f" _P_{i}_ ")

    # Protect shortcut keys like &&File or &File
    shortcuts = re.findall(r'\&\&[a-zA-Z]', temp_text)
    for i, s in enumerate(shortcuts):
        temp_text = temp_text.replace(s, f" _S_{i}_ ")

    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q=" + urllib.parse.quote(temp_text)
    
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # Combine sentences if there are multiple parts
                translated_parts = []
                for sentence in data[0]:
                    if sentence[0]:
                        translated_parts.append(sentence[0])
                translated = "".join(translated_parts)
                
                # Restore shortcuts and placeholders
                for i, s in enumerate(shortcuts):
                    # Replace placeholder back
                    # Usually in Chinese, shortcuts are appended as " (&&F)" at the end.
                    # But for now, we can just replace the token back to its original position
                    translated = re.sub(fr'\s*_S_{i}_\s*', s, translated)
                    
                for i, p in enumerate(placeholders):
                    # Replace placeholder back
                    translated = re.sub(fr'\s*_P_{i}_\s*', p, translated)
                    
                # Basic cleanup of any space issues introduced inside brackets
                translated = re.sub(r'\{\s*(\d+)\s*\}', r'{\1}', translated)
                return translated
        except Exception as e:
            print(f"\n[Warning] Attempt {attempt+1} failed for text: '{text[:20]}...'. Error: {e}")
            time.sleep(2 ** attempt)
            
    return text  # Fallback to original

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    untranslated_path = os.path.join(project_root, 'source', 'untranslated.json')
    zh_cn_path = os.path.join(project_root, 'translations', 'nls.messages.zh-CN.json')
    
    if not os.path.exists(untranslated_path):
        print("untranslated.json not found. Please run find_untranslated.py first.")
        sys.exit(1)
        
    with open(untranslated_path, 'r', encoding='utf-8') as f:
        untranslated_items = json.load(f)
        
    with open(zh_cn_path, 'r', encoding='utf-8') as f:
        zh_cn_messages = json.load(f)
        
    total = len(untranslated_items)
    print(f"Starting translation of {total} strings...")
    
    changed = False
    count = 0
    
    try:
        for item in untranslated_items:
            idx = item['index']
            english = item['english']
            
            # Print progress every 10 items
            if count % 10 == 0 or count == total - 1:
                print(f"Progress: {count}/{total} ({(count/total)*100:.1f}%)", end='\r')
                
            # Translate
            translation = translate_text(english)
            
            if translation != english:
                zh_cn_messages[idx] = translation
                changed = True
                
            count += 1
            time.sleep(0.05)  # Politeness delay
            
            # Periodic save every 100 translations in case of interrupt
            if count % 100 == 0:
                with open(zh_cn_path, 'w', encoding='utf-8') as f:
                    json.dump(zh_cn_messages, f, ensure_ascii=False, indent=2)
                
    except KeyboardInterrupt:
        print("\nTranslation interrupted by user. Saving current progress...")
    finally:
        if changed:
            with open(zh_cn_path, 'w', encoding='utf-8') as f:
                json.dump(zh_cn_messages, f, ensure_ascii=False, indent=2)
            print(f"\nSaved updated translations to {zh_cn_path}")
            
    print("\nTranslation script complete!")

if __name__ == '__main__':
    main()
