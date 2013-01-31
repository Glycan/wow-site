#!/usr/bin/python3 -i
import pyperclip
def make(name, x, subname=None):
    """
    name -> the Images subdirectory
    x -> number of images
    subname -> what each image name starts with, defaults to name
    """
    s = '\t\t<a href="http://wowballoons.com/Images/{name}/{subname}_{n:02d}_big.jpg" rel="lightbox[images]" title=""><img src="http://wowballoons.com/Images/{name}/{subname}_{n:02d}_small.jpg"></a>\n'
    if not subname:
        subname = name
    data = ""
    for n in range(1, x+1):
        data += s.format(name=name,subname=subname,n=n)
    pyperclip.copy(data)
