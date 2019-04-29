//#if ENCLAVE_PLATFORM_SGX

#include "../DhtClientConnection.h"

#include <DecentApi/Common/make_unique.h>
#include <DecentApi/CommonEnclave/Net/EnclaveConnectionOwner.h>

#include <sgx_edger8r.h>

using namespace Decent;
using namespace Decent::Net;
using namespace Decent::Tools;

extern "C" sgx_status_t SGX_CDECL ocall_dht_client_cnt_mgr_get_dht_node(void** retval, uint64_t* out_addr);
extern "C" sgx_status_t SGX_CDECL ocall_dht_client_cnt_mgr_get_dht_store(void** retval, uint64_t address);

std::unique_ptr<ConnectionBase> DhtClient::GetConnection2DhtNode(uint64_t& outAddr)
{
	return make_unique<EnclaveConnectionOwner>(EnclaveConnectionOwner::CntBuilder(SGX_SUCCESS, ocall_dht_client_cnt_mgr_get_dht_node, &outAddr));
}

std::unique_ptr<ConnectionBase> DhtClient::GetConnection2DhtStore(const uint64_t addr)
{
	return make_unique<EnclaveConnectionOwner>(EnclaveConnectionOwner::CntBuilder(SGX_SUCCESS, ocall_dht_client_cnt_mgr_get_dht_store, addr));
}

//#endif //ENCLAVE_PLATFORM_SGX
