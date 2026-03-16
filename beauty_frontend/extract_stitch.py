import urllib.request
from bs4 import BeautifulSoup

urls = {
    'Page1': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzc3ZGQwZDY5NmI3ZTQ2MTZiM2U3ZGRlMGNlYjhjNmUyEgsSBxCC9prb2hgYAZIBJAoKcHJvamVjdF9pZBIWQhQxNTAzNTcwMzcyMDg5ODY3MTMwMw&filename=&opi=89354086',
    'Page2': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzgxNzE0ZDgwYTUwYzQ5Y2Q4ZGFhMmRmOTk1MGVjNzcyEgsSBxCC9prb2hgYAZIBJAoKcHJvamVjdF9pZBIWQhQxNTAzNTcwMzcyMDg5ODY3MTMwMw&filename=&opi=89354086',
    'Page3': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzkxNTg5ZjczYjZiMDQzNzVhM2I1NzA4NzI5ZTY2Yjk4EgsSBxCC9prb2hgYAZIBJAoKcHJvamVjdF9pZBIWQhQxNTAzNTcwMzcyMDg5ODY3MTMwMw&filename=&opi=89354086',
    'Page4': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sX2UwZWU2MGQ3NmEzNjQxNTNhN2I1M2QxOGE5NmQxMjNiEgsSBxCC9prb2hgYAZIBJAoKcHJvamVjdF9pZBIWQhQxNTAzNTcwMzcyMDg5ODY3MTMwMw&filename=&opi=89354086',
    'Page5': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzI2NDk2ZTY3YmM1ZTRjMGRhOTg3MmQ2ODdlN2FmYjYwEgsSBxCC9prb2hgYAZIBJAoKcHJvamVjdF9pZBIWQhQxNTAzNTcwMzcyMDg5ODY3MTMwMw&filename=&opi=89354086',
    'Page6': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sX2FlZWFmZTZhZGY2ZDQyNzQ5OWUwZmVhY2VmNzgyY2YwEgsSBxCC9prb2hgYAZIBJAoKcHJvamVjdF9pZBIWQhQxNTAzNTcwMzcyMDg5ODY3MTMwMw&filename=&opi=89354086',
    'Page8': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sX2I4ZmViM2Q0ZjI1ZDQxM2JhMWZjOGQ2OTJlM2JhYmU5EgsSBxCC9prb2hgYAZIBJAoKcHJvamVjdF9pZBIWQhQxNTAzNTcwMzcyMDg5ODY3MTMwMw&filename=&opi=89354086',
    'Page9': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzM3YTFhMzBmYjI5ZjRkN2M4MmZmYTAyMTVlNGVlNTEzEgsSBxCC9prb2hgYAZIBJAoKcHJvamVjdF9pZBIWQhQxNTAzNTcwMzcyMDg5ODY3MTMwMw&filename=&opi=89354086',
    'Page10':'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzQ1YTc1MDY3NTM5ZjQ4ZmI5YzhmZDIxZmIxYWRmOTM3EgsSBxCC9prb2hgYAZIBJAoKcHJvamVjdF9pZBIWQhQxNTAzNTcwMzcyMDg5ODY3MTMwMw&filename=&opi=89354086',
}

for name, url in urls.items():
    print(f"--- {name} ---")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try to extract the main text content, ignoring scripts and styles
    for script in soup(["script", "style"]):
        script.extract()
        
    # Get text and clean it up
    text = soup.get_text(separator='|')
    lines = [line.strip() for line in text.split('|') if line.strip()]
    for line in lines:
        if len(line) > 1 and line not in ["Skip", "Next", "Back", "arrow_back", "check"]:
            print(line)
    print("\n")
