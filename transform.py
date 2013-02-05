from pdb import pm

new = ""

for line in open("source/portfolio.yaml"):
    if line.startswith("content: <a ", 4):
        print("replacing")
        21
        new += "    content: <a href=\"portfolio/" + line[22:]
    else:
        new += line
f = open("source/portfolio.yaml", "w")
f.write(new)
f.flush()
f.close()
