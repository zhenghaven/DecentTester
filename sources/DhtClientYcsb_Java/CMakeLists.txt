cmake_minimum_required(VERSION 3.8)

include(../../cmake/JavaJni.cmake)

add_custom_command(OUTPUT DecentDhtClient.h
	COMMAND ${JAVAC_BIN_PATH} -h . DecentDhtClient.java
	WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
	DEPENDS DecentDhtClient.java
	COMMENT "Generating JNI header..."
)

add_custom_target(DhtClientYcsb_Java DEPENDS DecentDhtClient.h)
set_target_properties(DhtClientYcsb_Java PROPERTIES FOLDER "DhtClientYcsb")
