/*
 * NamedStats.h
 *
 */

#ifndef TOOLS_NAMEDSTATS_H_
#define TOOLS_NAMEDSTATS_H_

#include <map>
#include <string>

using namespace std;

class NamedStats : public map<string, long>
{
public:
    NamedStats& operator+=(const NamedStats& other);

    void print();
};

#endif /* TOOLS_NAMEDSTATS_H_ */
