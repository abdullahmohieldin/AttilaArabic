import unicodedata
from fontTools.ttLib import TTFont
import arabic_reshaper

TAJAWAL = r'D:\AttilaArabic\fonts\upstream\Tajawal-Regular.ttf'
cmap = TTFont(TAJAWAL).getBestCmap()

def base_letter(cp):
    try:
        decomp = unicodedata.decomposition(chr(cp))
    except Exception:
        return None
    parts = decomp.split()
    if len(parts) >= 2 and parts[0].startswith('<'):
        try:
            return int(parts[1], 16)
        except ValueError:
            return None
    return None

full_cps = set()
full_cps.update(range(0x0621, 0x064B)) # U+0621-064A
full_cps.add(0x0640) # tatweel
full_cps.update(range(0x064B, 0x0653)) # harakat 064B-0652
full_cps.add(0x0670) # superscript alef
full_cps.update([0x060C, 0x061B, 0x061F, 0x066A, 0x066B, 0x066C, 0x06D4]) # punctuation
full_cps.update(range(0x0660, 0x066A)) # digits 0660-0669
full_cps.update(range(0xFB50, 0xFE00)) # FB50-FDFF
full_cps.update(range(0xFE70, 0xFF00)) # FE70-FEFF

available = {}
unavailable = []
for cp in sorted(full_cps):
    if cp in cmap:
        available[cp] = ('direct', chr(cp))
    else:
        b = base_letter(cp)
        if b is not None and b in cmap:
            available[cp] = ('decomp', chr(b))
        else:
            unavailable.append(cp)

print(f'Total in range: {len(full_cps)}')
print(f'Available (direct or 1-letter decomp): {len(available)}')
print(f'Unavailable: {len(unavailable)}')

needed_by_reshaper = set()
for cp in range(0x0600, 0x06FF):
    for s in [chr(cp), f' {chr(cp)} ', f'ب{chr(cp)}ب', f'ا{chr(cp)}ا']:
        try:
            for ch in arabic_reshaper.reshape(s):
                needed_by_reshaper.add(ord(ch))
        except:
            pass

ar_in_full = needed_by_reshaper.intersection(full_cps)
print(f'Needed by reshaper in full set: {len(ar_in_full)}')
missing_for_reshaper = [cp for cp in ar_in_full if cp not in available]
print(f'Missing for reshaper: {len(missing_for_reshaper)}')
for cp in missing_for_reshaper:
    print(f'  U+{cp:04X} {unicodedata.name(chr(cp), "?")} decomp={unicodedata.decomposition(chr(cp))}')
