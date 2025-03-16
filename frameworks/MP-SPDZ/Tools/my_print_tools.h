#include <string>
#include <mutex>


extern std::mutex cout_mutex;

void init_print();
int get_file_id();
int get_secret();
int get_pid();
void my_print_or_match(long long data, const std::string& name);
void get_folder_path(std::string &folder_path);
int get_vulnerability_message_idx();
void print_stack_trace();