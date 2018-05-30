import os,sys

def convert(prefix, label_file, outfile):
    fout = open(outfile, 'w')
    with open(label_file, 'r') as lf:
        for line in lf.readlines():
            itms = line.strip().split(' ')
            with open(itms[1], 'r') as f:
                lab_lines = f.readlines()
                if len(lab_lines) > 0: 
                    fout.write("{} {}".format(os.path.join(prefix, itms[0]), len(lab_lines)))
                    for wl in lab_lines:
                        fout.write(" {}".format(' '.join(wl.strip().split(' ')[1:])))
            fout.write("\n")
    fout.close()

if __name__ == "__main__" :
    prefix = os.getcwd()
    convert(prefix, sys.argv[1], sys.argv[2])
