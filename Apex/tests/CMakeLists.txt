add_executable(apex_tests test_main.cpp)
target_link_libraries(apex_tests PRIVATE Apex::apex)

add_test(NAME ApexUnitTests COMMAND apex_tests)
