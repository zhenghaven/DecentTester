cmake_minimum_required(VERSION 3.8)

set(PROJECT_NAME DhtClientNonEnclave)

# Source Files:
set(COMMON_ENCLAVE_SRC_DIR ${CMAKE_CURRENT_LIST_DIR}/../Common_Enclave)
file(GLOB_RECURSE SOURCES_${PROJECT_NAME}_Enc ${CMAKE_CURRENT_LIST_DIR}/*.[ch]*)

file(GLOB_RECURSE SOURCES_COMMON_Enc ${COMMON_ENCLAVE_SRC_DIR}/*.[ch]*)

source_group(TREE ${CMAKE_CURRENT_LIST_DIR}/../ FILES ${SOURCES_${PROJECT_NAME}_Enc} ${SOURCES_COMMON_Enc})

###########################################################
### Enclave
###########################################################

add_library(${PROJECT_NAME}_Enclave STATIC ${SOURCES_${PROJECT_NAME}_Enc} ${SOURCES_COMMON_Enc})
#defines:
target_compile_definitions(${PROJECT_NAME}_Enclave PRIVATE ${COMMON_ENCLAVE_DEFINES} ENCLAVE_PLATFORM_NON_ENCLAVE)
#compiler flags:
target_compile_options(${PROJECT_NAME}_Enclave PRIVATE ${INTEL_SGX_SDK_C_FLAGS} $<$<COMPILE_LANGUAGE:CXX>:${INTEL_SGX_SDK_CXX_FLAGS} ${COMMON_ENCLAVE_CXX_OPTIONS}>)
#linker flags:
set_target_properties(${PROJECT_NAME}_Enclave PROPERTIES LINK_FLAGS "${ENCLAVE_LINKER_OPTIONS}")
set_target_properties(${PROJECT_NAME}_Enclave PROPERTIES FOLDER "${PROJECT_NAME}")

target_link_libraries(${PROJECT_NAME}_Enclave 
	DecentRa_App_App 
	mbedtls 
)
