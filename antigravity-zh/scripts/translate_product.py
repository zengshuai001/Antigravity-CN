import json
import os

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_app = os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
    default_product_path = os.path.join(local_app, "Programs", "Antigravity", "resources", "app", "product.json")
    orig_product_path = os.environ.get("AGY_PRODUCT_PATH", default_product_path)
    dest_product_path = os.path.join(project_root, 'translations', 'product.json')
    
    if not os.path.exists(orig_product_path):
        print(f"Original product.json not found at: {orig_product_path}")
        return
        
    with open(orig_product_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Translate the aiGeneratedWorkspaceTrust fields if they exist
    if 'aiGeneratedWorkspaceTrust' in data:
        trust = data['aiGeneratedWorkspaceTrust']
        if 'title' in trust:
            trust['title'] = "此工作区是由 AI 自动生成的"
        if 'checkboxText' in trust:
            trust['checkboxText'] = "信任此工作区中所有文件的内容"
        if 'trustOption' in trust:
            trust['trustOption'] = "是，我信任这些内容"
        if 'dontTrustOption' in trust:
            trust['dontTrustOption'] = "否，我不信任这些内容"
        if 'startupTrustRequestLearnMore' in trust:
            trust['startupTrustRequestLearnMore'] = "如果您不信任由 AI 生成的文件内容，我们建议您继续在受限模式下工作。请参阅[我们的文档](https://aka.ms/vscode-workspace-trust)以了解更多信息。"
            
    os.makedirs(os.path.dirname(dest_product_path), exist_ok=True)
    with open(dest_product_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Saved translated product.json to {dest_product_path}")

if __name__ == '__main__':
    main()
