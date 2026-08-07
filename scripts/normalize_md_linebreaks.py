#!/usr/bin/env python3
import os
import re

root = '/Users/navin/tamil'
skip_dirs = {'.git'}
changed = 0
scanned = 0
for dirpath, dirs, files in os.walk(root):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for fname in files:
        if not fname.lower().endswith('.md'):
            continue
        scanned += 1
        path = os.path.join(dirpath, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
        except Exception as e:
            print(f"SKIP (read error): {path} -> {e}")
            continue
        out = []
        in_code = False
        modified = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            # detect fenced code blocks
            if stripped.startswith('```'):
                in_code = not in_code
                out.append(line)
                continue
            if in_code:
                out.append(line)
                continue
            # Ensure blank line after headings
            if stripped.startswith('#'):
                out.append(line)
                # if next line exists and is not blank, insert a blank line
                if i+1 < len(lines) and lines[i+1].strip() != '':
                    out.append('')
                    modified = True
                continue
            # skip lists, blockquotes, tables, headings, frontmatter
            if stripped == '':
                out.append('')
                continue
            if stripped.startswith(('-', '*', '+')) and (len(stripped)==1 or stripped[1:].startswith(' ')):
                out.append(line)
                continue
            if re.match(r'^\d+\.\s', stripped):
                out.append(line)
                continue
            if stripped.startswith('>'):
                out.append(line)
                continue
            if stripped.startswith('|'):
                out.append(line)
                continue
            # lines that already end with two or more spaces -> keep
            if line.endswith('  '):
                out.append(line)
                continue
            # For all-other plain lines, append two spaces to force a markdown line break
            new_line = line + '  '
            out.append(new_line)
            if new_line != line:
                modified = True
        if modified:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(out) + ('\n' if out and not out[-1].endswith('\n') else ''))
                print(f"UPDATED: {path}")
                changed += 1
            except Exception as e:
                print(f"FAIL WRITE: {path} -> {e}")

print(f"DONE: scanned={scanned} changed={changed}")
