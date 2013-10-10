CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

################################################################################

ADD_EXECUTABLE(testclient testclient.cpp)
TARGET_LINK_LIBRARIES(testclient poreclient)
