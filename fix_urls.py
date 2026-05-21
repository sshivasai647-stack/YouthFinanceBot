import sys
import re

filepath = r'c:\Users\sshiv\youth_finance_bot\templates\index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r"'http://127\.0\.0\.1:5000(/api/[^']+)'", r"`http://${window.location.hostname}:5000\1`", content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Replaced API URLs successfully.')
