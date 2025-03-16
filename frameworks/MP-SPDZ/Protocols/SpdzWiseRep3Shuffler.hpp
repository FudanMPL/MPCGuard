/*
 * SpdzWiseShuffler.cpp
 *
 */

#include "SpdzWiseRep3Shuffler.h"

template<class T>
SpdzWiseRep3Shuffler<T>::SpdzWiseRep3Shuffler(StackedVector<T>& a, size_t n,
        int unit_size, size_t output_base, size_t input_base,
        SubProcessor<T>& proc) :
        SpdzWiseRep3Shuffler(proc)
{
    store_type store;
    int handle = generate(n / unit_size, store);
    apply(a, n, unit_size, output_base, input_base, store.get(handle),
            false);
}

template<class T>
SpdzWiseRep3Shuffler<T>::SpdzWiseRep3Shuffler(SubProcessor<T>& proc) :
        proc(proc), internal_set(proc.P, {}), internal(internal_set.processor)
{
}

template<class T>
int SpdzWiseRep3Shuffler<T>::generate(int n_shuffle, store_type& store)
{
    return internal.generate(n_shuffle, store);
}

template<class T>
void SpdzWiseRep3Shuffler<T>::apply(StackedVector<T>& a, size_t n,
        int unit_size, size_t output_base, size_t input_base,
        shuffle_type& shuffle, bool reverse)
{
    stats[n / unit_size] += unit_size;

    StackedVector<typename T::part_type::Honest> to_shuffle;
    to_shuffle.reserve(2 * n);

    for (size_t i = 0; i < n; i++)
    {
        auto& x = a[input_base + i];
        to_shuffle.push_back(x.get_share());
        to_shuffle.push_back(x.get_mac());
    }

    internal.apply(to_shuffle, 2 * n, 2 * unit_size, 0, 0, shuffle, reverse);


    for (size_t i = 0; i < n; i++)
    {
        auto& x = a[output_base + i];
        x.set_share(to_shuffle[2 * i]);
        x.set_mac(to_shuffle[2 * i + 1]);
        proc.protocol.add_to_check(x);
    }

    proc.protocol.maybe_check();
}

template<class T>
void SpdzWiseRep3Shuffler<T>::inverse_permutation(StackedVector<T>&, size_t, size_t,
        size_t)
{
    throw not_implemented();
}
