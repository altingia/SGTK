#include "RuleBigDeg.h"

namespace filter {
    namespace scaffolder {
        void RuleBigDeg::simplifyGraph(filter::Filter *filter) {
            std::vector<int> vert = filter->getVertexList();
            std::vector<int> wignore(filter->getVertexCount(), 0);
            std::vector<int> wignoreR(filter->getVertexCount(), 0);

            for (int v : vert) {
                std::vector<int> edges = filter->getEdges(v);
                if (edges.size() >= BIG_DEG) {
                    wignore[v] = filter->getEdgeWeight(edges[0]);
                    for (int e : edges) {
                        wignore[v] = std::min(wignore[v], filter->getEdgeWeight(e));
                    }
                }

                std::vector<int> edgesR = filter->getEdgesR(v);
                if (edgesR.size() >= BIG_DEG) {
                    wignoreR[v] = filter->getEdgeWeight(edgesR[0]);
                    for (int e : edgesR) {
                        wignoreR[v] = std::min(wignoreR[v], filter->getEdgeWeight(e));
                    }
                }
            }

            ignoreEdges(filter, wignore);
            ignoreEdgesR(filter, wignoreR);

        }

        void RuleBigDeg::ignoreEdges(Filter *filter, std::vector<int> wig) {
            std::vector<int> vect = filter->getVertexList();
            for (int v : vect) {
                if (wig[v] != 0) {
                    std::vector<int> edges = filter->getEdges(v);
                    for (int e : edges) {
                        if (filter->getEdgeWeight(e) * MAX_DIF <= wig[v]) {
                            std::stringstream ss;
                            ss << e;
                            filter->processQuery(Query(Query::SET_IGNORE_EDGE, ss.str()));
                        }
                    }
                }
            }
        }

        void RuleBigDeg::ignoreEdgesR(Filter *filter, std::vector<int> wig) {
            std::vector<int> vect = filter->getVertexList();
            for (int v : vect) {
                if (wig[v] != 0) {
                    std::vector<int> edges = filter->getEdgesR(v);
                    for (int e : edges) {
                        if (filter->getEdgeWeight(e) * MAX_DIF <= wig[v]) {
                            std::stringstream ss;
                            ss << e;
                            filter->processQuery(Query(Query::SET_IGNORE_EDGE, ss.str()));
                        }
                    }
                }
            }
        }
    }
}
