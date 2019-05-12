cmake_minimum_required(VERSION 3.8)

set(PROJECT_NAME DhtClientYcsb)
set(ENCLAVE_PROJECT_NAME DhtClientSgx)
set(YCSB_TARGET_LIBS_DIR ${YCSB_ROOT_DIR}/decentdht/libs)
set(${PROJECT_NAME}_JAR_NAME dht-0.1.0.jar)

# Source Files:
set(COMMON_APP_SRC_DIR ${CMAKE_CURRENT_LIST_DIR}/../Common_App)
set(ENCLAVE_SRC_DIR ${CMAKE_CURRENT_LIST_DIR}/../DhtClient_Enclave)
file(GLOB_RECURSE SOURCES_${PROJECT_NAME}_App ${CMAKE_CURRENT_LIST_DIR}/*.[ch]*)
file(GLOB_RECURSE SOURCES_${PROJECT_NAME}_EDL ${ENCLAVE_SRC_DIR}/*.edl)

file(GLOB_RECURSE SOURCES_COMMON_App ${COMMON_APP_SRC_DIR}/*.[ch]*)

list(REMOVE_ITEM SOURCES_${PROJECT_NAME}_App "Debugger.cpp")

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
target_compile_definitions(${PROJECT_NAME}_App PRIVATE ${COMMON_APP_DEFINES} ENCLAVE_FILENAME="${${PROJECT_NAME}_ENCLAVE_SIGNED}" TOKEN_FILENAME="${PROJECT_NAME}_Enclave.token")
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

###########################################################
### Installer
###########################################################

set(${PROJECT_NAME}_ENCLAVE_SIGNED_JAVAINS "${CMAKE_SHARED_LIBRARY_PREFIX}${ENCLAVE_PROJECT_NAME}_Enclave.signed${CMAKE_SHARED_LIBRARY_SUFFIX}")
set(${PROJECT_NAME}_SHARED_LIB_NAME ${CMAKE_SHARED_LIBRARY_PREFIX}${PROJECT_NAME}_App${CMAKE_SHARED_LIBRARY_SUFFIX})
set(${PROJECT_NAME}_Java_SRC_DIR ${CMAKE_CURRENT_LIST_DIR}/../${PROJECT_NAME}_Java)

add_custom_command(OUTPUT ${YCSB_ROOT_DIR}/${${PROJECT_NAME}_SHARED_LIB_NAME} 
	                      ${YCSB_TARGET_LIBS_DIR}/${${PROJECT_NAME}_ENCLAVE_SIGNED_JAVAINS} 
	                      ${YCSB_TARGET_LIBS_DIR}/${${PROJECT_NAME}_JAR_NAME} 
	               COMMAND ${CMAKE_COMMAND} -E copy "${CMAKE_CURRENT_BINARY_DIR}/${${PROJECT_NAME}_ENCLAVE_SIGNED}" 
	                                                "${YCSB_ROOT_DIR}/${${PROJECT_NAME}_ENCLAVE_SIGNED_JAVAINS}"
	               COMMAND ${CMAKE_COMMAND} -E copy "${CMAKE_CURRENT_BINARY_DIR}/${BINARY_SUBDIRECTORY}/${${PROJECT_NAME}_SHARED_LIB_NAME}" 
	                                                "${YCSB_ROOT_DIR}/${${PROJECT_NAME}_SHARED_LIB_NAME}"
	               COMMAND ${CMAKE_COMMAND} -E copy "${${PROJECT_NAME}_Java_SRC_DIR}/${${PROJECT_NAME}_JAR_NAME}" 
	                                                "${YCSB_TARGET_LIBS_DIR}/${${PROJECT_NAME}_JAR_NAME}"
	               WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
	               DEPENDS ${PROJECT_NAME}_Debugger
	               COMMENT "Installing JNI and shared libraries..."
)

add_custom_target(${PROJECT_NAME}_Install DEPENDS ${YCSB_ROOT_DIR}/${${PROJECT_NAME}_ENCLAVE_SIGNED_JAVAINS} 
	                                              ${YCSB_ROOT_DIR}/${${PROJECT_NAME}_SHARED_LIB_NAME} 
	                                              ${YCSB_TARGET_LIBS_DIR}/${${PROJECT_NAME}_JAR_NAME})

set_target_properties(${PROJECT_NAME}_Install PROPERTIES FOLDER "${PROJECT_NAME}")
