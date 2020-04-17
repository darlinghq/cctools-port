project(ar)

if(CMAKE_HOST_SYSTEM_PROCESSOR MATCHES "aarch64")
    add_compile_definitions(__arm64__)
endif()

include_directories(AFTER ${CMAKE_CURRENT_SOURCE_DIR}/../include)
include_directories(AFTER ${CMAKE_CURRENT_SOURCE_DIR}/../include/foreign)

add_definitions(-U__APPLE__
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
	-D__USE_MISC)
add_definitions(-DHAVE_BCMP=1 -DHAVE_BZERO=1 -DHAVE_BCOPY=1 -DHAVE_INDEX=1 -DHAVE_RINDEX=1)

# i386 has a different CPU type/subtype, but Darling only supports x86_64
if (TARGET_x86_64 OR TARGET_i386)
	add_definitions(
		-DEMULATED_HOST_CPU_TYPE=16777223
		-DEMULATED_HOST_CPU_SUBTYPE=3
	)
elseif (TARGET_ARM64)
	add_definitions(
		-DEMULATED_HOST_CPU_TYPE=16777228
		-DEMULATED_HOST_CPU_SUBTYPE=0
	)
endif(TARGET_x86_64 OR TARGET_i386)

set(ar_sources
	append.c
	ar.c
	archive.c
	contents.c
	delete.c
	extract.c
	misc.c
	move.c
	print.c
	replace.c
	../libstuff/unix_standard_mode.c
	../libstuff/execute.c
	../libstuff/port.c
	../libstuff/fatals.c
	../libstuff/allocate.c
)

add_executable(x86_64-apple-darwin11-ar ${ar_sources})

set(ranlib_sources
	../misc/libtool.c
	$<TARGET_OBJECTS:stuff>
)
add_executable(ranlib ${ranlib_sources})
set_property(TARGET ranlib APPEND_STRING PROPERTY COMPILE_FLAGS " -DRANLIB")
set_target_properties(ranlib PROPERTIES OUTPUT_NAME "x86_64-apple-darwin11-ranlib")

