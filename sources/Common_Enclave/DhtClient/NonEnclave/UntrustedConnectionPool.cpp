#ifdef ENCLAVE_PLATFORM_NON_ENCLAVE

#include "../UntrustedConnectionPool.h"

#include <DecentApi/Common/RuntimeException.h>
#include <DecentApi/Common/Net/ConnectionBase.h>

using namespace Decent::DhtClient;
using namespace Decent::Net;

extern "C" void* ocall_dht_client_cnt_pool_get_dht_any(void* cnt_pool_ptr, uint64_t* address);
extern "C" void* ocall_dht_client_cnt_pool_get_dht(void* cnt_pool_ptr, uint64_t address);

std::pair<std::unique_ptr<ConnectionBase>, uint64_t> UntrustedConnectionPool::GetAnyDhtNode(void * cntPoolPtr)
{
	if (!cntPoolPtr)
	{
		throw RuntimeException("Null pointer was given to UntrustedConnectionPool::GetAnyDhtNode.");
	}

	uint64_t addr = 0;

	return std::make_pair(
		std::unique_ptr<ConnectionBase>(static_cast<ConnectionBase*>(ocall_dht_client_cnt_pool_get_dht_any(cntPoolPtr, &addr))),
		addr);
}

std::unique_ptr<ConnectionBase> UntrustedConnectionPool::GetDhtNode(void * cntPoolPtr, uint64_t addr)
{
	if (!cntPoolPtr)
	{
		throw RuntimeException("Null pointer was given to UntrustedConnectionPool::GetDhtNode.");
	}

	return std::unique_ptr<ConnectionBase>(static_cast<ConnectionBase*>(ocall_dht_client_cnt_pool_get_dht(cntPoolPtr, addr)));
}

#endif //ENCLAVE_PLATFORM_SGX
