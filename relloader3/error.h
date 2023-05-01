/*
    Error handling functions
*/

#pragma once

#include <common.h>

namespace relloader3 {

/*
    Calls assertionError with automatic filename, line and function
*/
#define ERROR(code) assertionError(__FILE__, __LINE__, __FUNCTION__, code)

/*
    Calls assertionError if an error code is negative
*/
#define CHECK_ERROR(code) if (code < 0) ERROR(code)

/*
    Calls assertionError if a condition isn't met
*/
#define CHECK_TRUE(condition) if (!condition) ERROR(0)

/*
    Calls assertionError if a pointer is null
*/
#define CHECK_PTR(ptr, size) if (ptr == nullptr) ERROR(size)

/*
    Displays an error message on screen for a failed assertion
*/
void NORETURN assertionError(const char * file, s32 line, const char * function, s32 code);

/*
    Displays an error message on screen
*/
void NORETURN error(const char * message);

}
