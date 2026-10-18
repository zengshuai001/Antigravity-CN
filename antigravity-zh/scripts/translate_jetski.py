import json
import os
import sys
import time
import urllib.request
import urllib.parse
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def translate_text(text, target_lang='zh-CN', source_lang='en'):
    if not text or not isinstance(text, str) or not text.strip():
        return text
        
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
                return translated
        except Exception as e:
            time.sleep(1 + attempt)
            
    return text

def is_safe_ui_string(s):
    if len(s) < 3:
        return False
        
    safe_single_words = {
        'accept', 'cancel', 'delete', 'close', 'settings', 'save', 'open', 
        'file', 'folder', 'search', 'view', 'help', 'user', 'model', 'agent', 
        'chat', 'error', 'warning', 'success', 'terminal', 'debug', 'run', 
        'stop', 'reset', 'clear', 'history', 'loading', 'stopped', 'allow', 
        'deny', 'always', 'never', 'options', 'archive', 'dismiss', 'approve',
        'export', 'import', 'refresh', 'configure', 'retry', 'abort', 'aborted',
        'about', 'active', 'add', 'advanced', 'all', 'analysis', 'analyzed',
        'appearance', 'back', 'next', 'previous', 'finish', 'completed', 'exit',
        'restart', 'reload', 'undo', 'redo', 'copy', 'paste', 'cut', 'share',
        'feedback', 'profile', 'accounts', 'login', 'logout', 'signin', 'signout',
        'features', 'options', 'preferences', 'themes', 'plugins', 'extensions'
    }
    
    s_lower = s.lower()
    if s_lower in safe_single_words:
        return True
        
    if ' ' in s:
        if re.match(r'^[a-zA-Z0-9\s\-\'\,\.\!\?\(\)\:]+$', s):
            return True
            
    return False

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates_path = os.path.join(project_root, 'source', 'jetski-ui-labels.json')
    patch_path = os.path.join(project_root, 'patches', 'jetskiAgent.patch.js')
    
    if not os.path.exists(candidates_path):
        print(f"Candidates file not found: {candidates_path}")
        sys.exit(1)
        
    with open(candidates_path, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
        
    safe_candidates = [c for c in candidates if is_safe_ui_string(c)]
    
    print(f"Total candidates: {len(candidates)}")
    print(f"Safe UI candidates: {len(safe_candidates)}")
    
    patch_data = []
    if os.path.exists(patch_path):
        try:
            with open(patch_path, 'r', encoding='utf-8') as f:
                patch_data = json.load(f)
            print(f"Loaded {len(patch_data)} existing patch items.")
        except Exception:
            pass
            
    translated_originals = {item['original'].strip('"') for item in patch_data}
    
    to_translate = [s for s in safe_candidates if s not in translated_originals]
    print(f"Remaining to translate: {len(to_translate)}")
    
    if not to_translate:
        print("All translations are already complete!")
        return

    # Use ThreadPoolExecutor to translate in parallel
    results_map = {}
    completed_count = 0
    total_to_translate = len(to_translate)
    
    print(f"Starting parallel translation with 10 threads...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_string = {executor.submit(translate_text, s): s for s in to_translate}
        
        for future in as_completed(future_to_string):
            s = future_to_string[future]
            try:
                translated = future.result()
                if translated and translated != s:
                    results_map[s] = translated
            except Exception as e:
                print(f"Failed translating: {s}. Error: {e}")
                
            completed_count += 1
            if completed_count % 10 == 0 or completed_count == total_to_translate:
                print(f"Progress: {completed_count}/{total_to_translate} ({(completed_count/total_to_translate)*100:.1f}%)")
                
                # Write current state of patch file
                current_patch = list(patch_data)
                for orig_s, trans_s in results_map.items():
                    current_patch.append({
                        "original": f'"{orig_s}"',
                        "translated": f'"{trans_s}"'
                    })
                with open(patch_path, 'w', encoding='utf-8') as f:
                    json.dump(current_patch, f, ensure_ascii=False, indent=2)

    # Save final results
    final_patch = list(patch_data)
    for orig_s, trans_s in results_map.items():
        final_patch.append({
            "original": f'"{orig_s}"',
            "translated": f'"{trans_s}"'
        })
        
    with open(patch_path, 'w', encoding='utf-8') as f:
        json.dump(final_patch, f, ensure_ascii=False, indent=2)
        
    print(f"Saved completed patch file to {patch_path}. Total items: {len(final_patch)}")

if __name__ == '__main__':
    main()
