/*
    Error handling functions
*/

#pragma once

#include <common.h>

namespace memtest {

/*
    Logs the id of the RelLoader used
*/
void logLoaderUsed(s32 loader);

/*
    Calls assertionError with automatic filename and line
*/
#define ASSERT_ERROR(code) assertionError(__FILE__, __LINE__, code)

/*
    Calls assertionError if an error code is negative
*/
#define CHECK_ERROR(code) if (code < 0) ASSERT_ERROR(code)

/*
    Calls assertionError if a condition isn't met
*/
#define CHECK_TRUE(condition) if (!condition) ASSERT_ERROR(0)

/*
    Calls assertionError if a pointer is null
*/
#define CHECK_PTR(ptr) if (ptr == nullptr) ASSERT_ERROR(0)

/*
    Calls assertionError if an allocation is null
*/
#define CHECK_ALLOC(ptr, size) if (ptr == nullptr) ASSERT_ERROR(size)

/*
    Displays an error message on screen for a failed assertion
*/
void NORETURN assertionError(const char * file, s32 line, s32 code);

/*
    Displays an error message on screen
*/
void NORETURN error(const char * message);

}
