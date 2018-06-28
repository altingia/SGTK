#include <iostream>
#include "DotWriter.h"
#include <cmath>

namespace filter {
    namespace writers {
        void DotWriter::writeVertexSet(std::vector<int> vert, std::string fileName) {
            DEBUG("writeVertexSet");
            std::vector<std::vector<int> > res = graphSplitter.split(graph, vert);
            for (int i = 0; i < (int) res.size(); ++i) {
                std::stringstream ss;
                ss << fileName << i;
                std::string name = std::string(ss.str());
                if (validator->isGoodVertexSet(res[i], graph)) {
                    TRACE("isOk vertex set" << i)
                    writeOneVertexSet(res[i], name);
                }
            }
        }

        void DotWriter::writeOneVertex(int v, int isColored, std::ofstream &out) {
            TRACE("write one vertex v=" << v << " isColored=" << isColored);

            out << "    \"" << graph->getTargetName(v) << "\"[label=\" " << graph->getTargetName(v) <<
                " id = " << v
                << "\nlen = " << graph->getTargetLen(v);

            if (coordFile != "") {
                out << "\n coord: \n";

                std::vector<alig_info::InfoAboutContigsAlig::Alignment> aligs = aligInfo.getAlignment(v);
                if (aligs.size() > 10) {
                    out << "too much alig\n";
                } else {
                    for (auto alig : aligs) {
                        out << alig.chrName << " " << alig.coordBegin << " " << alig.coordEnd
                            << " (" <<  100.0*(alig.coordEnd - alig.coordBegin)/graph->getTargetLen(v) << ")\n";
                    }
                }
            }

            std::vector<ContigGraph::Exon> exons = graph->getExons(v, 1);
            if (exons.size() > 0) {
                out << "\n exons: \n";
                if (exons.size() > 30) {
                    out << "too much\n";
                } else {
                    int cur = 0;
                    for (int i = 0; i < exons.size(); ++i) {
                        if (exons[i].id != cur) {
                            out << "\n";
                            cur = exons[i].id;
                        }
                        out << exons[i].b << " " << exons[i].e << " " << exons[i].cov << "; ";
                    }
                    out << "\n";
                }
            }

            out << "\"";
            if (isColored == 1) {
                out << " , style = \"filled\", color = \"#F0E68C\"";
            } else if (isColored == 2) {
                out << " , style = \"filled\", color = \"#c71585\"";
            }
            out << "];\n";
            TRACE("finish write one vert");
        }

        void DotWriter::writeOneEdge(int e, std::ofstream &out) {
            TRACE("write one edge e=" << e);

            int v = graph->getEdgeFrom(e);
            int u = graph->getEdgeTo(e);
            out << "    \"" << graph->getTargetName(v) << "\" -> \"";
            out << graph->getTargetName(u) << "\" [ ";
            out << "color = \"" << graph->getLibColor(graph->getEdgeLib(e)) << "\", ";
            out << "penwidth = " << 1 + (int) log10(graph->getEdgeWeight(e)) << ", ";
            out << "label = " << "\"" << graph->getLibName(graph->getEdgeLib(e));
            out << "\n weight = " << (graph->getEdgeWeight(e));
            out << "\n id = " << e;
            out << "\n " << graph->getInfo(e) << "\" ]\n";
        }

        void DotWriter::writeOneVertexSet(std::vector<int> vert, std::string fileName) {
            TRACE("write vertex set");
            std::vector<bool> hasOtherEdge(vert.size(), 0);
            std::vector<std::pair<int, int>> weightEdge;
            findVertWithOtherEdges(vert, hasOtherEdge, weightEdge);
            if (vert.size() == 1) return;

            std::ofstream out(fileName);
            out << "digraph {\n";
            for (int i = 0; i < (int) vert.size(); ++i) {
                writeOneVertex(vert[i], hasOtherEdge[i], out);
            }
            std::sort(weightEdge.rbegin(), weightEdge.rend());
            for (int i = 0; i < (int) weightEdge.size(); ++i) {
                writeOneEdge(weightEdge[i].second, out);
            }

            out << "labelloc=\"t\"" << "\n";
            out << "label=\"file name=" << fileName << "\";\n";

            out << "}\n";
            out.close();
        }

        void DotWriter::findVertWithOtherEdges(const std::vector<int> &vert, std::vector<bool> &hasOtherEdge,
                                               std::vector<std::pair<int, int>> &weightEdge) const {
            TRACE("find vertex with outsize edges");
            for (int i = 0; i < (int) vert.size(); ++i) {
                int v = vert[i];
                std::vector<std::pair<int, int> > curEdge;
                for (int e : graph->getEdges(v)) {
                    int u = graph->getEdgeTo(e);
                    int was = 0;
                    for (int h = 0; h < (int) vert.size(); ++h) {
                        if (vert[h] == u) was = 1;
                    }
                    if (was) {
                        curEdge.push_back(std::make_pair(graph->getEdgeWeight(e), e));
                    } else {
                        hasOtherEdge[i] = 1;
                    }
                }

                for (int e : graph->getEdgesR(v)) {
                    int u = graph->getEdgeFrom(e);
                    int was = 0;
                    for (int h = 0; h < (int) vert.size(); ++h) {
                        if (vert[h] == u) was = 1;
                    }
                    if (!was) {
                        hasOtherEdge[i] = 1;
                    }
                }

                if (curEdge.size() > 20) {
                    hasOtherEdge[i] = 2;
                } else {
                    for (auto cur : curEdge) {
                        weightEdge.push_back(cur);
                    }
                }
            }
        }
    }
}