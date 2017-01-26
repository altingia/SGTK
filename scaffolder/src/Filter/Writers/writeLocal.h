#ifndef SCAFFOLDER_WRITELOCAL_H
#define SCAFFOLDER_WRITELOCAL_H

#include "Writer.h"

class writeLocal : public  Writer {
private:
    int v;
    int dist;
    std::string fileName;
public:
    writeLocal(int v, int dist, std::string fileName, Filter *filter1);

    void write() override;
};


#endif //SCAFFOLDER_WRITELOCAL_H
