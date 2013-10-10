CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

################################################################################

PROJECT(Pore)
  
ADD_LIBRARY(poreclient client.cpp)

INSTALL(
  FILES client.h common.h
  DESTINATION include/pore)

INSTALL(
  TARGETS poreclient 
  DESTINATION lib)
