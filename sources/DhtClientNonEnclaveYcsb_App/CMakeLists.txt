cmake_minimum_required(VERSION 3.8)

set(PROJECT_NAME DhtClientNonEnclaveYcsb)
set(ENCLAVE_PROJECT_NAME DhtClientNonEnclave)

# Source Files:
set(COMMON_APP_SRC_DIR ${CMAKE_CURRENT_LIST_DIR}/../Common_App)
file(GLOB_RECURSE SOURCES_${PROJECT_NAME}_App ${CMAKE_CURRENT_LIST_DIR}/*.[ch]*)

file(GLOB_RECURSE SOURCES_COMMON_App ${COMMON_APP_SRC_DIR}/*.[ch]*)

list(REMOVE_ITEM SOURCES_${PROJECT_NAME}_App "${CMAKE_CURRENT_LIST_DIR}/Debugger.cpp")

source_group(TREE ${CMAKE_CURRENT_LIST_DIR}/../ FILES ${SOURCES_${PROJECT_NAME}_App} ${SOURCES_COMMON_App})

###########################################################
### App
###########################################################

add_library(${PROJECT_NAME}_App SHARED ${SOURCES_${PROJECT_NAME}_App} ${SOURCES_COMMON_App})
#defines:
target_compile_definitions(${PROJECT_NAME}_App PRIVATE ${COMMON_APP_DEFINES} ENCLAVE_PLATFORM_NON_ENCLAVE)
#linker flags:
set_target_properties(${PROJECT_NAME}_App PROPERTIES LINK_FLAGS_DEBUG "${APP_DEBUG_LINKER_OPTIONS}")
set_target_properties(${PROJECT_NAME}_App PROPERTIES LINK_FLAGS_DEBUGSIMULATION "${APP_DEBUG_LINKER_OPTIONS}")
set_target_properties(${PROJECT_NAME}_App PROPERTIES LINK_FLAGS_RELEASE "${APP_RELEASE_LINKER_OPTIONS}")
set_target_properties(${PROJECT_NAME}_App PROPERTIES FOLDER "${PROJECT_NAME}")

target_link_libraries(${PROJECT_NAME}_App 
	${COMMON_STANDARD_LIBRARIES} 
	${ENCLAVE_PROJECT_NAME}_Enclave
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



###########################################################
### Debugger
###########################################################

add_executable(${PROJECT_NAME}_Debugger Debugger.cpp)
#includes:
# target_include_directories(${PROJECT_NAME}_Debugger PRIVATE ${TCLAP_INCLUDE_DIR})
#defines:
target_compile_definitions(${PROJECT_NAME}_Debugger PRIVATE ${COMMON_APP_DEFINES} ENCLAVE_PLATFORM_NON_ENCLAVE)
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
