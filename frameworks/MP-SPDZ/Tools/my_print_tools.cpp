#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <filesystem>
#include <stdexcept>
#include <boost/stacktrace.hpp>
#include <mutex>
#include <execinfo.h>
#include <unistd.h>


#include "my_print_tools.h"

std::mutex cout_mutex;


int vulnerability_message_idx = 0;
int count = 0;
bool is_record = true;
bool init=false;

void init_print() {
    init = true;
    // get is_record from environment variable
    const char* env_var = std::getenv("NO_RECORD");
    if (env_var != nullptr) {
        is_record = false;
        vulnerability_message_idx = get_vulnerability_message_idx();
    }
}




int get_vulnerability_message_idx() {
    // read secret from environment variable
    const char* env_var = std::getenv("VUL_INDEX");
    long long vulnerability_message_idx;
    if (env_var == nullptr) {
        throw std::runtime_error("VULNERABILITY_MESSAGE_IDX environment variable is not set");
    }else{
        vulnerability_message_idx = std::stol(env_var);
    }
    return vulnerability_message_idx; // Example secret
}



void my_print_or_match(long long data, const std::string& name = "") {
    std::lock_guard<std::mutex> guard(cout_mutex);

    (void) data; 
    (void) name;
    if (!init) {
        init_print();
    }
    if (is_record) {
        std::cout << std::endl;
        std::cout << "from " << name  << " " << data << std::endl;
    } else  {
   
        if (count < vulnerability_message_idx && count + 1 >= vulnerability_message_idx) {
            std::cout << std::endl;
            std::cout << "==============" << std::endl;
            std::cout << boost::stacktrace::stacktrace();
            std::cout << "==============" << std::endl;
        }
        count += 1;
     
    }
}


void print_stack_trace() {
  std::cout << std::endl;
  std::cout << boost::stacktrace::stacktrace();
}