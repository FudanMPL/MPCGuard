#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/shape_inference.h"
#include "tensorflow/core/framework/op_kernel.h"
#include "tensorflow/core/lib/random/random_distributions.h"
#include "sodium.h"

#define CHACHABLOCKSIZE 64
#define NUMBER_OF_SEEDS randombytes_SEEDBYTES / sizeof(int32)

using namespace tensorflow;

// this function allows you to skip ahead in the chacha stream so you don't
// have to allocate more memory than you need to, used in rejection sampling and
// will be handy for parallelizing this operation
void randombytes_buf_deterministic_ic(void * const buf, const size_t size, uint32 count,
                              const unsigned char seed[randombytes_SEEDBYTES])
{
    static const unsigned char nonce[crypto_stream_chacha20_ietf_NONCEBYTES] = {
        'L', 'i', 'b', 's', 'o', 'd', 'i', 'u', 'm', 'D', 'R', 'G'
    };

    unsigned char * u_buf = (unsigned char *)buf;

    memset(u_buf, 0, size);

    crypto_stream_chacha20_ietf_xor_ic(u_buf, u_buf, (unsigned long long) size,
                                       nonce, count, seed);
}

void generate_seed(void * buf) {
    randombytes_buf(buf, randombytes_SEEDBYTES);
}

template <typename T>
class Generator {
public:
  Generator(T* output, size_t count) {
    count_ = count;
    bytes_count_ = count_ * sizeof(T);
    buf_ = output;
  }

  void GenerateData(T minval, T maxval) {
    unsigned char seeds[randombytes_SEEDBYTES];
    generate_seed(seeds);

    randombytes_buf_deterministic(buf_, bytes_count_, seeds);

    Uniform(minval, maxval - 1);
  }

protected:
  T *buf_ = nullptr;
  size_t count_ = 0;
  size_t bytes_count_ = 0;

  // The following random uniform distribution is based on a an implementation from
  // https://github.com/rust-random/rand/blob/3eadab75c8a5871d1be729091795a6c4e1dc19bb/src/distributions/uniform.rs#L310
  // There is quite a bit of documentation at that link which is explains the implementation.
  // See below for other inline docs.

  // inclusive uniform!
  void Uniform(T low, T high) {
    typedef typename std::make_unsigned<T>::type uT;

    // add one for inclusive range, subtract 1 from high input to get exclusive range
    auto range = static_cast<uT>(high) - static_cast<uT>(low) + 1;
    // uT range = static_cast<uT>(high) - static_cast<uT>(low) + 1;
    auto unsigned_max = std::numeric_limits<uT>::max();

    // find the number of integers to reject
    auto ints_to_reject = (unsigned_max - range + 1) % range;

    // find the allowed zone, multiple of the range
    auto zone = unsigned_max - ints_to_reject;

    // loop through all of the values to check for numbers to reject
    for (size_t i = 0; i < count_; ++i) {
      // we need the unsigned version here
      auto unsign = static_cast<uT>(buf_[i]);

      // if lo is out of the zone reject and get another number
      while(unsign > zone) {
        // rejection sampling, get the next valid number in the stream
        buf_[i] = this->GetNextValidData();
        unsign = static_cast<uT>(buf_[i]);
      }

      // shift hi by the lower bound to get the value in between lower/upper bound
      buf_[i] = random::SignedAdd(low, unsign % range);
    }
  }

  virtual T GetNextValidData() {
    T data;

    randombytes_buf(&data, sizeof(T));

    return data;
  }
};


template <typename T>
class SeededGenerator : public Generator<T> {
public:
  const unsigned char * seeds = nullptr;

  SeededGenerator(T* output, size_t count, const unsigned char * seeds)
                            : Generator<T>(output, count), seeds(seeds) {
    elements_per_block_ = CHACHABLOCKSIZE / sizeof(T);
    block_counter_ = this->bytes_count_ / CHACHABLOCKSIZE + 1;

    // prepare the extra block if any values get rejected in the rejection sampling
    randombytes_buf_deterministic_ic(extra_block_, CHACHABLOCKSIZE, block_counter_, seeds);
  }

  void GenerateData(T minval, T maxval) {
    randombytes_buf_deterministic(this->buf_, this->bytes_count_, seeds);

    this->Uniform(minval, maxval - 1);
  }

  T GetNextValidData() override {
    // if the extra block has been used up get the next available block
    if(inner_block_index_ + 1 == elements_per_block_) {
      inner_block_index_ = 0;
      block_counter_++;

      randombytes_buf_deterministic_ic(extra_block_, CHACHABLOCKSIZE, block_counter_, seeds);
    }

    T ret = extra_block_[inner_block_index_];
    inner_block_index_++;

    return ret;
  }

private:
  T extra_block_[CHACHABLOCKSIZE];
  uint32 block_counter_ = 0;
  uint32 elements_per_block_ = 0;
  uint32 inner_block_index_ = 0;
};
