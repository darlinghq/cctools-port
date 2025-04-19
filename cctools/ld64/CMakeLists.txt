project(ld64)

if(CMAKE_HOST_SYSTEM_PROCESSOR MATCHES "aarch64")
    add_compile_definitions(__arm64__)
endif()

add_definitions(-DHAVE_BCMP=1 -DHAVE_BZERO=1 -DHAVE_BCOPY=1 -DHAVE_INDEX=1 -DHAVE_RINDEX=1)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wno-everything -fblocks")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fblocks -std=c++20 -Wno-long-long -Wno-import -Wno-format -Wno-deprecated -Wno-unused-variable -Wno-unused-private-field -Wno-unused-function -Wno-invalid-offsetof -Wno-int-conversion -Wno-char-subscripts -Wno-shift-negative-value")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../include/foreign)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/3rd)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/3rd/BlocksRuntime)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/3rd/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/abstraction)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/ld)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/ld/parsers)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/mach_o)

add_definitions(-U__APPLE__
	-D__STDC_LIMIT_MACROS=1
	-D__STDC_CONSTANT_MACROS=1
	-DHAVE_EXECINFO_H=1
	-D__DARWIN_UNIX03
	-DPROGRAM_PREFIX="${APPLE_TARGET_TRIPLET_PRIMARY}-"
	-DSTDC_HEADERS=1 -DHAVE_SYS_TYPES_H=1 -DHAVE_SYS_STAT_H=1 -DHAVE_STDLIB_H=1 -DHAVE_STRING_H=1 -DHAVE_MEMORY_H=1 -DHAVE_STRINGS_H=1 -DHAVE_INTTYPES_H=1 -DHAVE_STDINT_H=1 -DHAVE_UNISTD_H=1 -DHAVE_DLFCN_H=1
	-Du_short=uint16_t)

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


set(ld64_sources
	# cctools/ld64/src/3rd/Makefile.am
	src/3rd/helper.c
	src/3rd/qsort_r.c
	src/3rd/strlcat.c
	src/3rd/strlcpy.c
	src/3rd/eprintf.c
	src/3rd/md5.c
	src/3rd/sha1.c
	src/3rd/sha256.c
	src/3rd/mkpath_np.c
	src/3rd/reallocf.c

	# cctools/ld64/src/mach_o/Makefile.am
	src/mach_o/Error.cpp
	src/mach_o/ExportsTrie.cpp

	# cctools/ld64/src/ld/Makefile.am
	src/ld/debugline.c
	src/ld/libcodedirectory.c
	src/ld/InputFiles.cpp
	src/ld/ld.cpp
	src/ld/Options.cpp
	src/ld/OutputFile.cpp
	src/ld/Resolver.cpp
	src/ld/Snapshot.cpp
	src/ld/SymbolTable.cpp
	src/ld/PlatformSupport.cpp
	src/ld/ResponseFiles.cpp
	src/ld/FatFile.cpp
	src/ld/Mangling.cpp
	src/ld/code-sign-blobs/blob.cpp

	# cctools/ld64/src/ld/parsers/Makefile.am
	src/ld/parsers/archive_file.cpp
	src/ld/parsers/lto_file.cpp
	src/ld/parsers/macho_dylib_file.cpp
	src/ld/parsers/macho_relocatable_file.cpp
	src/ld/parsers/opaque_section_file.cpp
	src/ld/parsers/textstub_dylib_file.cpp
	src/ld/parsers/generic_dylib_file.cpp

	# cctools/ld64/src/ld/passes/Makefile.am
	src/ld/passes/branch_island.cpp
	src/ld/passes/branch_shim.cpp
	src/ld/passes/compact_unwind.cpp
	src/ld/passes/dtrace_dof.cpp
	src/ld/passes/dylibs.cpp
	src/ld/passes/got.cpp
	src/ld/passes/huge.cpp
	src/ld/passes/objc.cpp
	src/ld/passes/order.cpp
	src/ld/passes/tlvp.cpp
	src/ld/passes/stubs/stubs.cpp
	src/ld/passes/bitcode_bundle.cpp
	src/ld/passes/code_dedup.cpp
	src/ld/passes/thread_starts.cpp
	src/ld/passes/inits.cpp
	src/ld/passes/objc_constants.cpp
	src/ld/passes/objc_stubs.cpp
)

add_executable(${APPLE_TARGET_TRIPLET_PRIMARY}-ld ${ld64_sources})
target_link_libraries(${APPLE_TARGET_TRIPLET_PRIMARY}-ld -lpthread -ldl -lBlocksRuntime -ldispatch)


# musl libc systems need libexecinfo
find_library(EXECINFO
	NAMES
		execinfo
	PATHS
		/usr/lib
		/usr/local/lib
		/opt/local/lib
		/sw/lib
)

if(EXECINFO)
	target_link_libraries(${APPLE_TARGET_TRIPLET_PRIMARY}-ld "${EXECINFO}")
endif()
