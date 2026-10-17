#ifndef __APPLE__

#ifndef STRLCPY_H
#define STRLCPY_H

#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif
#include <stddef.h>

/* glibc >= 2.38 declares it (with __THROW); redeclaring it differs and fails in C++ */
#if !(defined(__GLIBC__) && defined(__GLIBC_PREREQ) && __GLIBC_PREREQ(2, 38) && defined(__USE_MISC))
size_t strlcpy(char *dst, const char *src, size_t siz);
#endif

#ifdef __cplusplus
}
#endif

#endif

#endif /* ! __APPLE__ */