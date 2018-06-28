#ifndef SCAFFOLDER_VALIDATORFORK_H
#define SCAFFOLDER_VALIDATORFORK_H

#include <ContigGraph/ContigGraph.h>
#include "FileValidator.h"

namespace filter {
    namespace writers {
        using namespace contig_graph;
        class ValidatorFork : public FileValidator {
        private:
            int lib;
        public:
            ValidatorFork(int lib) : lib(lib) {}

            bool isGoodVertexSet(std::vector<int> vert, ContigGraph *graph);
        };
    }
}

#endif //SCAFFOLDER_VALIDATORFORK_H