/*
    Error handling functions
*/

#pragma once

#include <common.h>

namespace relloader3 {

/*
    Calls assertionError with automatic filename, line and function
*/
#define ERROR(code, context) assertionError(__FILE__, __LINE__, __FUNCTION__, code, context)

/*
    Calls assertionError if an error code is negative
*/
#define CHECK_ERROR(code, ctx) if (code < 0) ERROR(code, ctx)

/*
    Calls assertionError if a condition isn't met
*/
#define CHECK_TRUE(condition, context) if (!condition) ERROR(0, context)

/*
    Calls assertionError if a pointer is null
*/
#define CHECK_PTR(ptr, size, context) if (ptr == nullptr) ERROR(size, context)

/*
    Displays an error message on screen for a failed assertion
*/
void NORETURN assertionError(const char * file, s32 line, const char * function, s32 code,
                             const char * context);

/*
    Displays an error message on screen
*/
void NORETURN error(const char * message);

}
