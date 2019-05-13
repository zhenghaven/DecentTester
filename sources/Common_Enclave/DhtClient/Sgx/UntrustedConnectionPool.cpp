#ifdef ENCLAVE_PLATFORM_SGX

#include "../UntrustedConnectionPool.h"

#include <DecentApi/Common/make_unique.h>
#include <DecentApi/Common/RuntimeException.h>
#include <DecentApi/CommonEnclave/Net/EnclaveConnectionOwner.h>

#include <sgx_edger8r.h>

using namespace Decent::DhtClient;
using namespace Decent::Net;

extern "C" sgx_status_t SGX_CDECL ocall_dht_client_cnt_pool_get_dht_any(void** retval, void* cnt_pool_ptr, uint64_t* address);
extern "C" sgx_status_t SGX_CDECL ocall_dht_client_cnt_pool_get_dht(void** retval, void* cnt_pool_ptr, uint64_t address);

std::pair<std::unique_ptr<ConnectionBase>, uint64_t> UntrustedConnectionPool::GetAnyDhtNode(void * cntPoolPtr)
{
	if (!cntPoolPtr)
	{
		throw RuntimeException("Null pointer was given to UntrustedConnectionPool::GetAnyDhtNode.");
	}

	uint64_t addr = 0;

	return std::make_pair(
		Tools::make_unique<EnclaveConnectionOwner>(EnclaveConnectionOwner::CntBuilder(SGX_SUCCESS, ocall_dht_client_cnt_pool_get_dht_any, cntPoolPtr, &addr)),
		addr);
}

std::unique_ptr<ConnectionBase> UntrustedConnectionPool::GetDhtNode(void * cntPoolPtr, uint64_t addr)
{
	if (!cntPoolPtr)
	{
		throw RuntimeException("Null pointer was given to UntrustedConnectionPool::GetDhtNode.");
	}

	return Tools::make_unique<EnclaveConnectionOwner>(EnclaveConnectionOwner::CntBuilder(SGX_SUCCESS, ocall_dht_client_cnt_pool_get_dht, cntPoolPtr, addr));
}

#endif //ENCLAVE_PLATFORM_SGX
