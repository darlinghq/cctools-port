project(ld64)

if(CMAKE_HOST_SYSTEM_PROCESSOR MATCHES "aarch64")
    add_compile_definitions(__arm64__)
endif()

add_definitions(-DHAVE_BCMP=1 -DHAVE_BZERO=1 -DHAVE_BCOPY=1 -DHAVE_INDEX=1 -DHAVE_RINDEX=1)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fblocks -Wno-everything")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fblocks -std=c++20 -Wno-long-long -Wno-import -Wno-format -Wno-deprecated -Wno-unused-variable -Wno-unused-private-field -Wno-unused-function -Wno-invalid-offsetof -Wno-int-conversion -Wno-char-subscripts -Wno-shift-negative-value")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../../include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../../include/foreign)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/ld)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/ld/parsers)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/3rd)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/3rd/BlocksRuntime)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/3rd/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/abstraction)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/mach_o)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

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
	3rd/eprintf.c
	3rd/helper.c
	3rd/md5.c
	3rd/mkpath_np.c
	3rd/qsort_r.c
	3rd/reallocf.c
	3rd/sha1.c
	3rd/sha256.c
	3rd/strlcat.c
	3rd/strlcpy.c

	ld/FatFile.cpp
	ld/InputFiles.cpp
	ld/Mangling.cpp
	ld/Options.cpp
	ld/OutputFile.cpp
	ld/PlatformSupport.cpp
	ld/Resolver.cpp
	ld/ResponseFiles.cpp
	ld/Snapshot.cpp
	ld/SymbolTable.cpp
	ld/code-sign-blobs/blob.cpp
	ld/debugline.c
	ld/ld.cpp
	ld/libcodedirectory.c
	ld/parsers/archive_file.cpp
	ld/parsers/generic_dylib_file.cpp
	ld/parsers/lto_file.cpp
	ld/parsers/macho_dylib_file.cpp
	ld/parsers/macho_relocatable_file.cpp
	ld/parsers/opaque_section_file.cpp
	ld/parsers/textstub_dylib_file.cpp
	ld/passes/bitcode_bundle.cpp
	ld/passes/branch_island.cpp
	ld/passes/branch_shim.cpp
	ld/passes/code_dedup.cpp
	ld/passes/compact_unwind.cpp
	ld/passes/dtrace_dof.cpp
	ld/passes/dylibs.cpp
	ld/passes/got.cpp
	ld/passes/huge.cpp
	ld/passes/inits.cpp
	ld/passes/objc.cpp
	ld/passes/objc_constants.cpp
	ld/passes/objc_stubs.cpp
	ld/passes/order.cpp
	ld/passes/stubs/stubs.cpp
	ld/passes/thread_starts.cpp
	ld/passes/tlvp.cpp

	mach_o/Error.cpp
	mach_o/ExportsTrie.cpp
	
	# other/ObjectDump.cpp
	# other/PruneTrie.cpp
	# other/machochecker.cpp
	# other/objcimageinfo.cpp
	# other/unwinddump.cpp
)

add_executable(${APPLE_TARGET_TRIPLET_PRIMARY}-ld ${ld64_sources})
target_link_libraries(${APPLE_TARGET_TRIPLET_PRIMARY}-ld -lpthread -ldl -ldispatch -lBlocksRuntime)

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
