#include <deque>
#include <iomanip>
#include <iostream>

int main() {
  std::deque<std::string> numbers;

  numbers.push_back("abc");
  std::string s = "def";
  numbers.push_back(std::move(s));

  std::cout << "deque holds: ";
  for (auto &&i : numbers)
    std::cout << std::quoted(i) << ' ';
  std::cout << "\nMoved-from string holds " << std::quoted(s) << '\n';
}
