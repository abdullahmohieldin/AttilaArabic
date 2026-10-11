import sys, struct
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\AttilaArabic\tw_attila_ar\backup\sp_grand_campaign.vanilla', 'rb') as f:
    vanilla = f.read()

with open(r'D:\AttilaArabic\data\ui\frontend ui\sp_grand_campaign', 'rb') as f:
    modded = f.read()

# Parse the key components - extract their X, Y, Width, Height from UIC binary
# UIC component structure (from the hex dump):
# [name_len:2][name:name_len][null][X:2(le i16)][Y:2(le i16)][...][W/H somewhere later]

# Based on the hex dump analysis:
# tx_religion at 45827: name starts at 45827, after null: X at 45840 (0xB310)
# Pattern: ...04 00 tx_religion 00 00 [X_lo X_hi] 00 00 [?? ??] 00 00
#   Vanilla:  45840 = 0x45 = 69
#   Modded:   45840 = 0xFA = 250

# Let me parse properly by looking at the actual byte layout
components = {
    'tx_religion': {
        'name_offset': 45830,       # where "tx_religion" string starts
        'x_offset': 45840,          # little-endian i16 X
        'w_offset': 45844,          # 4 bytes after X for Width? Actually it's at +4
    },
    'dy_religion': {
        'name_offset': 46190,
        'x_offset': 46200,          # vanilla=0xA9=169, modded=0x33,0xFF,0xFF,0xFF
    },
    'icon': {
        'name_offset': 46553,
        'x_offset': 46559,          # vanilla=0xE8,0xFF,0xFF,0xFF = -24 (signed i32)
    },
    'tx_faction_leader': {
        'name_offset': 47004,
        'x_offset': 47020,
    },
    'dy_faction_leader': {
        'name_offset': 47396,
        'x_offset': 47412,
    },
}

print("=== VANILLA LAYOUT VALUES ===")
for cname, info in components.items():
    xoff = info['x_offset']
    # Read as signed 32-bit little-endian
    vanilla_x_i32 = struct.unpack_from('<i', vanilla, xoff)[0]
    modded_x_i32 = struct.unpack_from('<i', modded, xoff)[0]
    
    # Also read the next fields (typically Y at +4, then maybe W at +8 or after flags)
    vanilla_next = struct.unpack_from('<4i', vanilla, xoff)[0:4]
    modded_next = struct.unpack_from('<4i', modded, xoff)[0:4]
    
    print()
    print("Component: {}".format(cname))
    print("  Vanilla X(i32)={}, next 4 ints: {}".format(vanilla_x_i32, vanilla_next))
    print("  Modded  X(i32)={}, next 4 ints: {}".format(modded_x_i32, modded_next))

# Also check fields after the first NewState
# For tx_religion: name ends at 45840, then we see: 45 00 00 00 50 00 00 00
# That looks like X=0x45=69, then something=0x50=80
# Then flags, then another: 45 00 00 00 50 00 00 00  (duplicate for state)
print("\n\n=== DETAILED TX_RELIGION AROUND OFFSET 45838 ===")
for src_name, src_data in [("VANILLA", vanilla), ("MODDED", modded)]:
    off = 45838
    vals = struct.unpack_from('<8I', src_data, off)
    print("{}: offsets 45838-45870 as u32: {}".format(src_name, vals))
    vals_s = struct.unpack_from('<8i', src_data, off)
    print("{}: offsets 45838-45870 as i32: {}".format(src_name, vals_s))

print("\n\n=== DETAILED DY_RELIGION AROUND OFFSET 46198 ===")
for src_name, src_data in [("VANILLA", vanilla), ("MODDED", modded)]:
    off = 46198
    vals = struct.unpack_from('<8I', src_data, off)
    print("{}: offsets 46198-46230 as u32: {}".format(src_name, vals))
    vals_s = struct.unpack_from('<8i', src_data, off)
    print("{}: offsets 46198-46230 as i32: {}".format(src_name, vals_s))

print("\n\n=== DETAILED ICON AROUND OFFSET 46557 ===")
for src_name, src_data in [("VANILLA", vanilla), ("MODDED", modded)]:
    off = 46557
    vals = struct.unpack_from('<8I', src_data, off)
    print("{}: offsets 46557-46589 as u32: {}".format(src_name, vals))
    vals_s = struct.unpack_from('<8i', src_data, off)
    print("{}: offsets 46557-46589 as i32: {}".format(src_name, vals_s))

print("\n\n=== DETAILED TX_FACTION_LEADER AROUND OFFSET 47018 ===")
for src_name, src_data in [("VANILLA", vanilla), ("MODDED", modded)]:
    off = 47018
    vals = struct.unpack_from('<8I', src_data, off)
    print("{}: offsets 47018-47050 as u32: {}".format(src_name, vals))
    vals_s = struct.unpack_from('<8i', src_data, off)
    print("{}: offsets 47018-47050 as i32: {}".format(src_name, vals_s))

print("\n\n=== DETAILED DY_FACTION_LEADER AROUND OFFSET 47410 ===")
for src_name, src_data in [("VANILLA", vanilla), ("MODDED", modded)]:
    off = 47410
    vals = struct.unpack_from('<8I', src_data, off)
    print("{}: offsets 47410-47442 as u32: {}".format(src_name, vals))
    vals_s = struct.unpack_from('<8i', src_data, off)
    print("{}: offsets 47410-47442 as i32: {}".format(src_name, vals_s))
