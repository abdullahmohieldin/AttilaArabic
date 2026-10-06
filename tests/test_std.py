import arabic_reshaper
import unicodedata
from fontTools.ttLib import TTFont

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

std_ar = [chr(cp) for cp in range(0x0621, 0x064B)] + [chr(0x0640)]
std_reshaped = set()
for ch in std_ar:
    for s in [ch, f' {ch} ', f'ب{ch}ب', f'ا{ch}ا']:
        for c in arabic_reshaper.reshape(s):
            std_reshaped.add(ord(c))

# Add Lam-Alef ligatures
for la in ['لا', 'لأ', 'لإ', 'لآ', ' ب全都 ', ' بلا ', ' بلأ ', ' بلإ ', ' بلآ ']:
    for c in arabic_reshaper.reshape(la):
        std_reshaped.add(ord(c))

print(f'Standard Arabic reshaped distinct codepoints: {len(std_reshaped)}')
missing = []
for cp in sorted(std_reshaped):
    in_c = cp in cmap
    b = base_letter(cp)
    b_in_c = (b in cmap) if b else False
    if not in_c and not b_in_c:
        missing.append(cp)

print(f'Missing from Tajawal: {len(missing)}')
for cp in missing:
    print(f'  U+{cp:04X} {unicodedata.name(chr(cp), "?")} decomp={unicodedata.decomposition(chr(cp))}')
