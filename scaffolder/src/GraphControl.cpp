//
// Created by olga on 08.10.16.
//

#include "GraphControl.h"
#include "GraphBuilder/ReferenceGraphBuilder.h"

void GraphControl::evaluate(int argc, char **argv) {
    argc -= (argc > 0);
    argv += (argc > 0);

    option::Stats stats(usage, argc, argv);
    option::Option options[stats.options_max], buffer[stats.buffer_max];

    option::Parser parse(usage, argc, argv, options, buffer);

    if (parse.error() || options[HELP] || argc == 0) {
        option::printUsage(std::cout, usage);
        return;
    }

    GraphBuilder* gb = nullptr;
    bool needEval = false;

    for (int i = 0; i < parse.optionsCount(); ++i) {
        option::Option& opt = buffer[i];
        string arg;
        switch (opt.index()) {
            case NEW:
                if (needEval) {
                    graph.newLib();
                    gb -> setGraph(&graph);
                    gb -> evaluate();
                }

                delete gb;
                needEval = true;

                arg = opt.arg;
                if (arg == "RNA_PAIR") {
                    gb = new RNAPairReadGraphBuilder();
                    SamFileWriteEdge samFileWriter("reads_rna_pair");
                    gb->setSamFileWriter(samFileWriter);
                } else if (arg == "DNA_PAIR") {
                    gb = new DNAPairReadGraphBuilder();
                    SamFileWriteEdge samFileWriter("reads_dna_pair");
                    gb->setSamFileWriter(samFileWriter);
                } else if (arg == "RNA_SPLIT") {
                    gb = new RNASplitReadGraphBuilder();
                } else if (arg == "REF") {
                    gb = new ReferenceGraphBuilder();
                }

                break;
            case SAM1:
                if ( dynamic_cast <PairReadGraphBuilder *> ( gb )) {
                    (dynamic_cast<PairReadGraphBuilder*> (gb)) -> setFileName1(opt.arg);
                } else {
                    printf("Put the pair read sam file for not pair read builder.\n");
                    return;
                }
                break;
            case SAM2:
                if ( dynamic_cast <PairReadGraphBuilder *> ( gb )) {
                    (dynamic_cast<PairReadGraphBuilder*> (gb)) -> setFileName2(opt.arg);
                } else {
                    printf("Put the pair read sam file for not pair read builder.\n");
                    return;
                }
                break;
            case DIST_BETWEEN_PAIR_READS:
                if ( dynamic_cast <DNAPairReadGraphBuilder *> ( gb )) {
                    (dynamic_cast<DNAPairReadGraphBuilder*> (gb)) -> setFileName2(opt.arg);
                } else {
                    printf("Put the dist between pair read not for DNA pairs.\n");
                    return;
                }
                break;
            case MINCONTIGLEN:
                gb->setMinContigLen(atoi(opt.arg));
                break;
            case MINEDGELEN:
                gb->setMinEdgeWight(atoi(opt.arg));
                break;
            case REFFILE:
                if ( dynamic_cast <RNASplitReadGraphBuilder *> ( gb )) {
                    (dynamic_cast<RNASplitReadGraphBuilder*> (gb)) -> setRefFileName(opt.arg);
                } else if (dynamic_cast<ReferenceGraphBuilder *> ( gb )) {
                    (dynamic_cast<ReferenceGraphBuilder *>(gb)) -> setRefFileName(opt.arg);
                } else {
                    printf("Put the ref file not for (RNA split builder or REF builder).\n");
                    return;
                }
                break;
            case QUERYFILE:
                if (dynamic_cast<ReferenceGraphBuilder *> ( gb )) {
                    (dynamic_cast<ReferenceGraphBuilder *> (gb)) -> setQueryFileName(opt.arg);
                } else {
                    printf("Put query file name not for REF builder\n");
                }
                break;
            case READSFILE:
                if ( dynamic_cast <RNASplitReadGraphBuilder *> ( gb )) {
                    (dynamic_cast<RNASplitReadGraphBuilder*> (gb)) -> setRnaReadFileName(opt.arg);
                } else {
                    printf("Put the reads file not for RNA split builder.\n");
                    return;
                }
                break;
            case LIBNAME:
                gb -> setLibName(opt.arg);
                break;
            case TSVFILE:
                if (dynamic_cast<ReferenceGraphBuilder *> ( gb )) {
                    (dynamic_cast<ReferenceGraphBuilder *> (gb)) -> setTsvFileName(opt.arg);
                } else {
                    printf("Put tsv file name not for REF builder\n");
                }
                break;
            default:break;
        }
    }

    if (needEval) {
        graph.newLib();
        gb -> setGraph(&graph);
        gb -> evaluate();
    }

    delete gb;

    Serialization::write(&graph, "graph.gr");
}