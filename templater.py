#!/usr/bin/python3
import json
import sys
import os


frame = open("frame.html").read()
header = open("header.html").read()
bubble = open("bubble.html").read()
rule = open("rule.css").read()

if len(sys.argv) > 1:
    source = sys.argv[1]
if len(sys.argv) == 3:
    dest = sys.argv[2]
else:
    dest = "output"

try:
    print("making folder:", dest)
    os.mkdir(dest)
except OSError:
    print("it already exists")

files = os.listdir(source)
print("files source in folder:", files)
for filename in files:
    pagename, extension = filename.split(".")
    if extension == "json":
        print("building", pagename)
        pageinfo = json.load(open(source + os.sep + filename))
        print("opening css")
        css = open(dest + os.sep + pagename + ".css", "w")
        css.write(pageinfo.pop("CSS") + "\n")
        htmlcontent = ""
        pagetitle = pageinfo.pop("title")
        for objectid, attrs in pageinfo.items():
            print("making bubble:", objectid)
            css.write(rule.format(id=objectid, style=attrs.pop("style")))
            if "style" in attrs:
                attrs["style"] = " style=\"" + attrs["style"] + "\""
            else:
                attrs["style"] = ""
            htmlcontent += bubble.format(id=objectid + "-bubble", **attrs)
        print("writing html")
        open(dest + os.sep + pagename + ".html", "w").write(frame.format(
            title=pagetitle,
            stylesheet=pagename + ".css",
            header=header,
            content=htmlcontent,
        ))
        print("closing css")
        css.close()
