/*
 * NamedStats.cpp
 *
 */

#include "NamedStats.h"

#include <iomanip>
#include <iostream>

NamedStats& NamedStats::operator+=(const NamedStats& other)
{
    for (auto x : other)
        (*this)[x.first] += x.second;
    return *this;
}

void NamedStats::print()
{
    long sum = 0;
    for (auto x : *this)
        sum += x.second;
    if (sum > 0)
        cerr << "Detailed costs:" << endl;
    for (auto x : *this)
    {
        if (x.second > 0)
        {
            cerr.fill(' ');
            cerr << "    ";
            cerr << setw(10) << x.second << " " << x.first << endl;
        }
    }
}
