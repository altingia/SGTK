#include "Manager.h"

const std::string Manager::UPLOAD_GRAPH = "uploadGraph";
const std::string Manager::MIN_EDGE_WEIGHT = "minEdgeW";
const std::string Manager::MIN_CONTIG_LEN = "minContig";
const std::string Manager::WRITE_FULL = "writeFull";
const std::string Manager::WRITE_LOCAL = "writeLocal";
const std::string Manager::WRITE_ALL_LOCAL = "writeAllLocal";
const std::string Manager::WRITE_LOCAL_VERT_IN_SEG = "writeLocalSeg";
const std::string Manager::WRITE_BIG_COMP = "writeBig";
const std::string Manager::WRITE_SPLIT_BIG_COMP = "writeSB";
const std::string Manager::MERGE_SIMPLE_PATH = "mergeSimplePath";
const std::string Manager::WRITE_LOCAL_ALONG_PATH = "writeAlongPath";
const std::string Manager::SET_IGNORE = "setIgnore";
const std::string Manager::RESET_IGNORE = "resetIgnore";
const std::string Manager::EXIT = "exit";

const std::string Manager::CONFIG_FILE = "filter_config";

Manager::Manager() {
    filter = new FilterIgnore(new FilterMinWeight(new FilterAdapter(ContigGraph())));

    commandByKeyWord[UPLOAD_GRAPH] = new CommandUploadGraph();
}

void Manager::main() {
    readConfig();
    std::cout << "Finish read config file" << std::endl;

    while(handlingRequest(std::cin)) {
        std::cout << "Finish handling request" << std::endl;
    }

}

void Manager::readConfig() {
    std::ifstream in(CONFIG_FILE);

    while (handlingRequest(in));
}

bool Manager::handlingRequest(std::istream &in) {
    std::string keyWord;
    std::string argv;

    in >> keyWord;
    if (commandByKeyWord.count(keyWord) > 0) {
        getline(in, argv);

        commandByKeyWord[keyWord]->execute(argv, state, filter);
    }

    return false;
}

