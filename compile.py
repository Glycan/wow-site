#!/usr/bin/python3
import json
import yaml
import markdown
import os
import shutil
from pprint import pprint
from collections import defaultdict
from argparse import ArgumentParser
from yaml_ordered_dict import OrderedDictYAMLLoader
from subprocess import call, Popen, PIPE

from pdb import set_trace, pm

DEFAULT_ROOT = "/home/glycan/wow-site/output"
SOURCE_ROOT = "/home/glycan/wow-site/source"


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
    help="a directory with the source files in JSON or YAML, or path to one "
    "such file, defaults to source. Files *must* have extensions")

parser.add_argument("dest", default="output", nargs="?",
    help="the directory to output to, will be created if it doesn't exist, "
    "defaults to output")

parser.add_argument("root_less", default="bubble", nargs="?",
    help="the root less file too use")

parser.add_argument("header", default="bubble", nargs="?",
    help="what header to use, doesn't include extension")

parser.add_argument("-d", "--dont-copy", action="store_false", dest="copy",
    default=True, help="don't copy nonhtml files to output dir")

parser.add_argument("-l", "--leave-less", action="store_false", dest="less_copy",
    default=True, help="don't compile+copy less")

parser.add_argument("-k", "--keep-folder", action="store_false", dest="clear",
    default=True, help="clear the output folder if it exists, implies -d")

parser.add_argument("-t", "--testing", action="store_true", dest="testing",
    default=False, help="copy the testing.html file into each file")

parser.add_argument("--debug", action="store_true", dest="debug", default=False,
    help="activate debug mode")

parser.add_argument("--compress", action="store_true", dest="compress",
    default=False, help="compress CSS outputed by LESS")

parser.add_argument("--root", default=DEFAULT_ROOT, help="the site's root")

def set_root(s):
    return s.replace("~", args.root)


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

def compile_items(items, css):
    """
    items:  an ItemsView object of a dictionary or a [(key, value)*] object
    css: an open file to write CSS to
    -> the compiled html of each item, compiling recursivly
    """
    content = ""
    for objectid, attrs in items:
        print("making item:", objectid)
        #style
        if "style" in attrs:
            style = lessc(rule.format(id=objectid, style=attrs.pop("style")))
            if args.debug:
                print(style)
            css.write(style)
        #content
        try:
            attrs["content"] = compile_items(attrs["content"].items(), css)
            #will work if it's any type of dict, and won't otherwise
        except AttributeError:
            if "\n" in attrs["content"]:
                attrs["content"] = markdown.markdown(attrs["content"])
            attrs["content"] = attrs["content"].format(form=form.replace("{name}", filename))
        #type
        if "tab" not in attrs["type"]:
            objectid += "-bubble"
            attrs["type"] += " bubble"
        else:
            objectid += "-tab"

        #end
        content += item.format(id=objectid, **attrs)
    return content

def compile_file(path, dest):
    """
    outputed file is writted to dest ignoring the path subdirectories
    to output to a subdirectory, pass dest accordingly
    """
    global filename
    filename = path.split(os.sep)[-1]
    try:
        pagename, extension = filename.rsplit(".", 1)
    except ValueError:
        print("filename't look right and can't be processed correctly. is it a dirrectory? Skipping")
        return False
    pageinfo = None
    if extension == "json":
        pageinfo = json.load(open(path))
        print("loading", filename, "as JSON")
    elif extension == "yaml":
        pageinfo = yaml.load(open(path), OrderedDictYAMLLoader)
        print("loading", filename, "as YAML")
    else:
        print("unknown extension", extension + ", skipping file", filename)
        return False
    #start actually compiling
    print("opening css")
    css = open(args.dest + os.sep + "css" + os.sep + pagename + ".css", "w")
    open("temp.less", 'w').write(pageinfo.pop("less", "") + "\n\n")
    css.write(lessc(pageinfo.pop("CSS", "")) + "\n")
    pagetitle = pageinfo.pop("title")
    htmlcontent = compile_items(pageinfo.items(), css)
    print("writing html")
    f = open(dest + os.sep + pagename + ".html", "w")
    f.write(frame.format(
        title=pagetitle,
        stylesheet=pagename + ".css",
        header=header,
        footer=footer,
        content=htmlcontent,
    ))
    f.flush()
    f.close()
    print("closing css")
    css.close()
    return True

def compile_files(filetree):
    """
    compiles a tree
    """
    global processed
    set_trace()
    for folder in reversed(filetree):
        foldername, subfolders, files = folder
        print("descending into", foldername)
        if "/" in foldername:
            foldername.replace
            os.mkdir(foldername.replace(args.source, args.dest))
        for filename in files:
            print("compiling", filename)
            processed += int(compile_file(
                foldername + os.sep + filename,
                args.dest + os.sep + os.sep.join(foldername.split(os.sep)[1:])
            ))

if __name__ == "__main__":
    args = parser.parse_args()

    frame = set_root(open("templates/frame.html").read())
    item = open("templates/item.html").read()
    rule = open("templates/rule.css").read()

    header = set_root(open("other/headers/" + args.header + ".html").read())
    footer = set_root(open("other/footer.html").read())
    form = open("other/form.html").read()
    if not args.debug:
        set_trace = lambda :None
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
        else:
            print("not copying nonhtml files because -d")
        print("making css")
        os.mkdir(args.dest + os.sep + "css")
    if args.less_copy:
        fname = args.root_less + ".less"
        print("less is compiling", fname)
        destname = args.dest + os.sep + "css" + os.sep + "root.css"
        arg = ""
        if args.compress:
            arg = "--compress"
            print("compressing less")
        call(["lessc", arg, "less" + os.sep + fname, destname])
    else:
        print("not copying nonhtml files because -k")
        try:
            print("making output and css folder:", args.dest)
            os.mkdir(args.dest)
            os.mkdir(args.dest + os.sep + "css")
        except OSError:
            print("it already exists")

    global processed
    processed = 0
    if "." in args.source:
        args.source = os.path.relpath(args.source)
        print("compiling one file", args.source)
        path = args.source.split(os.sep)
        dest = args.dest
        if len(path) > 2:
            dest = os.sep.join([args.dest] + path[1:-1])
        processed += int(compile_file(args.source, dest))
    else:
        filetree = list(os.walk(args.source))
        print("source files in folder:")
        pprint(filetree)
        compile_files(filetree)

    try:
        os.remove("temp.less")
    except OSError:
        print("no files were copied. is this ok?")
    print("DONE - compiled", processed, "file(s)\n\n\n")
