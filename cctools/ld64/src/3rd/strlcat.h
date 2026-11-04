#ifndef __APPLE__

#ifndef STRLCAT_H
#define STRLCAT_H

#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif
#include <stddef.h>

/* glibc >= 2.38 declares it (with __THROW); redeclaring it differs and fails in C++ */
/* Compare __GLIBC__/__GLIBC_MINOR__ instead of calling __GLIBC_PREREQ: the
   preprocessor parses an undefined function-like macro even behind a
   short-circuited &&, which is a hard error on non-glibc hosts. */
#if !(defined(__GLIBC__) && (__GLIBC__ > 2 || (__GLIBC__ == 2 && __GLIBC_MINOR__ >= 38)) && defined(__USE_MISC))
size_t strlcat(char *dst, const char *src, size_t siz);
#endif

#ifdef __cplusplus
}
#endif

#endif

#endif /* ! __APPLE__ */