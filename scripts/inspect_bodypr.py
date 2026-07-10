import sys
import zipfile
from pathlib import Path

path = Path(sys.argv[1])
with zipfile.ZipFile(path) as zf:
    xml = zf.read("ppt/slides/slide1.xml").decode("utf-8", errors="ignore")

# Extract text bodies for shapes - rough search by position in file
for tag in ["anchor", "wrap", "lIns", "tIns", "noAutofit", "normAutofit", "spAutoFit"]:
    count = xml.count(tag)
    if count:
        print(f"{tag}: {count}")

# Check shape 2 area - find autofit on txBody
import re
bodies = re.findall(r"<p:txBody>.*?</p:txBody>", xml, re.DOTALL)
print(f"txBody count: {len(bodies)}")
for i, body in enumerate(bodies[:5]):
    bodypr = re.search(r"<a:bodyPr[^/]*/>", body)
    print(f"body {i} bodyPr: {bodypr.group(0)[:120] if bodypr else 'none'}")
