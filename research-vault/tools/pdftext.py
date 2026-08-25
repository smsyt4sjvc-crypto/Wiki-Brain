#!/usr/bin/env python3
# ============================================================================
#  PDF TEXT — decode PDFs whose text sits behind SUBSET FONTS.
#
#  WHY THIS EXISTS (2026-08-21). The vault's ad-hoc extractor pulls the raw
#  glyph codes out of Tj/TJ operators. That works when the font uses a standard
#  encoding and produces a SUBSTITUTION CIPHER when it does not -- which is what
#  every Safari "Print to PDF" and most exported docs do. Two documents this week
#  came out as gibberish that way (the FOMC Safari capture, and this one).
#  THE FIX: read each font's /ToUnicode CMap and map code -> unicode per font,
#  tracking which font is active via Tf. No external deps (pypdf's cryptography
#  backend is broken in this container).
#
#  USAGE:  python3 tools/pdftext.py <file.pdf> [-o out.txt]
# ============================================================================
import re, zlib, sys, collections

def objects(d):
    """obj number -> (dict_bytes, stream_bytes|None)"""
    out = {}
    for m in re.finditer(rb'(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj', d, re.S):
        num = int(m.group(1)); body = m.group(3)
        sm = re.search(rb'stream\r?\n(.*?)\r?\nendstream', body, re.S)
        raw = None
        if sm:
            raw = sm.group(1); body = body[:sm.start()]
            if b'FlateDecode' in body:
                try: raw = zlib.decompress(raw)
                except Exception:
                    try: raw = zlib.decompressobj().decompress(raw)
                    except Exception: raw = b''
        out[num] = (body, raw)
    return out

def parse_cmap(b):
    """/ToUnicode CMap -> {code:int -> str}."""
    m = {}
    txt = b.decode('latin-1', 'replace')
    for blk in re.findall(r'beginbfchar(.*?)endbfchar', txt, re.S):
        for src, dst in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            try: m[int(src, 16)] = ''.join(chr(int(dst[i:i+4], 16)) for i in range(0, len(dst), 4))
            except ValueError: pass
    for blk in re.findall(r'beginbfrange(.*?)endbfrange', txt, re.S):
        for lo, hi, dst in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            try:
                lo_i, hi_i, d0 = int(lo, 16), int(hi, 16), int(dst, 16)
                for k in range(lo_i, min(hi_i, lo_i + 65535) + 1):
                    m[k] = chr(d0 + (k - lo_i))
            except ValueError: pass
        for lo, hi, arr in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*\[(.*?)\]', blk, re.S):
            dsts = re.findall(r'<([0-9A-Fa-f]+)>', arr)
            try:
                lo_i = int(lo, 16)
                for j, ds in enumerate(dsts):
                    m[lo_i + j] = ''.join(chr(int(ds[i:i+4], 16)) for i in range(0, len(ds), 4))
            except ValueError: pass
    return m

def font_maps(objs):
    """resource-name -> {code->str}, plus a merged fallback map."""
    by_obj = {}
    for num, (body, _) in objs.items():
        if b'/Font' not in body: continue
        tu = re.search(rb'/ToUnicode\s+(\d+)\s+\d+\s+R', body)
        if not tu: continue
        ref = int(tu.group(1))
        if ref in objs and objs[ref][1]:
            cm = parse_cmap(objs[ref][1])
            if cm: by_obj[num] = cm
    # map /F<n> resource names to font objects via any /Font << /Fx N 0 R >> dict
    byname = collections.defaultdict(dict)
    for num, (body, _) in objs.items():
        for name, ref in re.findall(rb'/(\w+)\s+(\d+)\s+0\s+R', body):
            r = int(ref)
            if r in by_obj: byname[name.decode()].update(by_obj[r])
    merged = {}
    for cm in by_obj.values(): merged.update(cm)
    return byname, merged

def show_strings(content):
    """yield ('font', name) and ('str', bytes) in stream order."""
    i, n = 0, len(content)
    while i < n:
        c = content[i:i+1]
        if c == b'(':
            depth, j, buf = 1, i+1, bytearray()
            while j < n and depth:
                ch = content[j:j+1]
                if ch == b'\\': buf += content[j:j+2]; j += 2; continue
                if ch == b'(': depth += 1
                elif ch == b')':
                    depth -= 1
                    if not depth: break
                buf += ch; j += 1
            yield ('str', bytes(buf)); i = j+1; continue
        if c == b'<' and content[i:i+2] != b'<<':
            j = content.find(b'>', i)
            if j < 0: break
            yield ('hex', content[i+1:j]); i = j+1; continue
        m = re.match(rb'/(\w+)\s+[\d.]+\s+Tf', content[i:i+64])
        if m: yield ('font', m.group(1).decode()); i += m.end(); continue
        if content[i:i+2] == b'T*' or content[i:i+2] == b'TD':
            yield ('flush', b''); i += 2; continue
        if content[i:i+2] in (b'Tj', b'TJ') or content[i:i+1] == b"'":
            i += 2; continue
        i += 1

def decode(path):
    d = open(path, 'rb').read()
    objs = objects(d)
    byname, merged = font_maps(objs)
    pieces, cur = [], None
    for num, (body, raw) in sorted(objs.items()):
        if not raw or b'/Image' in body: continue
        if not re.search(rb'\b(Tj|TJ)\b', raw): continue
        for kind, val in show_strings(raw):
            if kind == 'font': cur = byname.get(val) or merged; continue
            if kind == 'flush':
                if pieces and not pieces[-1].endswith((' ', '\n')): pieces.append(' ')
                continue
            cmap = cur if cur else merged
            if kind == 'hex':
                h = re.sub(rb'[^0-9A-Fa-f]', b'', val)
                if len(h) % 2: h += b'0'
                if len(h) % 4 == 0 and len(h) >= 4:
                    codes = [int(h[k:k+4], 16) for k in range(0, len(h), 4)]
                else:
                    codes = [int(h[k:k+2], 16) for k in range(0, len(h), 2)]
            else:
                # ⚠️ OCTAL ESCAPES ARE [0-7] ONLY. Using \d here matches \8 and \9,
                # which are NOT octal and blow up int(x, 8) -- hit on a Safari
                # capture 2026-08-22. Per the PDF spec a backslash before any
                # other character is dropped and the character stands.
                s = re.sub(rb'\\([0-7]{1,3})',
                           lambda m: bytes([int(m.group(1), 8) & 0xFF]), val)
                for esc, lit in ((rb'\\n', b'\n'), (rb'\\r', b'\r'), (rb'\\t', b'\t'),
                                 (rb'\\b', b'\b'), (rb'\\f', b'\f')):
                    s = re.sub(esc, lit, s)
                s = re.sub(rb'\\(.)', rb'\1', s)
                codes = list(s)
            pieces.append(''.join(cmap.get(c, chr(c) if 32 <= c < 127 else '') for c in codes))
    txt = ''.join(pieces)
    txt = re.sub(r'[ \t]{2,}', ' ', txt)
    return txt

if __name__ == '__main__':
    a = sys.argv[1:]
    t = decode(a[0])
    if '-o' in a: open(a[a.index('-o')+1], 'w').write(t); print(f'{len(t)} chars ->', a[a.index("-o")+1])
    else: print(t)
