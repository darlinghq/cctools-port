project(misc)

if(CMAKE_HOST_SYSTEM_PROCESSOR MATCHES "aarch64")
    add_compile_definitions(__arm64__)
endif()

include_directories(AFTER ${CMAKE_CURRENT_SOURCE_DIR}/../include)
include_directories(AFTER ${CMAKE_CURRENT_SOURCE_DIR}/../include/foreign)

add_definitions(-U__APPLE__
	-DEMULATED_HOST_CPU_TYPE=16777223
	-DEMULATED_HOST_CPU_SUBTYPE=3
	-D__STDC_LIMIT_MACROS=1
	-D__STDC_CONSTANT_MACROS=1
	-DHAVE_EXECINFO_H=1
	-D__DARWIN_UNIX03
	-U__APPLE__
	-U_DARWIN_C_SOURCE
	-U_POSIX_C_SOURCE
	-DPROGRAM_PREFIX="x86_64-apple-darwin11-"
	-DSTDC_HEADERS=1 -DHAVE_SYS_TYPES_H=1 -DHAVE_SYS_STAT_H=1 -DHAVE_STDLIB_H=1 -DHAVE_STRING_H=1 -DHAVE_MEMORY_H=1 -DHAVE_STRINGS_H=1 -DHAVE_INTTYPES_H=1 -DHAVE_STDINT_H=1 -DHAVE_UNISTD_H=1 -DHAVE_DLFCN_H=1
	-Du_short=uint16_t -Du_int=uint32_t
	-DPACKAGE_NAME="lipo"
	-DRANLIB
	-DPACKAGE_VERSION="1.0")

add_library(stuff OBJECT
	../libstuff/fatals.c
	../libstuff/bytesex.c
	../libstuff/allocate.c
	../libstuff/errors.c
	../libstuff/arch.c
	../libstuff/arch_usage.c
	../libstuff/port.c
	../libstuff/apple_version.c
	../libstuff/execute.c
	../libstuff/rnd.c
	../libstuff/ofile.c
	../libstuff/ofile_error.c
	../libstuff/unix_standard_mode.c
	../libstuff/version_number.c
	../libstuff/print.c
	../libstuff/swap_headers.c
	../libstuff/get_arch_from_host.c
	../libstuff/set_arch_flag_name.c
	../libstuff/get_toc_byte_sex.c
)

set(lipo_sources
	lipo.c
	$<TARGET_OBJECTS:stuff>
)

add_executable(lipo ${lipo_sources})

set(ranlib_sources
	libtool.c
	$<TARGET_OBJECTS:stuff>
)
add_executable(ranlib ${ranlib_sources})
