#ifndef _PORECLIENT_H_INCLUDED
#define _PORECLIENT_H_INCLUDED

#include "common.h"
#include <vector>
#include <string>

#define USING_PORE

/******************************************************************************/

BEGIN_PORE_NAMESPACE

const int pore_default_port = 10943;

void send(const std::vector<int> &vec, const std::string &bucket_name, 
          int port_number=pore_default_port);

void send(const std::vector<float> &vec, const std::string &bucket_name, 
          int port_number=pore_default_port);

void set_verbose(int level);

END_PORE_NAMESPACE

/******************************************************************************/

#endif
