project(ld64)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fblocks -std=c++11 -Wno-long-long -Wno-import -Wno-format -Wno-deprecated -Wno-unused-variable -Wno-unused-private-field -Wno-unused-function -Wno-invalid-offsetof -Wno-int-conversion -Wno-char-subscripts -Wno-shift-negative-value")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../../include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../../include/foreign)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/ld)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/ld/parsers)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/3rd)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/3rd/BlocksRuntime)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/3rd/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/abstraction)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

add_definitions(-U__APPLE__
	-DEMULATED_HOST_CPU_TYPE=16777223
	-DEMULATED_HOST_CPU_SUBTYPE=3
	-D__STDC_LIMIT_MACROS=1
	-D__STDC_CONSTANT_MACROS=1
	-DHAVE_EXECINFO_H=1
	-D__DARWIN_UNIX03
	-DPROGRAM_PREFIX="x86_64-apple-darwin11-"
	-DSTDC_HEADERS=1 -DHAVE_SYS_TYPES_H=1 -DHAVE_SYS_STAT_H=1 -DHAVE_STDLIB_H=1 -DHAVE_STRING_H=1 -DHAVE_MEMORY_H=1 -DHAVE_STRINGS_H=1 -DHAVE_INTTYPES_H=1 -DHAVE_STDINT_H=1 -DHAVE_UNISTD_H=1 -DHAVE_DLFCN_H=1
	-Du_short=uint16_t)

set(ld64_sources
	./ld/InputFiles.cpp
	./ld/OutputFile.cpp
	./ld/SymbolTable.cpp
	./ld/code-sign-blobs/blob.cpp
	./ld/parsers/lto_file.cpp
	./ld/parsers/opaque_section_file.cpp
	./ld/parsers/macho_relocatable_file.cpp
	./ld/parsers/macho_dylib_file.cpp
	./ld/parsers/textstub_dylib_file.cpp
	./ld/parsers/archive_file.cpp
	./ld/Options.cpp
	./ld/Resolver.cpp
	./ld/ld.cpp
	./ld/Snapshot.cpp
	./ld/passes/branch_island.cpp
	./ld/passes/compact_unwind.cpp
	./ld/passes/code_dedup.cpp
	./ld/passes/got.cpp
	./ld/passes/tlvp.cpp
	./ld/passes/branch_shim.cpp
	./ld/passes/dtrace_dof.cpp
	./ld/passes/order.cpp
	./ld/passes/dylibs.cpp
	./ld/passes/stubs/stubs.cpp
	./ld/passes/huge.cpp
	./ld/passes/bitcode_bundle.cpp
	./ld/passes/objc.cpp
	./3rd/md5.c
	./3rd/strlcat.c
	./3rd/BlocksRuntime/runtime.c
	./3rd/BlocksRuntime/data.c
	./3rd/helper.c
	./3rd/strlcpy.c
	./3rd/qsort_r.c
	./3rd/eprintf.c
	./ld/debugline.c
)

add_executable(x86_64-apple-darwin11-ld ${ld64_sources})
target_link_libraries(x86_64-apple-darwin11-ld -lpthread -ldl)

