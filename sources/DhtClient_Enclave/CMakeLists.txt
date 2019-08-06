cmake_minimum_required(VERSION 3.8)

set(PROJECT_NAME DhtClientSgx)

# Source Files:
set(COMMON_ENCLAVE_SRC_DIR ${CMAKE_CURRENT_LIST_DIR}/../Common_Enclave)
file(GLOB_RECURSE SOURCES_${PROJECT_NAME}_Enc ${CMAKE_CURRENT_LIST_DIR}/*.[ch]*)
file(GLOB_RECURSE SOURCES_${PROJECT_NAME}_EDL ${CMAKE_CURRENT_LIST_DIR}/*.edl)

file(GLOB_RECURSE SOURCES_COMMON_Enc ${COMMON_ENCLAVE_SRC_DIR}/*.[ch]*)

source_group(TREE ${CMAKE_CURRENT_LIST_DIR}/../ FILES ${SOURCES_${PROJECT_NAME}_Enc} ${SOURCES_${PROJECT_NAME}_EDL} ${SOURCES_COMMON_Enc})

###########################################################
### EDL
###########################################################

set(EDL_T_SRC_OUTPUT ${CMAKE_CURRENT_LIST_DIR}/Enclave_t.h ${CMAKE_CURRENT_LIST_DIR}/Enclave_t.c)

add_custom_command(OUTPUT ${EDL_T_SRC_OUTPUT}
	COMMAND "${INTEL_SGX_EDGER_PATH}"  
	--trusted "${CMAKE_CURRENT_LIST_DIR}/Enclave.edl" 
	--search-path "${CMAKE_CURRENT_LIST_DIR}" 
	--search-path "${DECENT_API_EDL_DIR}" 
	--search-path "${INTEL_SGX_SDK_INCLUDE_DIR}"
	WORKING_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}"
	DEPENDS "${CMAKE_CURRENT_LIST_DIR}/Enclave.edl"
	COMMENT "Processing EDL for enclave..."
)

add_custom_target(${PROJECT_NAME}_EDL DEPENDS ${EDL_T_SRC_OUTPUT})
set_target_properties(${PROJECT_NAME}_EDL PROPERTIES FOLDER "${PROJECT_NAME}")

###########################################################
### Enclave
###########################################################

set(${PROJECT_NAME}_ENCLAVE_SIGNED "${CMAKE_SHARED_LIBRARY_PREFIX}${PROJECT_NAME}_Enclave$<$<CONFIG:Debug>:${CMAKE_DEBUG_POSTFIX}>.signed${CMAKE_SHARED_LIBRARY_SUFFIX}")
set(${PROJECT_NAME}_ENCLAVE_LIB "${CMAKE_SHARED_LIBRARY_PREFIX}${PROJECT_NAME}_Enclave$<$<CONFIG:Debug>:${CMAKE_DEBUG_POSTFIX}>${CMAKE_SHARED_LIBRARY_SUFFIX}")

add_library(${PROJECT_NAME}_Enclave SHARED ${SOURCES_${PROJECT_NAME}_Enc} ${SOURCES_${PROJECT_NAME}_EDL} ${SOURCES_COMMON_Enc})
#defines:
target_compile_definitions(${PROJECT_NAME}_Enclave PRIVATE ${COMMON_ENCLAVE_DEFINES} ENCLAVE_PLATFORM_SGX)
#compiler flags:
target_compile_options(${PROJECT_NAME}_Enclave PRIVATE ${INTEL_SGX_SDK_C_FLAGS} $<$<COMPILE_LANGUAGE:CXX>:${INTEL_SGX_SDK_CXX_FLAGS} ${COMMON_ENCLAVE_CXX_OPTIONS}>)
#linker flags:
set_target_properties(${PROJECT_NAME}_Enclave PROPERTIES LINK_FLAGS "${ENCLAVE_LINKER_OPTIONS} ${INTEL_SGX_SDK_LINKER_FLAGS_T}")
set_target_properties(${PROJECT_NAME}_Enclave PROPERTIES FOLDER "${PROJECT_NAME}")

add_custom_command(TARGET ${PROJECT_NAME}_Enclave
	POST_BUILD
	COMMAND "${INTEL_SGX_SIGNER_PATH}" sign
	-key "${CMAKE_SOURCE_DIR}/Enclave_private.pem"
	-enclave "${CMAKE_CURRENT_BINARY_DIR}/${BINARY_SUBDIRECTORY}/${${PROJECT_NAME}_ENCLAVE_LIB}"
	-out "${CMAKE_CURRENT_BINARY_DIR}/${${PROJECT_NAME}_ENCLAVE_SIGNED}"
	-config "${CMAKE_CURRENT_LIST_DIR}/Enclave.config.xml"
	COMMAND ${CMAKE_COMMAND} -E copy "${CMAKE_CURRENT_BINARY_DIR}/${${PROJECT_NAME}_ENCLAVE_SIGNED}"
	"${CMAKE_BINARY_DIR}"
)

target_link_libraries(${PROJECT_NAME}_Enclave 
	${WHOLE_ARCHIVE_FLAG_BEGIN} 
	IntelSGX::Trusted::switchless 
	IntelSGX::Trusted::rts 
	${WHOLE_ARCHIVE_FLAG_END}
	${GROUP_FLAG_BEGIN}
	IntelSGX::Trusted::stdc 
	IntelSGX::Trusted::cxx 
	IntelSGX::Trusted::service 
	IntelSGX::Trusted::key_exchange 
	IntelSGX::Trusted::crypto 
	IntelSGX::Trusted::file_system 
	DecentRa_App_Enclave 
	mbedcrypto_enclave 
	mbedx509_enclave 
	mbedtls_enclave 
	${GROUP_FLAG_END}
)

add_dependencies(${PROJECT_NAME}_Enclave ${PROJECT_NAME}_EDL)
