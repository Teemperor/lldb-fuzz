#include <array>
#include <iostream>

int main() {
  std::array<char, 10> s;
  std::cout << "Maximum size of a 'array' is " << s.max_size() << "\n";
}
