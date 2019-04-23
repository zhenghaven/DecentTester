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
else()
	set(JAVAC_BIN_PATH ${JAVA_HOME_DIR}/bin/javac)
endif()
