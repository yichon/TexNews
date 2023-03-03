import re
from news import NewsPage
import fileinput
import sys


tex_file = "/home/yichoz/1/Projects/tex/daily/2023/summary/nocc_2023_summary.tex"


addr = ""
host = ""

console_stdout = sys.stdout  # Save a reference to the original standard output

# print("hello", file=console_stdout)

def do_test():
    global tex_file, addr, host
    print(tex_file)

    with open(tex_file, encoding="utf-8") as f:
        data = f.read()
        ptn = re.compile(r'%%%(https://.*)')
        s_r = ptn.search(data)
        if s_r:
            addr = s_r.group(1)

        s_r = re.compile(r"(https://)([^/]+)/").search(addr)
        if s_r is not None:
            host = s_r.group(2)

        print(addr)
        print(host)
        print("\n")

        # f.write()

        # page = ReutersPage(addr)
        # tex = page.get_tex()
        # print(tex)





def do_replace():
    with fileinput.FileInput(tex_file, inplace=True, backup='.bak') as f:
        file_stdout = sys.stdout
        sys.stdout = console_stdout

        for line in f:
            ptn = re.compile(r'%%%(https://.*)')
            s_r = ptn.search(line)
            if s_r:
                addr = s_r.group(1)
                print("<" + addr + ">", file=console_stdout)
                page = NewsPage.get(addr)
                tex = page.get_tex()
                if tex:
                    print(tex, file=console_stdout)
                    # print(line)
                    print(tex)
                else:
                    print(line, end="")
            else:
                print(line, end="")




def read_file(file):
    data = ""
    fr = None
    try:
        fr = open(file, "r", encoding="utf-8")
        data = fr.read()
    except:
        pass
    finally:
        if fr is not None:
            fr.close()
            print("File Read Closed. \n")
    return data


def write_file(file, data):
    fw = None
    try:
        fw = open(file, "w", encoding="utf-8")
        fw.write(data)
    except:
        pass
    finally:
        if fw is not None:
            fw.close()
            print("File Write Closed. \n")



def do_replace2():
    def callback(mo):
        _tex = NewsPage.get(mo.group(1)).setProxyPort(1099).get_tex()
        if _tex is None:
            return mo.group()
        else:
            return _tex
    data = read_file(tex_file)
    # print(data)
    tex = re.sub(r'%%%(https://.*)', callback, data)
    tex = re.compile(r"\\noindent \\\\\n([A-Z*]+)(: \\\\)([\n|\s]+\\subsubsection)")\
        .sub(r'\\subsection{\1:}\n\n\3', tex)
    # tex = re.compile(r"\xa0").sub(r' ', tex)

    print(len(tex), "characters to be written to", "'" + tex_file + "'")
    write_file(tex_file, tex)





if __name__ == '__main__':
    # do_test()
    do_replace2()
    # do_replace3()
    
    
    
