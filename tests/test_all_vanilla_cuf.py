import glob, os, sys
sys.path.insert(0, r"D:\AttilaArabic\source")
from cuf import CUF

for f in sorted(glob.glob(r"extracted\fonts\*.cuf")):
    c = CUF.decode(open(f, "rb").read())
    name = os.path.basename(f)
    v_sz = c.props["v_size"]
    base = c.props["baseline"]
    ah_vals = set(dim[0] for dim in c.dims)
    h_vals = set(dim[3] for dim in c.dims)
    diff = sum(1 for dim in c.dims if dim[0] != dim[3] and dim[0] != -128)
    h_diff_vsize = sum(1 for dim in c.dims if dim[3] != v_sz and dim[0] != -128)
    print(f"{name:30}: v_size={v_sz:2}, base={base:2} | ah={sorted(ah_vals)} | h={sorted(h_vals)} | ah!=h:{diff} | h!=v_size:{h_diff_vsize}")
