cmake_minimum_required(VERSION 3.8)

include(../../cmake/JavaJni.cmake)

set(PROJECT_NAME DhtClientYcsb)
set(YCSB_TARGET_LIBS_DIR ${YCSB_ROOT_DIR}/decentdht/libs)

set(${PROJECT_NAME}_JAR_NAME dht-0.1.0.jar)

set(${PROJECT_NAME}_JNI_HEADER ${CMAKE_CURRENT_LIST_DIR}/com_decent_dht_DhtClientBinding.h
	                           ${CMAKE_CURRENT_LIST_DIR}/com_decent_dht_DhtClientNonEnclaveBinding.h)

set(${PROJECT_NAME}_JAVA_SRC_JNI ${CMAKE_CURRENT_LIST_DIR}/com/decent/dht/DhtClientBinding.java
	                             ${CMAKE_CURRENT_LIST_DIR}/com/decent/dht/DhtClientNonEnclaveBinding.java)

set(${PROJECT_NAME}_JAVA_SRC ${CMAKE_CURRENT_LIST_DIR}/com/decent/dht/DhtClientBinding.java
	                         ${CMAKE_CURRENT_LIST_DIR}/com/decent/dht/DhtClientNonEnclaveBinding.java
	                         ${CMAKE_CURRENT_LIST_DIR}/com/decent/dht/DhtClientBindingException.java)

set(${PROJECT_NAME}_JAVA_BIN ${CMAKE_CURRENT_LIST_DIR}/com/decent/dht/DhtClientBinding.class
	                         ${CMAKE_CURRENT_LIST_DIR}/com/decent/dht/DhtClientNonEnclaveBinding.class
	                         ${CMAKE_CURRENT_LIST_DIR}/com/decent/dht/DhtClientBindingException.class)

set(${PROJECT_NAME}_GENERATED_FILES ${${PROJECT_NAME}_JNI_HEADER} ${${PROJECT_NAME}_JAVA_BIN} "${YCSB_TARGET_LIBS_DIR}/${${PROJECT_NAME}_JAR_NAME}")

add_custom_command(OUTPUT  ${${PROJECT_NAME}_GENERATED_FILES}
	               COMMAND ${JAVAC_BIN_PATH} -h . ${${PROJECT_NAME}_JAVA_SRC_JNI}
	               COMMAND ${JAR_BIN_PATH} cf ${${PROJECT_NAME}_JAR_NAME} ${${PROJECT_NAME}_JAVA_BIN}
	               COMMAND ${CMAKE_COMMAND} -E copy "${CMAKE_CURRENT_LIST_DIR}/${${PROJECT_NAME}_JAR_NAME}"
	                                                "${YCSB_TARGET_LIBS_DIR}/${${PROJECT_NAME}_JAR_NAME}"
	               WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
	               DEPENDS ${${PROJECT_NAME}_JAVA_SRC}
	               COMMENT "Generating JNI header..."
)

add_custom_target(${PROJECT_NAME}_Java DEPENDS ${${PROJECT_NAME}_GENERATED_FILES})
set_target_properties(${PROJECT_NAME}_Java PROPERTIES FOLDER "${PROJECT_NAME}")
set_property(DIRECTORY APPEND PROPERTY ADDITIONAL_MAKE_CLEAN_FILES ${${PROJECT_NAME}_GENERATED_FILES})
