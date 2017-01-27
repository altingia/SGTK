#include <Filter/CommandParsers/State.h>
#include "CommandUploadGraph.h"

void CommandUploadGraph::execute(std::string argv, State& state, Filter *filter) {
    std::stringstream ss(argv);
    std::string fileName;
    ss >> fileName;
    filter->processQuery(Query(Query::UPLOAD_GRAPH, fileName));
}