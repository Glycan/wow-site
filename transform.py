from pdb import pm

new = ""

for line in open("source/portfolio.yaml"):
    if line.startswith("content: <a>", 4):
        print("replacing")
        name=line.split('\"')[1].split("/")[-1].split(".")[0]
        new  += '    content: <a href="' + name + "-balloon-decorations.html\"" + line[15:]
    else:
        new += line
f = open("source/portfolio.yaml", "w")
f.write(new)
f.flush()
f.close()
