import re, sys

with open('index.php', 'r', encoding='utf-8') as f:
    src = f.read()

m = re.search(r'<script>(.*?)</script>', src, re.S)
if not m:
    print('No <script> block found')
    sys.exit(1)
js = m.group(1)
print(f'JS block: {len(js)} chars')

BACKSLASH = chr(92)
SQUOTE = chr(39)
DQUOTE = chr(34)
BTICK = chr(96)

stack = []
pairs = {')': '(', ']': '[', '}': '{'}
opens = set('([{')
in_str = None
in_line_comment = False
in_block_comment = False
i = 0
errs = []
while i < len(js):
    c = js[i]
    nxt = js[i + 1] if i + 1 < len(js) else ''
    if in_line_comment:
        if c == '\n':
            in_line_comment = False
        i += 1
        continue
    if in_block_comment:
        if c == '*' and nxt == '/':
            in_block_comment = False
            i += 2
            continue
        i += 1
        continue
    if in_str:
        if c == BACKSLASH and i + 1 < len(js):
            i += 2
            continue
        if c == in_str:
            in_str = None
        i += 1
        continue
    if c == '/' and nxt == '/':
        in_line_comment = True
        i += 2
        continue
    if c == '/' and nxt == '*':
        in_block_comment = True
        i += 2
        continue
    if c in (SQUOTE, DQUOTE, BTICK):
        in_str = c
        i += 1
        continue
    if c in opens:
        stack.append((c, i))
    elif c in pairs:
        if not stack or stack[-1][0] != pairs[c]:
            errs.append(f'Mismatched {c} at offset {i} (line ~{js[:i].count(chr(10))+1})')
            break
        stack.pop()
    i += 1

if stack:
    print(f'UNCLOSED brackets: {len(stack)}')
    for c, off in stack[-5:]:
        line = js[:off].count('\n') + 1
        print(f'  {c} at line ~{line}')
    sys.exit(1)
elif errs:
    print('\n'.join(errs))
    sys.exit(1)
else:
    print('OK - JS braces/parens/brackets balanceados')
