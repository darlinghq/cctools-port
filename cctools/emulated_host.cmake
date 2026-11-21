# The architecture the tools default to (the CPU type of the emulated host: what `arch` and lipo
# report, ld64's default -arch, the assembler's instruction set) is Darling's primary slice,
# APPLE_ARCH_PRIMARY. Without it (an older parent project), arm64 is used when it is the only family
# enabled. Sets CCTOOLS_EMULATED_HOST_ARM to TRUE for arm64 and FALSE for the Intel architectures.
if (DEFINED APPLE_ARCH_PRIMARY AND NOT APPLE_ARCH_PRIMARY STREQUAL "")
	if (APPLE_ARCH_PRIMARY STREQUAL "arm64")
		set(CCTOOLS_EMULATED_HOST_ARM TRUE)
	else()
		set(CCTOOLS_EMULATED_HOST_ARM FALSE)
	endif()
elseif (TARGET_ARM64 AND NOT (TARGET_x86_64 OR TARGET_i386))
	set(CCTOOLS_EMULATED_HOST_ARM TRUE)
else()
	set(CCTOOLS_EMULATED_HOST_ARM FALSE)
endif()
