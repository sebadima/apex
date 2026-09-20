#include "apex/apex.hpp"
#include <iostream>
#include <cassert>

int main() {
    apex::Core engine;

    std::cout << "[TEST] Versione: " << engine.get_version() << std::endl;

    int res = engine.add(2, 3);
    assert(res == 5);

    std::cout << "[TEST] add(2, 3) = " << res << " -> OK" << std::endl;
    return 0;
}