#include <deque>
#include <iostream>

int main() {
  std::deque<char> s;
  std::cout << "Maximum size of a 'deque' is " << s.max_size() << "\n";
}
