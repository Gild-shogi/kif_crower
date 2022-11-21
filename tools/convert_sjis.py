import glob

for path  in glob.glob('kif_sjis/*/*.kif'):
    with open(path, mode="r", encoding="utf-8") as f:
        text = f.read()
    with open(path, mode="w+", encoding="shift-jis") as f:
        f.write(text)