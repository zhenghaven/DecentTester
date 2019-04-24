cmake_minimum_required(VERSION 3.8)

set(GENERAL_TARGET_NAME DhtClientYcsb)

###########################################################
### EDL
###########################################################

set(EDL_U_SRC_OUTPUT ${CMAKE_CURRENT_LIST_DIR}/Enclave_u.h ${CMAKE_CURRENT_LIST_DIR}/Enclave_u.c)
set(ENCLAVE_SRC_DIR ${CMAKE_CURRENT_LIST_DIR}/../DhtClient_Enclave)

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

add_custom_target(${GENERAL_TARGET_NAME}_EDL DEPENDS ${EDL_U_SRC_OUTPUT})
set_target_properties(${GENERAL_TARGET_NAME}_EDL PROPERTIES FOLDER "${GENERAL_TARGET_NAME}")
