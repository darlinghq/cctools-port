project(misc)

if(CMAKE_HOST_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
    add_compile_definitions(__arm64__)
endif()

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wno-everything")

include_directories(AFTER ${CMAKE_CURRENT_SOURCE_DIR}/../include)
include_directories(AFTER ${CMAKE_CURRENT_SOURCE_DIR}/../include/foreign)

add_definitions(-DHAVE_BCMP=1  -DHAVE_BCOPY=1  )

add_definitions(-U__APPLE__
	-D__STDC_LIMIT_MACROS=1
	-D__STDC_CONSTANT_MACROS=1
	-DHAVE_EXECINFO_H=1
	-D__DARWIN_UNIX03
	-U__APPLE__
	-U_DARWIN_C_SOURCE
	-U_POSIX_C_SOURCE
	-DPROGRAM_PREFIX="${APPLE_TARGET_TRIPLET_PRIMARY}-"
	-DSTDC_HEADERS=1 -DHAVE_SYS_TYPES_H=1 -DHAVE_SYS_STAT_H=1 -DHAVE_STDLIB_H=1 -DHAVE_STRING_H=1 -DHAVE_MEMORY_H=1 -DHAVE_STRINGS_H=1 -DHAVE_INTTYPES_H=1 -DHAVE_STDINT_H=1 -DHAVE_UNISTD_H=1 -DHAVE_DLFCN_H=1
	-Du_short=uint16_t -Du_int=uint32_t
	-DPACKAGE_NAME="lipo"
	-DRANLIB
	-DPACKAGE_VERSION="1.0")

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
	../libstuff/args.c
	../libstuff/write64.c
)

set(lipo_sources
	lipo.c
	$<TARGET_OBJECTS:stuff>
)

add_executable(lipo ${lipo_sources})
target_link_libraries(lipo m)

# Host tool that edits load commands (dylib install names and dependencies) of Mach-O files; Darling's build
# uses it to give prebuilt dylibs absolute dependency paths. The build's own copy of the cctools install_name_tool
# for the guest is a different target.
add_library(stuff_edit OBJECT
	../libstuff/breakout.c
	../libstuff/writeout.c
	../libstuff/checkout.c
	../libstuff/hash_string.c
	../libstuff/reloc.c
	../libstuff/crc32.c
	../libstuff/lto.c
	../libstuff/best_arch.c
	../libstuff/guess_short_name.c
	../libstuff/symbol_list.c
	../libstuff/fatal_arch.c
	../libstuff/ofile_get_word.c
)

add_executable(install_name_tool_host
	install_name_tool.c
	$<TARGET_OBJECTS:stuff>
	$<TARGET_OBJECTS:stuff_edit>
)
set_target_properties(install_name_tool_host PROPERTIES OUTPUT_NAME "${APPLE_TARGET_TRIPLET_PRIMARY}-install_name_tool")
target_link_libraries(install_name_tool_host m)
