#include "apex/apex.hpp"

namespace apex {

std::string Core::get_version() const {
    return "Apex Engine v0.1.0";
}

int Core::add(int a, int b) const {
    return a + b;
}

} // namespace apex
