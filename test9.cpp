#include <iostream>
#include <map>

int main() {
  const std::map<int, const char *> m{
      {0, "zero"},
      {1, "one"},
      {2, "two"},
  };

  {
    auto p = m.equal_range(1);
    for (auto &q = p.first; q != p.second; ++q) {
      std::cout << "m[" << q->first << "] = " << q->second << '\n';
    }

    if (p.second == m.find(2)) {
      std::cout << "end of equal_range (p.second) is one-past p.first\n";
    } else {
      std::cout << "unexpected; p.second expected to be one-past p.first\n";
    }
  }

  {
    auto pp = m.equal_range(-1);
    if (pp.first == m.begin()) {
      std::cout << "pp.first is iterator to first not-less than -1\n";
    } else {
      std::cout << "unexpected pp.first\n";
    }

    if (pp.second == m.begin()) {
      std::cout << "pp.second is iterator to first element greater-than -1\n";
    } else {
      std::cout << "unexpected pp.second\n";
    }
  }

  {
    auto ppp = m.equal_range(3);
    if (ppp.first == m.end()) {
      std::cout << "ppp.first is iterator to first not-less than 3\n";
    } else {
      std::cout << "unexpected ppp.first\n";
    }

    if (ppp.second == m.end()) {
      std::cout << "ppp.second is iterator to first element greater-than 3\n";
    } else {
      std::cout << "unexpected ppp.second\n";
    }
  }
}
