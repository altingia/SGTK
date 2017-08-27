#include <algorithm>
#include <iostream>
#include <set>
#include <Filter/CommandParsers/Commands/Command.h>
#include "ScaffolderPipeline.h"
#include "ScaffoldStrategy.h"
#include "ScaffoldStrategyUniqueConnection.h"
#include "RuleBigDifInWeight.h"
#include "RuleDelCycle.h"
#include "RuleInOneLine.h"
#include "RuleBigDeg.h"
#include "RuleDelSmallCycle.h"
#include "RuleDelSmallEdges.h"
#include "RuleCoord.h"
#include "RuleDel30.h"
#include "RuleValidateCoord.h"
#include "RuleCovering.h"

namespace filter {
    namespace scaffolder {
        using namespace commands;
        void ScaffolderPipeline::evaluate(ContigGraph *graph, std::string contigFile,
                                          std::string out, std::vector<State::BamFiles> bamFiles) {
            INFO("start build scaffolds");
            /*std::vector<int> libs = graph->getLibList();
            for (int i = (int)libs.size() - 1; i > 0; --i)
                double w1 = 1, w2 = 1;
                if (i == libs.size() - 1 && graph->getLibType(libs[i]) == contig_graph::ContigGraph::Lib::RNA_SPLIT_50) {
                    w1 = 1.75;
                }
                if (graph->getLibType(libs[i - 1]) == contig_graph::ContigGraph::Lib::RNA_SPLIT_50) {
                    w2 = 1.75;
                }
                graph->mergeLib(libs[i], libs[i - 1], "lib", w1, w2);
            }*/

            Scaffolds scaffolds(contigFile);

            RuleDelSmallEdges rdse;
            rdse.simplifyGraph(graph);
            graph->write("smp.gr");
            RuleDelSmallCycle rdsc;
            rdsc.simplifyGraph(graph);
            RuleInOneLine riol;
            riol.simplifyGraph(graph);
            RuleBigDifInWeight rbddiw;
            rbddiw.simplifyGraph(graph);
            riol.simplifyGraph(graph);
            RuleCoord rc;
            rc.simplifyGraph(graph);
            //RuleValidateCoord rvc;
            //rvc.simplifyGraph(graph);
            RuleDel30 rd30;
            rd30.simplifyGraph(graph);

            RuleCovering rcov;
            rcov.setBamFiles(bamFiles);
            rcov.setAligFile(alig);
            rcov.simplifyGraph(graph);

            ScaffoldStrategyUniqueConnection ssuc;
            ssuc.addConnection(&scaffolds, graph);
            scaffolds.print(out);
        }
    }
}
