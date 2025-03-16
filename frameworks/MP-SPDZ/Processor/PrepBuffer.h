/*
 * PrepBuffer.h
 *
 */

#ifndef PROCESSOR_PREPBUFFER_H_
#define PROCESSOR_PREPBUFFER_H_

#include "Tools/Buffer.h"

template<class T, class U = T, class V = T>
class PrepBuffer : public BufferOwner<T, U, V>
{
    int num_players;
    string fake_opts;

public:
    PrepBuffer() :
            num_players(0)
    {
    }

    void setup(int num_players, const string& filename, int tuple_length,
            const string& type_string = "", const char* data_type = "")
    {
        this->num_players = num_players;
        fake_opts = V::template proto_fake_opts<typename V::open_type>();
        BufferOwner<T, U, V>::setup(filename, tuple_length, type_string, data_type);
    }

    void input(U& a)
    {
        try
        {
            BufferOwner<T, U, V>::input(a);
        }
        catch (exception& e)
        {
            throw prep_setup_error(e.what(), num_players, fake_opts);
        }
    }
};

#endif /* PROCESSOR_PREPBUFFER_H_ */
