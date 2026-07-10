import sys
import zipfile

path = sys.argv[1]
needle = sys.argv[2] if len(sys.argv) > 2 else "284E64"
with zipfile.ZipFile(path) as zf:
    xml = zf.read("ppt/slides/slide1.xml").decode("utf-8", errors="ignore")

idx = xml.find(needle)
print(f"Found {needle} at {idx}")
if idx != -1:
    print(xml[max(0, idx - 200) : idx + 200])
