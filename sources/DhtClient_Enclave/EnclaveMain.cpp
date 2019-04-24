#include <cstdint>

#include <vector>
#include <algorithm>

#include <DecentApi/Common/Common.h>
#include <DecentApi/Common/GeneralKeyTypes.h>
#include <DecentApi/Common/MbedTls/Hasher.h>
#include <DecentApi/DecentAppEnclave/AppStatesSingleton.h>

#include "Dht/DhtClient.h"

#include "Enclave_t.h"

using namespace Decent;
using namespace Decent::Ra;
using namespace Decent::Dht;
using namespace Decent::MbedTlsObj;

namespace
{
	static AppStates& gs_state = GetAppStateSingleton();

	static char gs_ack[] = "ACK";

}

extern "C" int ecall_dht_client_insert(const uint8_t* key_buf, size_t key_size, const uint8_t* val_buf, size_t val_size)
{
	try
	{
		std::vector<uint8_t> key(key_buf, key_buf + key_size);
		std::vector<uint8_t> val(val_buf, val_buf + val_size);

		std::array<uint8_t, sk_hashSizeByte> id;

		Hasher::Calc<HashType::SHA256>(key, id);

		SetData(id, val);

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to insert data.\nError message: %s.", e.what());
		return false;
	}
}

extern "C" int ecall_dht_client_read(const uint8_t* key_buf, size_t key_size, uint8_t** out_val_buf, size_t* out_val_size)
{
	try
	{
		std::vector<uint8_t> key(key_buf, key_buf + key_size);

		std::array<uint8_t, sk_hashSizeByte> id;

		Hasher::Calc<HashType::SHA256>(key, id);

		std::vector<uint8_t> val;
		GetData(id, val);

		sgx_status_t ocallRet = ocall_dht_client_malloc(out_val_buf, val.size());
		
		if (ocallRet != SGX_SUCCESS)
		{
			return false;
		}

		std::copy(val.begin(), val.end(), *out_val_buf);
		*out_val_size = val.size();

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to read data.\nError message: %s.", e.what());
		return false;
	}
}

extern "C" int ecall_dht_client_delete(const uint8_t* key_buf, size_t key_size)
{
	try
	{
		std::vector<uint8_t> key(key_buf, key_buf + key_size);

		std::array<uint8_t, sk_hashSizeByte> id;

		Hasher::Calc<HashType::SHA256>(key, id);

		DelData(id);

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to delete data.\nError message: %s.", e.what());
		return false;
	}
}
