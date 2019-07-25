#include <string>
#include <iostream>
 
int main()
{
    std::string a = "0123456789abcdefghij";
 
    // count is npos, returns [pos, size())
    std::string sub1 = a.substr(10);
    std::cout << sub1 << '\n';
 
    // both pos and pos+count are within bounds, returns [pos, pos+count)
    std::string sub2 = a.substr(5, 3);
    std::cout << sub2 << '\n';
 
    // pos is within bounds, pos+count is not, returns [pos, size()) 
    std::string sub4 = a.substr(a.size()-3, 50);
    std::cout << sub4 << '\n';
 
    try {
        // pos is out of bounds, throws
        std::string sub5 = a.substr(a.size()+3, 50);
        std::cout << sub5 << '\n';
    } catch(const std::out_of_range& e) {
        std::cout << "pos exceeds string size\n";
    }
}
