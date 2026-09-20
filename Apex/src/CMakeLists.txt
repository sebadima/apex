add_library(apex_lib apex.cpp)
add_library(Apex::apex ALIAS apex_lib)

target_include_directories(apex_lib
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
)
