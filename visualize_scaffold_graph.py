#!/usr/bin/python3
import sys
import os
import argparse
from shutil import copyfile
from shutil import move
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC

#Log class, use it, not print
class Log:
    text = ""
    def log(self, s):
        self.text += s + "\n"
        print(s)

    def warn(self, s):
        msg = "WARNING: " + s
        self.text += msg + "\n"
        sys.stdout.write(msg)
        sys.stdout.flush()

    def err(self, s):
        msg = "ERROR: " + s + "\n"
        self.text += msg
        sys.stdout.write(msg)
        sys.stdout.flush()

    def print_log(self):
        print(self.text)

    def get_log(self):
        return self.text

log = Log()
path_to_exec_dir = os.path.dirname(os.path.abspath(__file__)) + "/"

class Lib:
    def __init__(self, path, id, name):
        self.path = []
        for p in path:
            self.path.append(os.path.abspath(p))
        self.id = id
        self.color = "#000000"
        self.label = name + "_" + str(id)
        self.name = name + "_" + str(id)

    def fix_graph_file(self):
        if self.name.startswith("scaf"):
            return

        copyfile(self.name + "/graph.gr", "tmp")

        g = open(self.name + "/graph.gr", "w")
        f = open("tmp", "r")

        if not self.name.startswith("rna"):
            f.readline()
            g.write("1\n")
            libinfo = f.readline().split(' ')
            libinfo[2] = self.color
            libinfo[3] = self.label
            g.write(' '.join(libinfo))
            str = f.read()
            g.write(str)
        elif self.name.startswith("rnap"):
            f.readline()
            g.write("3\n")
            libinfo = f.readline().split(' ')
            libinfo[2] = self.color
            libinfo[3] = self.label + "_sp50"
            g.write(' '.join(libinfo))

            libinfo = f.readline().split(' ')
            libinfo[2] = self.color
            libinfo[3] = self.label + "_sp30"
            g.write(' '.join(libinfo))

            libinfo = f.readline().split(' ')
            libinfo[2] = self.color
            libinfo[3] = self.label + "_pair"
            g.write(' '.join(libinfo))

            str = f.read()
            g.write(str)
        else:
            f.readline()
            g.write("2\n")
            libinfo = f.readline().split(' ')
            libinfo[2] = self.color
            libinfo[3] = self.label + "_sp50"
            g.write(' '.join(libinfo))

            libinfo = f.readline().split(' ')
            libinfo[2] = self.color
            libinfo[3] = self.label + "_sp30"
            g.write(' '.join(libinfo))

            str = f.read()
            g.write(str)

        f.close()
        g.close()

libsType = {"rnap", "rnas", "rf", "ff", "scg", "ref", "scafinfo", "scaffolds", "refcoord", "fr", "long", "fastg", "gfa", "frsam", "rfsam", "ffsam"}

class StoreArgAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not 'lib_cnt' in namespace:
            setattr(namespace, 'lib_cnt', 0)
        lib_cnt = namespace.lib_cnt

        if not 'libs' in namespace:
            libs = dict()
            for lib in libsType:
                libs[lib] = []

            setattr(namespace, 'libs', libs)

        libs = namespace.libs
        libs[self.dest].append(Lib(values, lib_cnt, self.dest))

        lib_cnt += 1
        setattr(namespace, 'libs', libs)
        setattr(namespace, 'lib_cnt', lib_cnt)

def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--contigs", "-c", nargs=1, dest="contigs", help="path to contigs", type=str, action='append')
    parser.add_argument("--scaffolds", "-s", nargs=1, dest="scaffolds", help="path to scaffolds in fasta format", type=str, action=StoreArgAction)
    parser.add_argument("--scg", nargs=1, dest="scg", help="path to file with connection list", type=str, action=StoreArgAction)
    parser.add_argument("--fastg", nargs=1, dest="fastg", help="path to assembly graph in FASTG format", type=str, action=StoreArgAction)
    parser.add_argument("--gfa", nargs=1, dest="gfa", help="path to assembly graph in GFA format", type=str, action=StoreArgAction)
    parser.add_argument("--gr", nargs=1, dest="graph", help="path to graph in .gr format", type=str, action='append')
    parser.add_argument("--rna-p", dest="rnap", nargs=2, help="path to rna pair reads file", type=str, action=StoreArgAction)
    parser.add_argument("--rna-s", dest="rnas", nargs=1, help="path to rna read file", type=str, action=StoreArgAction)

    parser.add_argument("--fr", dest="fr", nargs=2, help="path to forward-reverse paired reads file", type=str, action=StoreArgAction)
    parser.add_argument("--rf", dest="rf", nargs=2, help="path to reverse-forward paired reads file", type=str, action=StoreArgAction)
    parser.add_argument("--ff", dest="ff", nargs=2, help="path to forward-forward paired reads file", type=str, action=StoreArgAction)

    parser.add_argument("--fr_sam", dest="frsam", nargs=2, help="path to alignment of forward-reverse paired reads file in SAM/BAM format", type=str, action=StoreArgAction)
    parser.add_argument("--rf_sam", dest="rfsam", nargs=2, help="path to alignment of reverse-forward paired reads file in SAM/BAM format", type=str, action=StoreArgAction)
    parser.add_argument("--ff_sam", dest="ffsam", nargs=2, help="path to alignment of forward-forward paired reads file in SAM/BAM format", type=str, action=StoreArgAction)

    parser.add_argument("--long", dest="long", nargs=1, help="path to long reads(PacBio/Oxford Nanopore) file", type=str, action=StoreArgAction)
    parser.add_argument("--local_output_dir", "-o", nargs=1, help="use this output dir", type=str)
    parser.add_argument("--ref", dest="ref", nargs=1, help="path to reference", type=str, action=StoreArgAction)
    parser.add_argument("--refcoord", dest="refcoord", nargs=2, help="path to ref and to alignment of contigs to reference in coord format", type=str, action=StoreArgAction)
    parser.add_argument("--scafinfo", nargs=1, help="path to .info file with info about scaffolds", type=str, action=StoreArgAction)
    parser.add_argument("--label", "-l", nargs='*', help="list with labels for all libs in definition order", type=str, action='store')
    parser.add_argument("--color", nargs='*', help="list with color for all libs in definition order", type=str, action='store')
    args = parser.parse_args()
    return args

def alig_split(lib_name, reads, flag):
    prevdir = os.getcwd()
    log.log("START ALIG: " + lib_name)
    lib_dir = os.path.dirname(os.path.abspath(lib_name) + "/")
    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir)
    os.chdir(lib_dir)

    os.system(path_to_exec_dir + "readSplitter " + str(flag) + " " + reads + " reads1.fasta reads2.fasta")
    os.system("STAR --runThreadN 20 --genomeDir ../genomeDir --readFilesIn reads1.fasta")
    os.system("mv Aligned.out.sam rna1.sam")
    os.system("STAR --runThreadN 20 --genomeDir ../genomeDir --readFilesIn reads2.fasta")
    os.system("mv Aligned.out.sam rna2.sam")
    os.chdir(prevdir)

def alig_pair_rna_reads(rnap):
    prevdir = os.getcwd()
    log.log("START ALIG: " + rnap.label)
    lib_dir = os.path.dirname(os.path.abspath(rnap.name) + "/")
    os.chdir(lib_dir)

    unm1 = ""
    unm2 = ""

    os.system("STAR --runThreadN 4 --genomeDir ../genomeDir --outReadsUnmapped Fastx --readFilesIn " + rnap.path[0])
    os.system("mv Aligned.out.sam rna1.sam")
    if rnap.path[0][-1] == "q":
        os.system("mv Unmapped.out.mate1 Unmapped1.fastq")
        unm1 = "../" + rnap.name + "/Unmapped1.fastq"
    else:
        os.system("mv Unmapped.out.mate1 Unmapped1.fasta")
        unm1 = "../" + rnap.name + "/Unmapped1.fasta"

    os.system("STAR --runThreadN 4 --genomeDir ../genomeDir --outReadsUnmapped Fastx --readFilesIn " + rnap.path[1])
    os.system("mv Aligned.out.sam rna2.sam")

    if rnap.path[1][-1] == "q":
        os.system("mv Unmapped.out.mate1 Unmapped2.fastq")
        unm2 = "../" + rnap.name + "/Unmapped2.fastq"
    else:
        os.system("mv Unmapped.out.mate1 Unmapped2.fasta")
        unm2 = "../" + rnap.name + "/Unmapped2.fasta"

    os.chdir(prevdir)

    alig_split(rnap.name + "_50_1", unm1, 0)
    alig_split(rnap.name + "_50_2", unm2, 0)
    alig_split(rnap.name + "_30_1", "../" + rnap.name + "/rna1.sam", 1)
    alig_split(rnap.name + "_30_2", "../" + rnap.name + "/rna2.sam", 1)

def alig_pair_dna_reads(dnap, contig_file_name):
    prevdir = os.getcwd()
    log.log("START ALIG: " + dnap.label)
    lib_dir = os.path.dirname(os.path.abspath(dnap.name) + "/")
    os.chdir(lib_dir)

    os.system("minimap2 -t 16 -ax sr " + contig_file_name + " " + dnap.path[0] + " > dna1.sam")
    os.system("minimap2 -t 16 -ax sr " + contig_file_name + " " + dnap.path[1] + " > dna2.sam")

    #os.system("bowtie2-build " + contig_file_name + " contig")
    #if dnap.path[0].endswith(".fa") or dnap.path[0].endswith(".fasta") or dnap.path[0].endswith(".mfa") or dnap.path[0].endswith(".fna"):
    #    os.system("bowtie2 -x contig -f --ignore-quals -U " + dnap.path[0] + " -S dna1.sam")
    #    os.system("bowtie2 -x contig -f --ignore-quals -U " + dnap.path[1] + " -S dna2.sam")
    #else:
    #    os.system("bowtie2 -x contig -U " + dnap.path[0] + " -S dna1.sam")
    #    os.system("bowtie2 -x contig -U " + dnap.path[1] + " -S dna2.sam")
    os.chdir(prevdir)

def alig_long(long, contig_file_name):
    prevdir = os.getcwd()
    log.log("START ALIG: " + long.label)
    lib_dir = os.path.dirname(os.path.abspath(long.name) + "/")
    os.chdir(lib_dir)

    os.system("minimap2 -t 16 -x map-pb " + contig_file_name + " " + long.path[0] + " > out.paf")

    os.chdir(prevdir)

def alig_single_rna_reads(rnas):
    prevdir = os.getcwd()
    lib_name = rnas.name + "_50"
    lib_dir = os.path.dirname(os.path.abspath(lib_name) + "/")
    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir)
    os.chdir(lib_name)
    unm = ""
    os.system("STAR --runThreadN 4 --genomeDir ../genomeDir --outReadsUnmapped Fastx --readFilesIn " + rnas)
    os.system("mv Aligned.out.sam rna.sam")
    if rnas.path[0][-1] == "q":
        os.system("mv Unmapped.out.mate1 Unmapped.fastq")
        unm = "Unmapped.fastq"
    else:
        os.system("mv Unmapped.out.mate1 Unmapped.fasta")
        unm = "Unmapped.fasta"

    os.chdir(prevdir)
    alig_split(lib_name, unm, 0)
    alig_split(rnas.name + "_30", "../" + rnas.name + "_30/rna.sam", 1)
    return

def alig_reads(contig_file_name, args):
    genome_dir = "genomeDir"
    gen_dir = os.path.dirname(os.path.abspath(genome_dir) + "/")
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir)

    try:
        if (len(args.libs["rnap"]) > 0 or len(args.libs["rnas"]) > 0):
            log.log("STAR --runMode genomeGenerate --genomeDir genomeDir --runThreadN 20 --genomeSAindexNbases 10 --genomeFastaFiles " +
                    contig_file_name + " --limitGenomeGenerateRAM 90000000000 --genomeChrBinNbits 15")
            os.system("STAR --runMode genomeGenerate --genomeDir genomeDir --runThreadN 20 --genomeSAindexNbases 10 --genomeFastaFiles " +
                      contig_file_name + " --limitGenomeGenerateRAM 90000000000 --genomeChrBinNbits 15")
    except:
        log.err(sys.exc_info()[0])
        return

    for i in range(len(args.libs["rnap"])):
        alig_pair_rna_reads(args.libs["rnap"][i])

    for i in range(len(args.libs["fr"])):
        alig_pair_dna_reads(args.libs["fr"][i], contig_file_name)

    for i in range(len(args.libs["rf"])):
        alig_pair_dna_reads(args.libs["rf"][i], contig_file_name)

    for i in range(len(args.libs["ff"])):
        alig_pair_dna_reads(args.libs["ff"][i], contig_file_name)

    for i in range(len(args.libs["long"])):
        alig_long(args.libs["long"][i], contig_file_name)

    for i in range(len(args.libs["rnas"])):
        alig_single_rna_reads(args.libs["rnas"][i])

    return

def runGraphBuilder(lib_name, prevdir, type, label):
    log.log("START BUILD GRAPH: " + lib_name)
    lib_dir = os.path.dirname(os.path.abspath(lib_name) + "/")
    os.chdir(lib_dir)
    os.system(path_to_exec_dir + "build " + type + " rna1.sam rna2.sam " + label)
    os.chdir(prevdir)
    return

def build_graph(contig_file_name, args):
    for lib in args.libs["rnap"]:
        prevdir = os.getcwd()
        runGraphBuilder(lib.name, prevdir, "RNA_PAIR", lib.label)
        runGraphBuilder(lib.name + "_50_1", prevdir, "RNA_SPLIT_50", lib.label)
        runGraphBuilder(lib.name + "_50_2", prevdir, "RNA_SPLIT_50", lib.label)
        runGraphBuilder(lib.name + "_30_1", prevdir, "RNA_SPLIT_30", lib.label)
        runGraphBuilder(lib.name + "_30_2", prevdir, "RNA_SPLIT_30", lib.label)

    for lib in args.libs["rnas"]:
        prevdir = os.getcwd()
        runGraphBuilder(lib.name + "_50", prevdir, "RNA_SPLIT_50", lib.label)
        runGraphBuilder(lib.name + "_30", prevdir, "RNA_SPLIT_30", lib.label)

    for lib in args.libs["fr"]:
        prevdir = os.getcwd()
        log.log("START BUILD GRAPH: " + lib.label)
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        os.chdir(lib_dir)
        os.system(path_to_exec_dir + "build DNA_PAIR_FR dna1.sam dna2.sam " + lib.label)
        os.chdir(prevdir)

    for lib in args.libs["rf"]:
        prevdir = os.getcwd()
        log.log("START BUILD GRAPH: " + lib.label)
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        os.chdir(lib_dir)
        os.system(path_to_exec_dir + "build DNA_PAIR_RF dna1.sam dna2.sam " + lib.label)
        os.chdir(prevdir)

    for lib in args.libs["ff"]:
        prevdir = os.getcwd()
        log.log("START BUILD GRAPH: " + lib.label)
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        os.chdir(lib_dir)
        os.system(path_to_exec_dir + "build DNA_PAIR_FF dna1.sam dna2.sam " + lib.label)
        os.chdir(prevdir)


    for lib in args.libs["frsam"]:
        prevdir = os.getcwd()
        log.log("START BUILD GRAPH: " + lib.label)
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        os.chdir(lib_dir)
        os.system(path_to_exec_dir + "build DNA_PAIR_FR " + lib.path[0] + " " + lib.path[1]  + " " + lib.label)
        os.chdir(prevdir)

    for lib in args.libs["rfsam"]:
        prevdir = os.getcwd()
        log.log("START BUILD GRAPH: " + lib.label)
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        os.chdir(lib_dir)
        os.system(path_to_exec_dir + "build DNA_PAIR_RF " + lib.path[0] + " " + lib.path[1]  + " " + lib.label)
        os.chdir(prevdir)

    for lib in args.libs["ffsam"]:
        prevdir = os.getcwd()
        log.log("START BUILD GRAPH: " + lib.label)
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        os.chdir(lib_dir)
        os.system(path_to_exec_dir + "build DNA_PAIR_FF " + lib.path[0] + " " + lib.path[1]  + " " + lib.label)
        os.chdir(prevdir)


    for lib in args.libs["long"]:
        prevdir = os.getcwd()
        log.log("START BUILD GRAPH: " + lib.label)
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        os.chdir(lib_dir)
        os.system(path_to_exec_dir + "build LONG out.paf " + contig_file_name + " " + lib.label)
        os.chdir(prevdir)

    for lib in args.libs["scg"]:
        prevdir = os.getcwd()
        log.log("START BUILD GRAPH: " + lib.label)
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        os.chdir(lib_dir)
        os.system(path_to_exec_dir + "build CONNECTION " + lib.path[0] + " " + contig_file_name + " " + lib.label)
        os.chdir(prevdir)

    for lib in args.libs["fastg"]:
        prevdir = os.getcwd()
        log.log("START BUILD GRAPH: " + lib.label)
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        os.chdir(lib_dir)
        os.system(path_to_exec_dir + "build FASTG " + lib.path[0] + " " + contig_file_name + " " + lib.label)
        os.chdir(prevdir)

    for lib in args.libs["gfa"]:
        prevdir = os.getcwd()
        log.log("START BUILD GRAPH: " + lib.label)
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        os.chdir(lib_dir)
        os.system(path_to_exec_dir + "build GFA " + lib.path[0] + " " + lib.label)
        os.chdir(prevdir)
        
    return

def merge_lib_rna(libs):
    f = open("filter_config", 'w')
    f.write("uploadGraph graph.gr\n")
    f.write("mergeLib 2 0 sp_50\n")
    f.write("mergeLib 3 1 sp_30\n")
    f.write("print graph.gr\n")
    f.write("exit\n")
    f.close()

    for lib in libs:
        os.system(path_to_exec_dir + "mergeGraph " +
                  lib.name + "_50_1/graph.gr " +
                  lib.name + "_30_1/graph.gr " +
                  lib.name + "_50_2/graph.gr " +
                  lib.name + "_30_2/graph.gr " +
                  lib.name + "/graph.gr " +
                  lib.name + "/gr.gr")

        copyfile(lib.name + "/gr.gr", lib.name + "/graph.gr")
        prevdir = os.getcwd()
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        os.chdir(lib_dir)
        os.system(path_to_exec_dir + "filter " + os.path.abspath("../filter_config"))
        os.chdir(prevdir)
    return

def merge_graph(args):
    if 'libs' in args:
        merge_lib_rna(args.libs["rnap"])

    merge_list = ""

    if 'libs' in args:
        for lib_type in libsType:
            for lib in args.libs[lib_type]:
                if lib_type == "rnap" or lib_type == "rnas" or lib_type == "fr" or lib_type == "rf" or \
                        lib_type == "long" or lib_type == "ff" or lib_type == "scg" or lib_type=="fastg" \
                        or lib_type=="gfa" or lib_type == "frsam" or lib_type == "rfsam" or lib_type == "ffsam":
                    lib.fix_graph_file()
                    if lib_type != "rnas":
                        merge_list += lib.name + "/graph.gr "
                    else:
                        merge_list += lib.name + "_50/graph.gr "
                        merge_list += lib.name + "_30/graph.gr "

    if args.graph != None:
        for gr in args.graph:
            merge_list += gr + " "

    merge_list += "graph.gr"
    os.system(path_to_exec_dir + "mergeGraph " + merge_list)
    return

idbyname = dict()
lenbyid = []
cntedge = 0
cntlib = 0

#save id to idbyname
#write node info to data
def gen_id_from_contig_file(contig_file_name, f):
    fasta_seq = SeqIO.parse(open(contig_file_name), 'fasta')
    id = 0
    nodestr = "var scaffoldnodes = ["
    for fasta in fasta_seq:
        name, lenn = fasta.id, len(fasta.seq.tostring())
        idbyname[name] = id
        idbyname[name + "-rev"] = id + 1
        lenbyid.append(lenn)
        lenbyid.append(lenn)
        if (id != 0):
            nodestr += ', '
        nodestr += "new ScaffoldNode(" + str(id) + ", '" + name + "', " + str(lenn) + "), "
        nodestr += "new ScaffoldNode(" + str(id + 1) + ", '" + name + "-rev', " + str(lenn) + ")"
        id += 2
    nodestr += "];"
    f.write(nodestr)


def save_scaffolds_from_info(lib, f):
    global cntedge
    global cntlib
    global idbyname
    with open(lib.path[0]) as g:
        f.write("scaffoldlibs.push(new ScaffoldEdgeLib(" + str(cntlib) + ", '" + str(lib.color) + "', '" + str(lib.label) + "', 'SCAFF'));\n")

        scafnum = 0

        for line in g:
            tokens = line.split(" ")
            if (tokens[len(tokens) - 1] == '\n'):
                tokens.pop()

            f.write("scaffoldlibs["+ str(cntlib) +"].scaffolds.push(new Scaffold('" + tokens[0][1:] + "'));\n")
            f.write("scaffoldlibs["+ str(cntlib) +"].scaffolds.push(new Scaffold('" + tokens[0][1:] + "-rev'));\n")

            nodeslist = []
            for i in range(1, len(tokens), 3):
                nm = tokens[i][1:]
                if (tokens[i + 2][0] == '+'):
                    nodeslist.append(idbyname[nm])
                else:
                    nodeslist.append(idbyname[nm]^1)


            for i in range(1, len(nodeslist)):
                f.write("scaffoldedges.push(new ScaffoldEdge(" + str(cntedge) + ", "+ str(nodeslist[i - 1]) +
                        ", " + str(nodeslist[i]) + ", " + str(cntlib) + ", 1));\n")
                f.write("scaffoldedges["+str(cntedge)+"].name='"+ tokens[0][1:] + "';\n")
                f.write("scaffoldlibs["+ str(cntlib) +"].scaffolds["+str(scafnum) +"].edges.push(scaffoldedges["+str(cntedge)+"]);\n")
                cntedge += 1

            for i in range(len(nodeslist)-2, -1, -1):
                f.write("scaffoldedges.push(new ScaffoldEdge(" + str(cntedge) + ", "+ str(nodeslist[i + 1]^1) +
                        ", " + str(nodeslist[i]^1) + ", " + str(cntlib) + ", 1));\n")
                f.write("scaffoldedges["+str(cntedge)+"].name='"+ tokens[0][1:] + "-rev';\n")
                f.write("scaffoldlibs["+ str(cntlib) +"].scaffolds["+str(scafnum+1) +"].edges.push(scaffoldedges["+str(cntedge)+"]);\n")
                cntedge += 1

            scafnum += 2
    cntlib += 1


def sortcmp(x, y):
    if (x[0] < y[0]):
        return -1
    if (x[0] == y[0] and x[1] > y[1]):
        return -1
    if (x[0] == y[0] and x[1] == y[1]):
        return 0
    return 1

def save_scaffolds_from_fasta(contig_file_name, lib, f):
    prevdir = os.getcwd()
    lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
    os.chdir(lib_dir)
    os.system("nucmer " + lib.path[0] + " " + contig_file_name)
    os.system("show-coords out.delta -THrgl > out.coords")

    global cntedge
    global cntlib
    global idbyname
    with open("out.coords") as g:
        f.write("scaffoldlibs.push(new ScaffoldEdgeLib(" + str(cntlib) + ", '" + str(lib.color) + "', '" + str(lib.label) + "', 'SCAFF'));\n")

        contigsAlignment = dict()
        rcontlist = []

        for line in g:
            tokens = line.split("\t")
            print(tokens)
            if (tokens[len(tokens) - 1] == '\n'):
                tokens.pop()
            if (tokens[len(tokens) - 1][-1] == '\n'):
                tokens[len(tokens) - 1] = tokens[len(tokens) - 1][0:-1]

            lq = int(tokens[2])
            rq = int(tokens[3])
            l = int(tokens[0])
            r = int(tokens[1])
            qcont = tokens[10]
            rcont = tokens[9]
            chrlen = int(tokens[7])
            if (lq > rq):
                qcont += "-rev"
                lq, rq = rq, lq

            id = idbyname[qcont]
            if (lq < 2 and rq > lenbyid[id] - 2):
                if (rcont not in contigsAlignment):
                    rcontlist.append(rcont)
                    rcontlist.append(rcont + "-rev")
                    contigsAlignment[rcont] = []
                    contigsAlignment[rcont + "-rev"] = []

                contigsAlignment[rcont].append((l, r, id))
                contigsAlignment[rcont + "-rev"].append((chrlen - r, chrlen - l, id^1))


        scafnum = 0
        for rc in rcontlist:
            contigsAlignment[rc].sort(key=lambda x: (x[0], -x[1]))
            f.write("scaffoldlibs["+ str(cntlib) +"].scaffolds.push(new Scaffold('" + rc + "'));\n")

            lst = 0
            for i in range(1, len(contigsAlignment[rc])):
                if (contigsAlignment[rc][i][0] >= contigsAlignment[rc][lst][1] - 100):
                    f.write("scaffoldedges.push(new ScaffoldEdge(" + str(cntedge) + ", "+ str(contigsAlignment[rc][lst][2]) +
                        ", " + str(contigsAlignment[rc][i][2]) + ", " + str(cntlib) + ", 1));\n")
                    f.write("scaffoldedges["+str(cntedge)+"].name='"+ rc + "';\n")
                    f.write("scaffoldedges["+str(cntedge)+"].len=" + str(contigsAlignment[rc][i][0] - contigsAlignment[rc][lst][1]) + "\n")
                    f.write("scaffoldlibs["+ str(cntlib) +"].scaffolds["+str(scafnum) +"].edges.push(scaffoldedges["+str(cntedge)+"]);\n")
                    cntedge += 1
                    lst = i

            scafnum += 1

        cntlib += 1

    os.chdir(prevdir)


def save_scaffolds_from_gfa(lib, f):
    global cntedge
    global cntlib
    global idbyname
    with open(lib.path[0]) as g:
        f.write("scaffoldlibs.push(new ScaffoldEdgeLib(" + str(cntlib) + ", '" + str(lib.color) + "', '" + str(lib.label) + "', 'SCAFF'));\n")

        scafnum = 0

        for line in g:
            tokens = line.split()
            if (tokens[0] != 'P'):
                continue

            f.write("scaffoldlibs["+ str(cntlib) +"].scaffolds.push(new Scaffold('" + tokens[1] + "'));\n")
            f.write("scaffoldlibs["+ str(cntlib) +"].scaffolds.push(new Scaffold('" + tokens[1] + "-rev'));\n")

            nodeslist = []
            tt = tokens[2].split(',')
            for i in range(0, len(tt)):
                nm = tt[i][:-1]
                if (tt[i][-1] == '+'):
                    nodeslist.append(idbyname[nm])
                else:
                    nodeslist.append(idbyname[nm]^1)


            for i in range(1, len(nodeslist)):
                f.write("scaffoldedges.push(new ScaffoldEdge(" + str(cntedge) + ", "+ str(nodeslist[i - 1]) +
                        ", " + str(nodeslist[i]) + ", " + str(cntlib) + ", 1));\n")
                f.write("scaffoldedges["+str(cntedge)+"].name='"+ tokens[0][1:] + "';\n")
                f.write("scaffoldlibs["+ str(cntlib) +"].scaffolds["+str(scafnum) +"].edges.push(scaffoldedges["+str(cntedge)+"]);\n")
                cntedge += 1

            for i in range(len(nodeslist)-2, -1, -1):
                f.write("scaffoldedges.push(new ScaffoldEdge(" + str(cntedge) + ", "+ str(nodeslist[i + 1]^1) +
                        ", " + str(nodeslist[i]^1) + ", " + str(cntlib) + ", 1));\n")
                f.write("scaffoldedges["+str(cntedge)+"].name='"+ tokens[0][1:] + "-rev';\n")
                f.write("scaffoldlibs["+ str(cntlib) +"].scaffolds["+str(scafnum+1) +"].edges.push(scaffoldedges["+str(cntedge)+"]);\n")
                cntedge += 1

            scafnum += 2
    cntlib += 1


def save_scaffolds(contig_file_name, args, f):
    for lib in args.libs["scafinfo"]:
        save_scaffolds_from_info(lib, f)

    for lib in args.libs["scaffolds"]:
        save_scaffolds_from_fasta(contig_file_name, lib, f)

    for lib in args.libs["gfa"]:
        save_scaffolds_from_gfa(lib, f)


def add_conection_to_res_file(f):
    global cntlib
    global cntedge
    if (not os.path.isfile("graph.gr")):
        return

    with open("graph.gr") as g:
        cntlib = int(g.readline())

        for i in range(cntlib):
            libsinfo = g.readline().split(" ")
            libsinfo[4] = libsinfo[4][:-1]
            f.write("scaffoldlibs.push(new ScaffoldEdgeLib(" + libsinfo[1] + ", '" + libsinfo[2] + "', '" + libsinfo[3] + "', '" + libsinfo[4] + "'));\n")

        nodecnt = int(g.readline())

        for i in range(nodecnt):
            g.readline()

        cntedge = int(g.readline())
        for i in range(cntedge):
            curs = g.readline()
            extraInfo = ""
            if ("\""  in curs):
                extraInfo = curs.split("\"")[1]
            edgesinfo = curs.split()
            f.write("scaffoldedges.push(new ScaffoldEdge(" + edgesinfo[1] + ", " + edgesinfo[2] + ", " + edgesinfo[3] + ", " + edgesinfo[4] + ", " + edgesinfo[5] + "));\n")
            f.write("scaffoldedges[" + str(i) + "].len=" + str(edgesinfo[6]) + ";\n")
            f.write("scaffoldedges[" + str(i) + "].info=\"" + extraInfo + "\";\n")

def add_refcoord_to_res_file(contig_file_name, f):
    if (len(args.libs["refcoord"]) == 0):
        return

    lib = args.libs["refcoord"][0]

    chrid = {}
    chrlen = []
    chrlist = []
    chralig = []
    fasta_seq = SeqIO.parse(open(lib.path[0]), 'fasta')
    curid = 0

    for fasta in fasta_seq:
        name, lenn = fasta.id, len(fasta.seq.tostring())
        print(name)
        chrid[name] = curid
        chrid[name + "-rev"] = curid + 1
        chrlen.append(lenn)
        chrlen.append(lenn)
        chrlist.append("new Chromosome(" + str(curid) + ", '" + name + "', " + str(lenn) + ")")
        chrlist.append("new Chromosome(" + str(curid + 1) + ", '" + name + "-rev', " + str(lenn) + ")")
        chralig.append([])
        chralig.append([])
        curid += 2

    global idbyname
    global lenbyid

    lastname = '-'
    #TODO: del file
    g = open("out.coords", "w")

    with open(lib.path[1]) as cf:
        for line in cf:
            if ("[S1]     [E1]  |     [S2]     [E2]  |  [LEN 1]  [LEN 2]  |  [% IDY]  | [TAGS]" in line or "====" in line):
                continue
            info = line.split(" ")
            info[-1] = info[-1][:-1]
            print(info)
            vid = idbyname[info[12]]
            curid = chrid[info[11].split('_')[0]]
            lq = int(info[3])
            rq = int(info[4])
            l = int(info[0])
            r = int(info[1])
            lenf = chrlen[curid]
            if ((max(rq, lq) - min(rq, lq)) * 100 < lenbyid[vid]):
                continue
            if (lq > rq):
                vid ^= 1

            chralig[curid].append("new Alignment(" + str(l) + ", " + str(r) + ", " + str(curid) + ", " + str(vid) + ")")
            chralig[curid + 1].append("new Alignment(" + str(lenf - r) + ", " + str(lenf - l) + ", " + str(curid + 1) + ", " + str(vid^1) + ")")
            g.write(str(l) + " " + str(r) + " " + str(lq) + " " + str(rq) + " 0 0 0 " + str(lenf) + " 0 " + info[11].split('_')[0] + " " + info[12] + "\n")

    g.close()

    for i in range(len(chrlist)):
        f.write("chromosomes.push(" + chrlist[i] + ");\n")

    for i in range(len(chrlist)):
        f.write("chromosomes[" + str(i) + "].alignments = " + "[")
        for j in range(len(chralig[i])):
            f.write(chralig[i][j])
            if (j != len(chralig[i]) - 1):
                f.write(", ")
        f.write("];\n")
    
def getRefFileName(fileName):
    return fileName.split('/')[-1].split('.')[0]


def merge_ref_files(ref_libs):
    if (len(ref_libs) == 1):
        return ref_libs[0]

    with open("ref_merge.fasta", "w") as out:
        for i in range(len(ref_libs)):
            for record in SeqIO.parse(ref_libs[i].path[0], "fasta"):
                record.id = getRefFileName(ref_libs[i].path[0]) + "_" + record.id
                SeqIO.write(record, out, "fasta")

    return Lib([os.path.abspath("ref_merge.fasta")], "ref", "ref")

def add_ref_to_res_file(contig_file_name, f):
    if (len(args.libs["ref"]) == 0):
        return

    lib = merge_ref_files(args.libs["ref"])

    prevdir = os.getcwd()
    lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
    os.chdir(lib_dir)
    os.system("nucmer -b 10000 " + lib.path[0] + " " + contig_file_name)
    os.system("show-coords out.delta -THrgl > out.coords")

    global idbyname
    global lenbyid

    chrlist = []
    chralig = []

    curid = -2
    lastname = '-'

    with open("out.coords") as cf:
        for line in cf:
            info = line.split("\t")
            info[10] = info[10][:-1]
            vid = idbyname[info[10]]
            chrname = info[9]
            lenf = int(info[7])
            if (chrname != lastname):
                curid += 2
                chrlist.append("new Chromosome(" + str(curid) + ", '" + chrname + "', " + str(lenf) + ")")
                chrlist.append("new Chromosome(" + str(curid + 1) + ", '" + chrname + "-rev', " + str(lenf) + ")")
                chralig.append([])
                chralig.append([])
                lastname = chrname

            lq = int(info[2])
            rq = int(info[3])
            l = int(info[0])
            r = int(info[1])


            if ((max(rq, lq) - min(rq, lq)) * 100 < lenbyid[vid]):
                continue
            
            if (lq > rq):
                vid ^= 1
   

            chralig[curid].append("new Alignment(" + str(l) + ", " + str(r) + ", " + str(curid) + ", " + str(vid) + ")")
            chralig[curid + 1].append("new Alignment(" + str(lenf - r) + ", " + str(lenf - l) + ", " + str(curid + 1) + ", " + str(vid^1) + ")")

    for i in range(len(chrlist)):
        f.write("chromosomes.push(" + chrlist[i] + ");\n")

    for i in range(len(chrlist)):
        f.write("chromosomes[" + str(i) + "].alignments = " + "[")
        for j in range(len(chralig[i])):
            f.write(chralig[i][j])
            if (j != len(chralig[i]) - 1):
                f.write(", ")
        f.write("];\n")

    os.chdir(prevdir)


def merge_contigs(contigs):
    with open("contigs_merge.fasta", "w") as out:
        for i in range(len(contigs)):
            for record in SeqIO.parse(contigs[i], "fasta"):
                SeqIO.write(record, out, "fasta")

    return os.path.abspath("contigs_merge.fasta")

def fastg_to_contigs(args):
    for lib in args.libs['fastg']:
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        if not os.path.exists(lib_dir):
            os.makedirs(lib_dir)
        prevdir = os.getcwd()
        os.chdir(lib_dir)

        with open("contigs.fasta", "w") as out:
            for record in SeqIO.parse(lib.path[0], "fasta"):
                record.id = record.id.split(':')[0].split(';')[0]
                if (record.id[-1] != '\''):
                    SeqIO.write(record, out, "fasta")

        if (args.contigs == None):
            args.contigs = []

        args.contigs.append(os.path.abspath('contigs.fasta'))
        os.chdir(prevdir)


def gfa_to_contigs(args):
    for lib in args.libs['gfa']:
        lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
        if not os.path.exists(lib_dir):
            os.makedirs(lib_dir)
        prevdir = os.getcwd()
        os.chdir(lib_dir)

        with open("contigs.fasta", "w") as out:
            lines = [line.rstrip('\n') for line in open(lib.path[0])]
            for line in lines:
                parts = line.split()
                if (parts[0] == 'S'):
                    record = SeqRecord(Seq(parts[2], IUPAC.ambiguous_dna), id=parts[1])
                    SeqIO.write(record, out, "fasta")

        if (args.contigs == None):
            args.contigs = []

        args.contigs.append(os.path.abspath('contigs.fasta'))
        os.chdir(prevdir)


def run(args):
    if args.contigs == None and ('libs' not in args) and ('fastg' not in args.libs)  and ('gfa' not in args.libs):
        log.err("none contig/FASTG/GFA file provide")
        return

    if (args.contigs != None):
        for i in range(len(args.contigs)):
            args.contigs[i] = os.path.abspath(args.contigs[i][0])

    main_out_dir = os.path.abspath(".") + "/"

    if args.local_output_dir != None:
        main_out_dir = os.path.abspath(args.local_output_dir[0]) + "/"

    if args.graph != None:
        for i in range(len(args.graph)):
            args.graph[i] = os.path.abspath(args.graph[i][0])

    out_dir = main_out_dir + "tmp/"
    log.log("OUTPUT DIR: " + out_dir)
    directory = os.path.dirname(out_dir)
    if not os.path.exists(directory):
        log.log("MKDIR")
        os.makedirs(directory)
    os.chdir(directory)

    if 'libs' in args:
        fastg_to_contigs(args)
        gfa_to_contigs(args)

    contig_file_name = ""
    if (len(args.contigs) == 1):
        contig_file_name = args.contigs[0]
    else:
        contig_file_name = merge_contigs(args.contigs)

    if args.color != None and len(args.color) != args.lib_cnt:
        log.err("wrong number of color provide, lib cnt = " + str(args.lib_cnt) + " color cnt = " + str(len(args.color)))

    if args.label != None and len(args.label) != args.lib_cnt:
        log.err("wrong number of labels provide")

    if 'libs' in args:
        for lib_type in libsType:
            for lib in args.libs[lib_type]:
                lib_dir = os.path.dirname(os.path.abspath(lib.name) + "/")
                if not os.path.exists(lib_dir):
                    os.makedirs(lib_dir)

                if args.color != None:
                    lib.color = args.color[lib.id]
                if args.label != None:
                    lib.label = args.label[lib.id]

        if (not os.path.exists(os.path.dirname(os.path.abspath("ref_ref") + "/"))):
            os.makedirs(os.path.dirname(os.path.abspath("ref_ref") + "/"))
        alig_reads(contig_file_name, args)
        build_graph(contig_file_name, args)

    merge_graph(args) #result file graph.gr

    f = open("data.js", 'w')
    gen_id_from_contig_file(contig_file_name, f)
    f.write("var scaffoldlibs = [];\n")
    f.write("var scaffoldedges = [];\n")
    f.write("var chromosomes = [];\n")
    add_conection_to_res_file(f)
    if 'libs' in args:
        save_scaffolds(contig_file_name, args, f)
        add_ref_to_res_file(contig_file_name, f)
        add_refcoord_to_res_file(contig_file_name, f)

    f.write("var scaffoldgraph = new ScaffoldGraph(scaffoldlibs, scaffoldnodes, scaffoldedges);\n")
    f.close()

    directory = os.path.dirname(main_out_dir)
    os.chdir(directory)

    os.system("cp -r " + path_to_exec_dir + "/scripts ./")
    move("tmp/data.js", "./scripts/data.js")
    os.system("cp " + path_to_exec_dir + "/mainPage.html ./main.html")
    return

args = parse_args()
run(args)