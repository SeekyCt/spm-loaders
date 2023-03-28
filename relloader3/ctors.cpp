#include <common.h>

#include "ctors.h"

namespace relloader3 {

typedef void (ctor)();

extern "C" {

extern ctor * ctors_start[];
extern ctor * ctors_end[];

}

void callCtors()
{
    for (ctor ** p = ctors_start; p < ctors_end; p++)
        (*p)();
}

}