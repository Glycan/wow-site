#!/usr/bin/python3
import json
import yaml
import markdown
import os
import shutil
from collections import defaultdict
from argparse import ArgumentParser
from yaml_ordered_dict import OrderedDictYAMLLoader
from subprocess import call, Popen, PIPE

from pdb import set_trace


frame = open("templates/frame.html").read()
bubble = open("templates/bubble.html").read()
rule = open("templates/rule.css").read()

header = open("other/header.html").read()
footer = open("other/footer.html").read()


parser = ArgumentParser(description="""
Put togeather a site from source files. The contents of the nonhtml folder
will be copied into the output file. The source files can be in YAML or JSON
format. Each section will be made into a bubble. Each bubble should have a
content attribute, a type attribute (which will be it's class attribute),
and possibly a CSS attribute (which will be it's style attribute). A source
file can also have a CSS attribute, which will be put into a linked css
file. A source file should also have a title attribute, which will be it's
title
""")
parser.add_argument("source", default="source", nargs="?",
    help="a directory with the source files in JSON or YAML, defaults to source")

parser.add_argument("dest", default="output", nargs="?",
    help="the directory to output to, will be created if it doesn't exist, "
    "defaults to output")

parser.add_argument("-d", "--dont-copy", action="store_false", dest="copy",
    default=True, help="don't copy nonhtml files to output dir"
)

parser.add_argument("-k", "--keep-folder", action="store_false", dest="clear",
    default=True, help="clear the output folder if it exists, implies -d")

parser.add_argument("-t", "--testing", action="store_true", dest="testing",
    default=False, help="copy the testing.html file into each file")

parser.add_argument("--debug", action="store_true", dest="debug", default=False,
    help="activate debug mode")

parser.add_argument("--compress", action="store_true", dest="compress",
    default=False, help="compress CSS outputed by LESS")




def lessc(source):
    arg = ""
    if args.compress:
        arg = "--compress"
        print("compressing less")
    proc = Popen("lessc " + arg + " -", shell=True, stdin=PIPE, stdout=PIPE)
    proc.stdin.write(bytes('@import "temp.less";\n' + source, "utf-8"))
    proc.stdin.close()
    proc.wait()
    output = proc.stdout.read().decode() + "\n"
    #####CHECK THIS IF ANYTHING LOOKS WEIRD WITH THE CESS!
    #set_trace()
    output = output.split("/*end*/")[-1]
    #lessc import shoves everything in the temp file into the
    #output. this cuts away everything before, well, something
    return output

if __name__ == "__main__":
    args = parser.parse_args()

    if args.testing:
        print("adding testing html to footer")
        footer += "\n" + open("other/testing.html").read()

    if args.clear:
        print("clearing output folder")
        try:
            shutil.rmtree(args.dest)
        except OSError:
            print("it does not exist")
        if args.copy:
            print("copying nonhtml files into output folder")
            shutil.copytree("nonhtml", args.dest)
            for fname in os.listdir("less"):
                print("less is compiling", fname)
                destname = args.dest + os.sep + fname.split(".")[0] + ".css"
                call(["lessc", "--yui-compress", "less" + os.sep + fname, destname])
        else:
            print("not copying nonhtml files because -d")
    else:
        print("not copying nonhtml files because -k")
        try:
            print("making output folder:", args.dest)
            os.mkdir(args.dest)
        except OSError:
            print("it already exists")

    files = os.listdir(args.source)
    print("source files in folder:", files)
    for filename in files:
        pagename, extension = filename.rsplit(".", 1)
        pageinfo = None
        if extension == "json":
            pageinfo = json.load(open(args.source + os.sep + filename))
            print("loading", filename, "as JSON")
        elif extension =="yaml":
            pageinfo = yaml.load(open(args.source + os.sep + filename), OrderedDictYAMLLoader)
            print("loading", filename, "as YAML")
        else:
            print("unknown extension", extension + ", skipping file", filename)
        if pageinfo:
            print("opening css")
            css = open(args.dest + os.sep + pagename + ".css", "w")
            open("temp.less", 'w').write(pageinfo.pop("less", "") + "\n\n")
            css.write(lessc(pageinfo.pop("CSS", "")) + "\n")
            htmlcontent = ""
            pagetitle = pageinfo.pop("title")
            JS = pageinfo.pop("JS", "")
            for objectid, attrs in pageinfo.items():
                print("making bubble:", objectid)
                if "style" in attrs:
                    style = lessc(rule.format(id=objectid, style=attrs.pop("style")))
                    if args.debug:
                        print(style)
                    css.write(style)
                if "\n" in attrs["content"]:
                    attrs["content"] = markdown.markdown(attrs["content"])
                htmlcontent += bubble.format(id=objectid + "-bubble", **attrs)
            print("writing html")
            open(args.dest + os.sep + pagename + ".html", "w").write(frame.format(
                title=pagetitle,
                stylesheet=pagename + ".css",
                header=header,
                footer=footer,
                content=htmlcontent,
                JS=JS
            ))
            print("closing css")
            css.close()
os.remove("temp.less")
