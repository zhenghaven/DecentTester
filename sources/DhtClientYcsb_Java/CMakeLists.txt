cmake_minimum_required(VERSION 3.8)

include(../../cmake/JavaJni.cmake)

add_custom_command(OUTPUT com_Decent_DhtClientBinding.h
	COMMAND ${JAVAC_BIN_PATH} -h . com/decent/dht/DhtClientBinding.java
	WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
	DEPENDS com/decent/dht/DhtClientBinding.java
	COMMENT "Generating JNI header..."
)

add_custom_target(DhtClientYcsb_Java DEPENDS com_Decent_DhtClientBinding.h)
set_target_properties(DhtClientYcsb_Java PROPERTIES FOLDER "DhtClientYcsb")
