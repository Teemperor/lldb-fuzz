#include <iostream>
#include <set>

int main() {
  std::multiset<int> numbers;
  std::cout << "Initially, numbers.empty(): " << numbers.empty() << '\n';

  numbers.insert(42);
  numbers.insert(13317);
  std::cout << "After adding elements, numbers.empty(): " << numbers.empty()
            << '\n';
}
