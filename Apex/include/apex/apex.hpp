#pragma once

#include <string>

namespace apex {

class Core {
public:
    Core() = default;
    std::string get_version() const;
    int add(int a, int b) const;
};

} // namespace apex