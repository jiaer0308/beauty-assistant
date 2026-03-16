import os
from bs4 import BeautifulSoup

for filename in sorted(os.listdir('stitch_screens')):
    if not filename.endswith('.html'):
        continue
    print(f"\n--- {filename} ---")
    with open(os.path.join('stitch_screens', filename), 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
        
    text = soup.get_text(separator='\n')
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    filtered_lines = []
    for line in lines:
        if line in ["arrow_back", "check", "Skip", "Next", "Back", "arrow_forward"]:
            continue
        filtered_lines.append(line)
        
    print("\n".join(filtered_lines))
