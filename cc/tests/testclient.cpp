#include "poreclient.h"
#include <vector>
#include <cstdlib>
#include <iostream>

using namespace std;

int main(int argc, char **argv)
{
    if (argc < 2) {
        cerr << "usage: test_client array_count [port]\n";
        exit(1);
    }
    int sz = atoi(argv[1]);
    int port_number;

    if (argc > 2) {
        port_number = atoi(argv[2]);
    } else
        port_number = 10943;
    vector<int> data;
    vector<float> data_f;
    for (size_t i=0; i<sz; ++i) {
        data.push_back(i);
        data_f.push_back(i);
    }
    pore::send(data, "foo", port_number);
    pore::send(data_f, "foo_float", port_number);
}
