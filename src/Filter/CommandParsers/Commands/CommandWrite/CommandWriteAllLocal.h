#ifndef SCAFFOLDER_COMMANDWRITEALLLOCAL_H
#define SCAFFOLDER_COMMANDWRITEALLLOCAL_H

#include "CommandWrite.h"
#include <Filter/Writers/WriteLocal.h>

namespace filter {
    namespace commands {
        class CommandWriteAllLocal : public CommandWrite {
        public:
            void writeGraph(std::string argv, State &state, ContigGraph &graph) override;
        };
    }
}

#endif //SCAFFOLDER_COMMANDWRITEALLLOCAL_H