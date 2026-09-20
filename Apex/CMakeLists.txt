cmake_minimum_required(VERSION 3.16)

project(
    Apex
    VERSION 0.1.0
    DESCRIPTION "Progetto C++ per robotica e sistemi embedded"
    LANGUAGES CXX
)

# Standard C++20
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Genera compile_commands.json per LSP (clangd, ZED, Neovim)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Opzioni di compilazione
option(APEX_BUILD_TESTS "Compila i test unitari" OFF)
option(APEX_BUILD_EXAMPLES "Compila gli esempi" OFF)
option(APEX_BUILD_TOOLS "Compila le utility e i tool CLI" OFF)

# Warning del compilatore
if(MSVC)
    add_compile_options(/W4 /permissive-)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Wconversion -Wshadow)
endif()

# Cartelle di output
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Abilita le sottodirectory solo quando creerai i relativi CMakeLists.txt interni
# add_subdirectory(src)
# if(APEX_BUILD_TESTS)
#     enable_testing()
#     add_subdirectory(tests)
# endif()
# if(APEX_BUILD_EXAMPLES)
#     add_subdirectory(examples)
# endif()
# if(APEX_BUILD_TOOLS)
#     add_subdirectory(tools)
# endif()