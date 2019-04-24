#include "ConnectionManager.h"

#include<memory>

#include <DecentApi/CommonApp/Net/Connection.h>

using namespace Decent::DhtClient;

extern "C" void* ocall_dht_client_cnt_mgr_get_dht_node()
{
	return ConnectionManager::GetConnection2DecentDhtNode().release();
}

extern "C" void* ocall_dht_client_cnt_mgr_get_dht_store(uint64_t address)
{
	return ConnectionManager::GetConnection2DecentDhtStore(address).release();
}

extern "C" void* ocall_dht_client_malloc(size_t size)
{
	return (new uint8_t[size]);
}
