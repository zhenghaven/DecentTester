cmake_minimum_required(VERSION 3.11)

#==========================================================
#   Options for Decent DHT Project
#==========================================================

option(DHT_YCSB_TEST "Test set option: Decent DHT test with YCSB" ON)
set(YCSB_ROOT_DIR ${CMAKE_CURRENT_LIST_DIR}/benchmarks/YCSB)
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

set(HUNTER_BOOST_RUNTIME_STATIC ON CACHE BOOL "Switch for using boost runtime static linking." FORCE)

if(APPLE)
	message(WARNING "Mac OS is not supported by Intel SGX for now. Trying to build in simulation mode...")
	set(CMAKE_BUILD_TYPE DebugSimulation)
endif()

# Automated part:
if(${DHT_YCSB_TEST})
	set(DHT_TEST_ENCLAVE ON)
	if(${DHT_YCSB_TEST} AND NOT EXISTS ${YCSB_ROOT_DIR}/pom.xml)
		message(FATAL_ERROR "YCSB test is on, but the root directory of YCSB couldn't be found!")
	endif()
endif()
#==========================================================
#   Setup Hunter
#==========================================================

set(gate_dir "${CMAKE_CURRENT_LIST_DIR}/hunter/gate")
set(gate_module "${gate_dir}/cmake/HunterGate.cmake")
set(HUNTER_KEEP_PACKAGE_SOURCES ON)

get_filename_component(gate_module "${gate_module}" ABSOLUTE)

if(NOT EXISTS "${gate_module}")
	message(FATAL_ERROR "${gate_module} module not found!")
endif()

message(STATUS "Including HunterGate: ${gate_module}")
include("${gate_module}")

get_filename_component(HUNTER_ROOT "${CMAKE_CURRENT_LIST_DIR}/hunter" ABSOLUTE)
HunterGate(URL "x" SHA1 "xxxxxxxx" FILEPATH ${CMAKE_CURRENT_LIST_DIR}/HunterConfig.cmake)

#==========================================================
#   Start Decent Decent Tester Project
#==========================================================
project(DecentTester)

#==========================================================
#   Add Hunter Libraries
#==========================================================
set(BUILD_SHARED_LIBS OFF)
set(BUILD_STATIC_LIBS ON)
set(USE_MSVC_RUNTIME_LIBRARY_DLL OFF)

hunter_add_package(Boost COMPONENTS filesystem)
hunter_add_package(OpenSSL)

set(Boost_USE_STATIC_LIBS ON)
set(Boost_USE_STATIC_RUNTIME ${HUNTER_BOOST_RUNTIME_STATIC})
set(Boost_NO_SYSTEM_PATHS ON)
find_package(Boost CONFIG REQUIRED system filesystem)

#==========================================================
#   Setup options
#==========================================================

if (WIN32)
	macro(get_WIN32_WINNT version)
		if(CMAKE_SYSTEM_VERSION)
			set(ver ${CMAKE_SYSTEM_VERSION})
			string(REGEX MATCH "^([0-9]+).([0-9])" ver ${ver})
			string(REGEX MATCH "^([0-9]+)" verMajor ${ver})
			# Check for Windows 10, b/c we'll need to convert to hex 'A'.
			if("${verMajor}" MATCHES "10")
				set(verMajor "A")
				string(REGEX REPLACE "^([0-9]+)" ${verMajor} ver ${ver})
			endif()
			# Remove all remaining '.' characters.
			string(REPLACE "." "" ver ${ver})
			# Prepend each digit with a zero.
			string(REGEX REPLACE "([0-9A-Z])" "0\\1" ver ${ver})
			set(${version} "0x${ver}")
		endif()
	endmacro()

	get_WIN32_WINNT(win_ver)
	message(STATUS "CMAKE_SYSTEM_VERSION: " "${CMAKE_SYSTEM_VERSION}")
	message(STATUS "_WIN32_WINNT: " "${win_ver}")
	add_definitions(-D_WIN32_WINNT=${win_ver})
endif(WIN32)

if(MSVC)
	set(COMMON_OPTIONS /W3 /wd4996 /we4239 /we4002 /we4700 /we4305 /EHsc /MP)
	set(DEBUG_OPTIONS /MTd /Od /Zi /DDEBUG)
	set(SIMULATE_OPTIONS /DSIMULATING_ENCLAVE)
	set(RELEASE_OPTIONS /MT /Ox /Oi /Ob2 /fp:fast /GR- /DEDEBUG)# /DNDEBUG
	
	set(COMMON_ENCLAVE_CXX_OPTIONS )
	
	set(ENCLAVE_LINKER_OPTIONS "/NODEFAULTLIB /NOENTRY")
	set(APP_DEBUG_LINKER_OPTIONS "/NODEFAULTLIB:libc.lib /NODEFAULTLIB:libcmt.lib /NODEFAULTLIB:msvcrt.lib /NODEFAULTLIB:libcd.lib /NODEFAULTLIB:msvcrtd.lib")
	set(APP_RELEASE_LINKER_OPTIONS "/NODEFAULTLIB:libc.lib /NODEFAULTLIB:libcmtd.lib /NODEFAULTLIB:msvcrt.lib /NODEFAULTLIB:libcd.lib /NODEFAULTLIB:msvcrtd.lib")
	
	set(COMMON_APP_DEFINES WIN32_LEAN_AND_MEAN CURL_STATICLIB BOOST_DATE_TIME_NO_LIB)
	set(COMMON_ENCLAVE_DEFINES ENCLAVE_ENVIRONMENT)
	
	set(Additional_Sys_Lib )
else()
	set(COMMON_OPTIONS -pthread)
	set(DEBUG_OPTIONS -O0 -g -DDEBUG -UNDEBUG -UEDEBUG)
	set(SIMULATE_OPTIONS -DSIMULATING_ENCLAVE)
	set(RELEASE_OPTIONS -O2 -DEDEBUG -UDEBUG) #-DNDEBUG defined by default
	
	set(COMMON_ENCLAVE_CXX_OPTIONS -std=c++11)
	
	set(ENCLAVE_LINKER_OPTIONS "")
	set(APP_DEBUG_LINKER_OPTIONS "")
	set(APP_RELEASE_LINKER_OPTIONS "")
	
	set(COMMON_APP_DEFINES CURL_STATICLIB BOOST_DATE_TIME_NO_LIB)
	set(COMMON_ENCLAVE_DEFINES ENCLAVE_ENVIRONMENT)
	
	set(Additional_Sys_Lib rt pthread)
endif()

set(DEBUG_OPTIONS ${COMMON_OPTIONS} ${DEBUG_OPTIONS})
set(DEBUGSIM_OPTIONS ${COMMON_OPTIONS} ${DEBUG_OPTIONS} ${SIMULATE_OPTIONS})
set(RELEASE_OPTIONS ${COMMON_OPTIONS} ${RELEASE_OPTIONS})

if(MSVC)
	set(CMAKE_EXE_LINKER_FLAGS_DEBUG "${CMAKE_EXE_LINKER_FLAGS_DEBUG} /DEBUG")
endif()

add_compile_options(
	"$<$<CONFIG:Debug>:${DEBUG_OPTIONS}>"
	"$<$<CONFIG:DebugSimulation>:${DEBUGSIM_OPTIONS}>"
	"$<$<CONFIG:Release>:${RELEASE_OPTIONS}>"
)

#Remove all standard libraries dependency here so that enclave DLL can be 
# compiled properly. And it will be added back later for non-enclave apps.
set(COMMON_STANDARD_LIBRARIES "${CMAKE_CXX_STANDARD_LIBRARIES_INIT}")
separate_arguments(COMMON_STANDARD_LIBRARIES)
set(CMAKE_CXX_STANDARD_LIBRARIES "")
set(CMAKE_C_STANDARD_LIBRARIES "")

if(MSVC) 
	#Removed Basic Runtime Checks in MSVC
	STRING (REGEX REPLACE "/RTC(su|[1su])" "" CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}")
	STRING (REGEX REPLACE "/RTC(su|[1su])" "" CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")
	STRING (REGEX REPLACE "/RTC(su|[1su])" "" CMAKE_C_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}")
	STRING (REGEX REPLACE "/RTC(su|[1su])" "" CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE}")
endif()

set(CMAKE_CXX_FLAGS_DEBUGSIMULATION ${CMAKE_CXX_FLAGS_DEBUG})
set(CMAKE_C_FLAGS_DEBUGSIMULATION ${CMAKE_C_FLAGS_DEBUG})
set(CMAKE_EXE_LINKER_FLAGS_DEBUGSIMULATION ${CMAKE_EXE_LINKER_FLAGS_DEBUG})
set(CMAKE_SHARED_LINKER_FLAGS_DEBUGSIMULATION ${CMAKE_SHARED_LINKER_FLAGS_DEBUG})
set(CMAKE_STATIC_LINKER_FLAGS_DEBUGSIMULATION ${CMAKE_STATIC_LINKER_FLAGS_DEBUG})

set(CMAKE_CONFIGURATION_TYPES Release Debug DebugSimulation)
set_property(GLOBAL PROPERTY DEBUG_CONFIGURATIONS Debug DebugSimulation)

#-------
# Flag results:
#-------
message(STATUS "Final set of flags")
message(STATUS "==================================================")
message(STATUS "CMake Standard Libraries:")
message(STATUS "${CMAKE_CXX_STANDARD_LIBRARIES_INIT}")
message(STATUS "CMake CXX Flags:")
message(STATUS "${CMAKE_CXX_FLAGS}")
message(STATUS "CMake CXX Flags (Debug):")
message(STATUS "${CMAKE_CXX_FLAGS_DEBUG}")
message(STATUS "CMake CXX Flags (Release):")
message(STATUS "${CMAKE_CXX_FLAGS_RELEASE}")
message(STATUS "CMake CXX Link Flags:")
message(STATUS "${CMAKE_EXE_LINKER_FLAGS}")
message(STATUS "CMake CXX Link Flags (Debug):")
message(STATUS "${CMAKE_EXE_LINKER_FLAGS_DEBUG}")
message(STATUS "CMake CXX Link Flags (Release):")
message(STATUS "${CMAKE_EXE_LINKER_FLAGS_RELEASE}")
message(STATUS "==================================================")
message(STATUS "")

#==========================================================
#   Add submodules
#==========================================================

##Header only libraries
set(TCLAP_INCLUDE_DIR ${CMAKE_CURRENT_LIST_DIR}/libs/tclap/include)


# set(DECENT_API_DECENT_SERVER ON CACHE BOOL "Add decent server module." FORCE)
set(DECENT_API_DECENT_APP ON CACHE BOOL "Add decent app module." FORCE)
add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/libs/decent-ra-api)

#Intel SGX SDK
include(${CMAKE_CURRENT_LIST_DIR}/libs/decent-ra-api/cmake/FindSgxSdk.cmake)

#==========================================================
#   Add files
#==========================================================

set(SOURCEDIR ${CMAKE_CURRENT_LIST_DIR}/sources)

#==========================================================
#   G++ linking flags
#==========================================================

if(MSVC)
	set(WHOLE_ARCHIVE_FLAG_BEGIN "")
	set(WHOLE_ARCHIVE_FLAG_END "")
	set(GROUP_FLAG_BEGIN "")
	set(GROUP_FLAG_END "")
else()
	set(WHOLE_ARCHIVE_FLAG_BEGIN -Wl,--whole-archive)
	set(WHOLE_ARCHIVE_FLAG_END -Wl,--no-whole-archive)
	set(GROUP_FLAG_BEGIN -Wl,--start-group)
	set(GROUP_FLAG_END -Wl,--end-group)
endif()

if(MSVC)
	set(BINARY_SUBDIRECTORY "$<CONFIG>")
else()
	set(BINARY_SUBDIRECTORY "")
endif()

#==========================================================
#   Projects
#==========================================================

if(${DHT_TEST_ENCLAVE})
	add_subdirectory(${SOURCEDIR}/DhtClient_Enclave)
	add_subdirectory(${SOURCEDIR}/DhtClientNonEnclave_Enclave)
endif()

if(${DHT_YCSB_TEST})
	add_subdirectory(${SOURCEDIR}/DhtClientYcsb_Java)
	add_subdirectory(${SOURCEDIR}/DhtClientYcsb_App)
	add_subdirectory(${SOURCEDIR}/DhtClientNonEnclaveYcsb_App)
endif()
