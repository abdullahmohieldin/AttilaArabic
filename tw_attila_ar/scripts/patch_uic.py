import struct
import os

base = r'D:\AttilaArabic'
vanilla_path = os.path.join(base, 'tw_attila_ar', 'backup', 'sp_grand_campaign.vanilla')
target_path = os.path.join(base, 'data', 'ui', 'frontend ui', 'sp_grand_campaign')

with open(vanilla_path, 'rb') as f:
    data = bytearray(f.read())

# Exact coordinates for consistent RTL Arabic layout:
# Container right-aligned at X=220, dynamic values at X=-175 (abs X=45)
# Icon at X=145 (abs X=190, between dy_religion and tx_religion)
coord_patches = [
    # tx_religion (abs X=220, Y=80)
    (45840, 220, 80),
    (45868, 220, 80),

    # dy_religion (rel X=-175, Y=0 -> abs X=45)
    (46200, -175, 0),
    (46228, -175, 0),

    # icon (rel X=145, Y=0 -> abs X=190)
    (46559, 145, 0),
    (46587, 145, 0),

    # tx_faction_leader (abs X=220, Y=50)
    (47020, 220, 50),
    (47048, 220, 50),

    # dy_faction_leader (rel X=-175, Y=0 -> abs X=45)
    (47412, -175, 0),
    (47440, -175, 0),
]

for offset, x, y in coord_patches:
    struct.pack_into('<2i', data, offset, x, y)
    print(f'Coord patch offset {offset}: X={x}, Y={y}')

# Width patches in NewState
# dy_religion width = 145 (from X=45 to 190, touching icon)
struct.pack_into('<i', data, 46271, 145)
print('dy_religion width set to 145')

# dy_faction_leader width = 170 (from X=45 to 215, touching tx_faction_leader)
struct.pack_into('<i', data, 47483, 170)
print('dy_faction_leader width set to 170')

# Alignment patches in NewState:
# 2 = Left alignment (text starts at left anchor of box)
# 3 = Right alignment (text flushes against right edge of box)
align_patches = [
    # tx_religion: align Left (2) so it starts right at X=220
    (45941, 2),
    # dy_religion: align Right (3) so it flushes to X=190 next to icon
    (46305, 3),
    # tx_faction_leader: align Left (2) so it starts right at X=220
    (47133, 2),
    # dy_faction_leader: align Right (3) so it flushes to X=215 next to label
    (47513, 3),
]

for offset, align in align_patches:
    struct.pack_into('<i', data, offset, align)
    print(f'Align patch offset {offset}: align_x={align}')

with open(target_path, 'wb') as f:
    f.write(data)

print(f'Successfully wrote patched UIC to: {target_path}')
