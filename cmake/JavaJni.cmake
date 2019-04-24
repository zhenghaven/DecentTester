cmake_minimum_required(VERSION 3.8)

set(JAVA_HOME_DIR $ENV{JAVA_HOME})

if((NOT EXISTS ${JAVA_HOME_DIR}) OR
		(NOT EXISTS ${JAVA_HOME_DIR}/bin) OR
		(NOT EXISTS ${JAVA_HOME_DIR}/include) OR
		(NOT EXISTS ${JAVA_HOME_DIR}/lib))
	message(FATAL_ERROR "JAVA JDK is required, but it cannot be found!")
endif()

if(MSVC)
	set(JAVAC_BIN_PATH ${JAVA_HOME_DIR}/bin/javac.exe)
	set(JAVA_INCLUDE_OS win32)
else()
	set(JAVAC_BIN_PATH ${JAVA_HOME_DIR}/bin/javac)
	set(JAVA_INCLUDE_OS linux)
endif()

if(NOT TARGET Java::JNI)
	add_library(Java::JNI INTERFACE IMPORTED GLOBAL)
	target_include_directories(Java::JNI INTERFACE ${JAVA_HOME_DIR}/include ${JAVA_HOME_DIR}/include/${JAVA_INCLUDE_OS})
endif()
