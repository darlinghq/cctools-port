// workaround for some libc's that try to use `__block` as a variable name
#undef __block
#include_next <unistd.h>
#define __block __attribute__((__blocks__(byref)))
