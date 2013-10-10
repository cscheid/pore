#include "client.h"
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <netdb.h> 
#include <iostream>
#include <errno.h>
#include <fstream>
#include <cstring>
#include <cstdlib>

using namespace std;

static void safe_read(int fd, void *dest, size_t size);
static void safe_write(int fd, const void *source, size_t size);
static int get_socket(int port_number);

template <typename T>
    static void send_vector(int fd, const vector<T> &vec)
{
    int size = vec.size() * sizeof(T);
    safe_write(fd, &size, sizeof(int));
    safe_write(fd, &vec[0], size);
}

static void send_string(int fd, const std::string &s)
{
    int bnsize = s.size();
    safe_write(fd, &bnsize, sizeof(int));
    safe_write(fd, &s[0], s.size());
}

BEGIN_PORE_NAMESPACE

void send(const vector<int> &vec, const string &bucket_name, int port_number)
{
    int fd = get_socket(port_number);
    if (fd == -1) return;
    send_string(fd, bucket_name);
    int dt = 0;
    safe_write(fd, &dt, sizeof(int));
    send_vector<int>(fd, vec);
    close(fd);
}

void send(const vector<float> &vec, const string &bucket_name, int port_number)
{
    int fd = get_socket(port_number);
    if (fd == -1) return;
    send_string(fd, bucket_name);
    int dt = 1;
    safe_write(fd, &dt, sizeof(int));
    send_vector<float>(fd, vec);
    close(fd);
}

static int _verbose = 0;
void set_verbose(int level)
{
    _verbose = level;
}

END_PORE_NAMESPACE

static void safe_read(int fd, void *dest, size_t size)
{
    char *d = (char*) dest;
    while (size) {
        ssize_t result = read(fd, d, size);
        if (result == -1) {
            if (errno != EINTR) {
                cerr << "ERROR in safe_read: " << strerror(errno) << endl;
                exit(1);
            }
            // hasn't read anything, got interrupted
            usleep(50000);
            continue;
        }
        d += result;
        size -= result;
        // don't hammer the processor
        if (result == 0) {
            usleep(50000);
        }
    }
}

void safe_write(int fd, const void *source, size_t size)
{
    const char *s = (const char*) source;
    while (size) {
        ssize_t result = write(fd, s, size);
        if (result == -1) {
            if (errno != EINTR) {
                cerr << "ERROR in safe_write: " << strerror(errno) << endl;
                exit(1);
            }
            // hasn't written anything, got interrupted
            usleep(50000);
            continue;
        }
        s += result;
        size -= result;
        // don't hammer the processor
        if (result == 0) {
            usleep(50000);
        }
    }
}

static int get_socket(int port_number)
{
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    struct hostent *server = gethostbyname("localhost");
    if (server == NULL) {
        cerr << "can't find localhost? you're in deep dodo" << endl;
        exit(1);
    }
    struct sockaddr_in serv_addr;

    memset((char *) &serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    memcpy((char *) &serv_addr.sin_addr.s_addr,
           (char *) server->h_addr,
           server->h_length);
    serv_addr.sin_port = htons(port_number);

    if (connect(sock, (const sockaddr*)&serv_addr,
                sizeof(serv_addr))) {
        if (pore::_verbose > 0) {
            cerr << "poreclient: cannot connect to pore server" << endl;
        }
        return -1;
    }
    return sock;
}
