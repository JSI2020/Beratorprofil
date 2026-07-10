import re
import sys
import zipfile

path = sys.argv[1]
with zipfile.ZipFile(path) as zf:
    xml = zf.read("ppt/slides/slide1.xml").decode("utf-8", errors="ignore")

fills = sorted(set(re.findall(r'srgbClr val="([A-F0-9]{6})"', xml, re.I)))
print("RGB fills:", fills)
