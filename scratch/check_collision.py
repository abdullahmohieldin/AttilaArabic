import os
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from source.shape import shape

probes = [
    (0xFE80, 'CP_CHUNK_MISR', 'H3c: pre-rendered chunk'),
    (0xFE81, 'CP_BLEED_REH', 'H3b: bleed Reh final (widened right)'),
    (0xFE82, 'CP_BLEED_SAD', 'H3b: bleed Sad medial (widened right)'),
    (0xFE83, 'CP_BLEED_MEEM', 'H3b: Meem initial'),
    (0xFE84, 'CP_KERN_A', 'H4: kerning probe A'),
    (0xFE85, 'CP_KERN_B', 'H4: kerning probe B'),
    (0xFE86, 'CP_BLANK_40', 'H7b/c: blank 40px glyph'),
    (0xFE7D, 'CP_INK_SOLID', 'H5: thresholded solid Yeh'),
    (0xFE7E, 'CP_INK_GRAY', 'H5: antialiased gray Yeh'),
    (0xFEFC, 'CP_DEEP_YEH', 'H6: deep descender Yeh (-3px)'),
    (0xFEFD, 'CP_TALL_ALEF', 'H6: tall Alef (+3px)'),
]

non_probe_strings = {
    'btn_start_campaign_1': ('[B1] بدء الحملة', '[B1] ' + shape('بدء الحملة')),
    'btn_start_campaign_2': ('[B2] بدء الحملة', '[B2] ' + shape('بدء الحملة')),
    'header_factions_1': ('[F1] الفصائل', '[F1] ' + shape('الفصائل')),
    'header_factions_2': ('[F2] الفصائل', '[F2] ' + shape('الفصائل')),
    'header_factions_3': ('[F3] الفصائل', '[F3] ' + shape('الفصائل')),
    'diff_tooltip_1': ('[T1] مؤشر الصعوبة...', '[T1] ' + shape('مؤشر الصعوبة') + '||' + shape('حرك لتغيير الصعوبة')),
    'diff_tooltip_2': ('[T2] مؤشر الصعوبة...', '[T2] ' + shape('مؤشر الصعوبة') + '||' + shape('حرك لتغيير الصعوبة')),
    'diff_tooltip_3': ('[T3] مؤشر الصعوبة...', '[T3] ' + shape('مؤشر الصعوبة') + '||' + shape('حرك لتغيير الصعوبة')),
    'diff_hard_1': ('[H1] صعب', '[H1] ' + shape('صعب')),
    'diff_hard_2': ('[H2] صعب', '[H2] ' + shape('صعب')),
    'diff_hard_3': ('[H3] صعب', '[H3] ' + shape('صعب')),
    'diff_desc': ('[D1] للاعبين...', '[D1] ' + shape('للاعبين المتمرسين في توتال وور.')),
    'header_cultural': ('[C1] السمة الثقافية', '[C1] ' + shape('السمة الثقافية')),
    'faction_title': ('[FT] الإمبراطورية...', '[FT] ' + shape('الإمبراطورية الرومانية الشرقية')),
}

probe_words = {
    'H5 diacritics text': ('شَدَّة كَسْرَة', shape('شَدَّة كَسْرَة')),
    'H7a spaces text': ('مسافات', shape('مسافات')),
    'H7b blank text': ('فراغ', shape('فراغ')),
    'H7c blank text': ('بداية نهاية', shape('بداية') + ' ' + shape('نهاية')),
    'H9 tags text': ('أصفر نص', shape('أصفر') + ' ' + shape('نص')),
}

combined_real = {}
combined_real.update(non_probe_strings)
combined_real.update(probe_words)

print('=== CODEPOINT COLLISION CHECK ===\n')
for cp, tag, desc in probes:
    try:
        uname = unicodedata.name(chr(cp))
    except ValueError:
        uname = 'UNKNOWN / RESERVED'
    
    in_arabic = (0x0600 <= cp <= 0x06FF) or (0xFB50 <= cp <= 0xFDFF) or (0xFE70 <= cp <= 0xFEFF)
    
    matched_strings = []
    for s_id, (label, s_text) in combined_real.items():
        if chr(cp) in s_text:
            matched_strings.append(f'{s_id} ("{label}")')
            
    print(f'Probe: {tag} = U+{cp:04X} ({desc})')
    print(f'  Unicode Name: {uname}')
    print(f'  Arabic Block: {in_arabic}')
    if matched_strings:
        print(f'  COLLISION DETECTED with real Arabic text: {matched_strings}')
        print(f'  Trivial pass vulnerability: YES. Assertion checking all_override_text passes even without probe row.')
    else:
        print(f'  Collision: None in tested real strings.')
        print(f'  Trivial pass vulnerability: NO.')
    print()
