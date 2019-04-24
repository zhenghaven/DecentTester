#include "../Dht/DhtConnection.h"

#include <DecentApi/Common/make_unique.h>
#include <DecentApi/CommonEnclave/SGX/OcallConnector.h>

#include <sgx_edger8r.h>

using namespace Decent;
using namespace Decent::Dht;
using namespace Decent::Net;
using namespace Decent::Tools;

extern "C" sgx_status_t SGX_CDECL ocall_dht_client_cnt_mgr_get_dht_node(void** retval);
extern "C" sgx_status_t SGX_CDECL ocall_dht_client_cnt_mgr_get_dht_store(void** retval, uint64_t address);

std::unique_ptr<EnclaveNetConnector> Dht::GetConnection2DhtNode()
{
	return make_unique<OcallConnector>(ocall_dht_client_cnt_mgr_get_dht_node);
}

std::unique_ptr<EnclaveNetConnector> Dht::GetConnection2DhtStore(const uint64_t addr)
{
	return make_unique<OcallConnector>(ocall_dht_client_cnt_mgr_get_dht_store, addr);
}
