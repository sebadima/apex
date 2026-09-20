cmake_minimum_required(VERSION 3.16)

# Configurazione del progetto
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

# Genera compile_commands.json per strumenti LSP (clangd, ZED, Neovim)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Opzioni di compilazione
option(APEX_BUILD_TESTS "Compila i test unitari" ON)
option(APEX_BUILD_EXAMPLES "Compila gli esempi" ON)
option(APEX_BUILD_TOOLS "Compila le utility e i tool CLI" ON)

# Configurazione dei flag di warning del compilatore
if(MSVC)
    add_compile_options(/W4 /permissive-)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Wconversion -Wshadow)
endif()

# Cartelle di output per i binari generati
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Sottodirectory del codice sorgente principale
add_subdirectory(src)

# Sottodirectory condizionali
if(APEX_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

if(APEX_BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

if(APEX_BUILD_TOOLS)
    add_subdirectory(tools)
endif()