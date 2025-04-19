project(as)

if(CMAKE_HOST_SYSTEM_PROCESSOR MATCHES "aarch64")
	add_compile_definitions(__arm64__)
endif()

# i386 has a different CPU type/subtype, but Darling only supports x86_64
if(TARGET_x86_64 OR TARGET_i386)
	add_compile_definitions(
		EMULATED_HOST_CPU_TYPE=16777223
		EMULATED_HOST_CPU_SUBTYPE=3
	)
elseif(TARGET_ARM64)
	add_compile_definitions(
		EMULATED_HOST_CPU_TYPE=16777228
		EMULATED_HOST_CPU_SUBTYPE=0
	)
endif()

add_compile_definitions(
	NeXT_MOD
	__DARWIN_UNIX03
	__LITTLE_ENDIAN__
	PROGRAM_PREFIX="${APPLE_TARGET_TRIPLET_PRIMARY}-"
	PACKAGE_NAME="cctools-darling"
	PACKAGE_VERSION="949.0.1"
	__STDC_LIMIT_MACROS=1
	__STDC_CONSTANT_MACROS=1
	STDC_HEADERS=1
	HAVE_SYS_TYPES_H=1
	HAVE_SYS_STAT_H=1
	HAVE_STDLIB_H=1
	HAVE_STRING_H=1
	HAVE_MEMORY_H=1
	HAVE_STRINGS_H=1
	HAVE_INTTYPES_H=1
	HAVE_STDINT_H=1
	HAVE_UNISTD_H=1
	HAVE_DLFCN_H=1

	HAVE_BCMP=1
	HAVE_BZERO=1
	HAVE_BCOPY=1
	HAVE_INDEX=1
	HAVE_RINDEX=1

	u_short=uint16_t
	u_int=uint32_t
)

add_definitions(
	-U__APPLE__
	-U_DARWIN_C_SOURCE
	-U_POSIX_C_SOURCE
)

if(TARGET_x86_64 OR TARGET_i386)
	add_compile_definitions(
		I386
		i486
		i586
		i686
		ARCH64
	)
elseif(TARGET_ARM64)
	add_compile_definitions(ARM)
endif()

include_directories(AFTER
	${CMAKE_CURRENT_SOURCE_DIR}/../include
	${CMAKE_CURRENT_SOURCE_DIR}/../include/foreign
	${CMAKE_CURRENT_SOURCE_DIR}/../libstuff
	${CMAKE_CURRENT_SOURCE_DIR}
)


set(AS_SOURCES
	as.c
)

add_executable(${APPLE_TARGET_TRIPLET_PRIMARY}-as ${AS_SOURCES})
