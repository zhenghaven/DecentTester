cmake_minimum_required(VERSION 3.8)

set(PROJECT_NAME DhtClientYcsb)
set(ENCLAVE_PROJECT_NAME DhtClientSgx)

# Source Files:
set(COMMON_APP_SRC_DIR ${CMAKE_CURRENT_LIST_DIR}/../Common_App)
set(ENCLAVE_SRC_DIR ${CMAKE_CURRENT_LIST_DIR}/../DhtClient_Enclave)
file(GLOB_RECURSE SOURCES_${PROJECT_NAME}_App ${CMAKE_CURRENT_LIST_DIR}/*.[ch]*)
file(GLOB_RECURSE SOURCES_${PROJECT_NAME}_EDL ${ENCLAVE_SRC_DIR}/*.edl)

file(GLOB_RECURSE SOURCES_COMMON_App ${COMMON_APP_SRC_DIR}/*.[ch]*)

list(REMOVE_ITEM SOURCES_${PROJECT_NAME}_App "${CMAKE_CURRENT_LIST_DIR}/Debugger.cpp")

source_group(TREE ${CMAKE_CURRENT_LIST_DIR}/../ FILES ${SOURCES_${PROJECT_NAME}_App} ${SOURCES_COMMON_App})

###########################################################
### EDL
###########################################################

set(EDL_U_SRC_OUTPUT ${CMAKE_CURRENT_LIST_DIR}/Enclave_u.h ${CMAKE_CURRENT_LIST_DIR}/Enclave_u.c)

add_custom_command(OUTPUT ${EDL_U_SRC_OUTPUT}
	COMMAND "${INTEL_SGX_EDGER_PATH}"  
	--untrusted "${ENCLAVE_SRC_DIR}/Enclave.edl" 
	--search-path "${ENCLAVE_SRC_DIR}" 
	--search-path "${DECENT_API_EDL_DIR}" 
	--search-path "${INTEL_SGX_SDK_INCLUDE_DIR}"
	WORKING_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}"
	DEPENDS "${ENCLAVE_SRC_DIR}/Enclave.edl"
	COMMENT "Processing EDL for app..."
)

add_custom_target(${PROJECT_NAME}_EDL DEPENDS ${EDL_U_SRC_OUTPUT})
set_target_properties(${PROJECT_NAME}_EDL PROPERTIES FOLDER "${PROJECT_NAME}")

###########################################################
### App
###########################################################

set(${PROJECT_NAME}_ENCLAVE_SIGNED "${CMAKE_SHARED_LIBRARY_PREFIX}${ENCLAVE_PROJECT_NAME}_Enclave$<$<CONFIG:Debug>:${CMAKE_DEBUG_POSTFIX}>.signed${CMAKE_SHARED_LIBRARY_SUFFIX}")
set(${PROJECT_NAME}_ENCLAVE_LIB "${CMAKE_SHARED_LIBRARY_PREFIX}${ENCLAVE_PROJECT_NAME}_Enclave$<$<CONFIG:Debug>:${CMAKE_DEBUG_POSTFIX}>${CMAKE_SHARED_LIBRARY_SUFFIX}")

add_library(${PROJECT_NAME}_App SHARED ${SOURCES_${PROJECT_NAME}_App} ${SOURCES_${PROJECT_NAME}_EDL} ${SOURCES_COMMON_App})
#defines:
target_compile_definitions(${PROJECT_NAME}_App PRIVATE ${COMMON_APP_DEFINES} ENCLAVE_PLATFORM_SGX ENCLAVE_FILENAME="${${PROJECT_NAME}_ENCLAVE_SIGNED}" TOKEN_FILENAME="${PROJECT_NAME}_Enclave.token")
#linker flags:
set_target_properties(${PROJECT_NAME}_App PROPERTIES LINK_FLAGS_DEBUG "${APP_DEBUG_LINKER_OPTIONS}")
set_target_properties(${PROJECT_NAME}_App PROPERTIES LINK_FLAGS_DEBUGSIMULATION "${APP_DEBUG_LINKER_OPTIONS}")
set_target_properties(${PROJECT_NAME}_App PROPERTIES LINK_FLAGS_RELEASE "${APP_RELEASE_LINKER_OPTIONS}")
set_target_properties(${PROJECT_NAME}_App PROPERTIES FOLDER "${PROJECT_NAME}")

target_link_libraries(${PROJECT_NAME}_App 
	${COMMON_STANDARD_LIBRARIES} 
	IntelSGX::Untrusted::Libs
	DecentRa_App_App 
	jsoncpp_lib_static 
	mbedcrypto 
	mbedx509 
	mbedtls 
	Boost::filesystem
	Boost::system
	Java::JNI
	${Additional_Sys_Lib}
)

add_custom_command(TARGET ${PROJECT_NAME}_App
	POST_BUILD
	COMMAND ${CMAKE_COMMAND} -E copy "${CMAKE_CURRENT_BINARY_DIR}/${BINARY_SUBDIRECTORY}/${CMAKE_SHARED_LIBRARY_PREFIX}${PROJECT_NAME}_App${CMAKE_SHARED_LIBRARY_SUFFIX}"
	"${CMAKE_BINARY_DIR}"
)

add_dependencies(${PROJECT_NAME}_App ${PROJECT_NAME}_EDL)

###########################################################
### Debugger
###########################################################

set(ENCLAVE_BIN_DIR ${CMAKE_CURRENT_BINARY_DIR}/../DhtClient_Enclave)

add_executable(${PROJECT_NAME}_Debugger Debugger.cpp)
#includes:
# target_include_directories(${PROJECT_NAME}_Debugger PRIVATE ${TCLAP_INCLUDE_DIR})
#defines:
target_compile_definitions(${PROJECT_NAME}_Debugger PRIVATE ${COMMON_APP_DEFINES} ENCLAVE_FILENAME="${${PROJECT_NAME}_ENCLAVE_SIGNED}" TOKEN_FILENAME="${PROJECT_NAME}_Enclave.token")
#linker flags:
set_target_properties(${PROJECT_NAME}_Debugger PROPERTIES LINK_FLAGS_DEBUG "${APP_DEBUG_LINKER_OPTIONS}")
set_target_properties(${PROJECT_NAME}_Debugger PROPERTIES LINK_FLAGS_DEBUGSIMULATION "${APP_DEBUG_LINKER_OPTIONS}")
set_target_properties(${PROJECT_NAME}_Debugger PROPERTIES LINK_FLAGS_RELEASE "${APP_RELEASE_LINKER_OPTIONS}")
set_target_properties(${PROJECT_NAME}_Debugger PROPERTIES FOLDER "${PROJECT_NAME}")

target_link_libraries(${PROJECT_NAME}_Debugger 
	${COMMON_STANDARD_LIBRARIES} 
	${PROJECT_NAME}_App
	${Additional_Sys_Lib}
)

add_custom_command(TARGET ${PROJECT_NAME}_Debugger 
	POST_BUILD
	COMMAND ${CMAKE_COMMAND} -E copy "${ENCLAVE_BIN_DIR}/${${PROJECT_NAME}_ENCLAVE_SIGNED}" "${CMAKE_CURRENT_BINARY_DIR}/${${PROJECT_NAME}_ENCLAVE_SIGNED}"
)
add_dependencies(${PROJECT_NAME}_Debugger ${ENCLAVE_PROJECT_NAME}_Enclave)
