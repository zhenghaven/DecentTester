#include <cstdint>

#include <vector>
#include <algorithm>

#include <DecentApi/Common/Common.h>
#include <DecentApi/Common/GeneralKeyTypes.h>
#include <DecentApi/Common/MbedTls/Hasher.h>

#include "DhtClient/DhtClient.h"
#include "DhtClient/States.h"
#include "DhtClient/StatesSingleton.h"
#include "DhtClient/ConnectionManager.h"

#include "Enclave_t.h"

using namespace Decent;
using namespace Decent::DhtClient;
using namespace Decent::Ra;
using namespace Decent::Dht;
using namespace Decent::MbedTlsObj;

namespace
{
	static DhtClient::States& gs_state = GetStatesSingleton();

	static char gs_ack[] = "ACK";

}

extern "C" int ecall_dht_client_init(void* cnt_pool_ptr)
{
	gs_state.GetConnectionMgr().InitConnectionPoolPtr(cnt_pool_ptr);
	return true;
}

extern "C" int ecall_dht_client_insert(const void* key_buf, size_t key_size, const void* val_buf, size_t val_size)
{
	try
	{
		const uint8_t* keyBytePtr = static_cast<const uint8_t*>(key_buf);
		const uint8_t* ValBytePtr = static_cast<const uint8_t*>(val_buf);

		std::vector<uint8_t> key(keyBytePtr, keyBytePtr + key_size);
		std::vector<uint8_t> val(ValBytePtr, ValBytePtr + val_size);

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

extern "C" int ecall_dht_client_read(const void* key_buf, size_t key_size, void** out_val_buf, size_t* out_val_size)
{
	try
	{
		const uint8_t* keyBytePtr = static_cast<const uint8_t*>(key_buf);

		std::vector<uint8_t> key(keyBytePtr, keyBytePtr + key_size);

		std::array<uint8_t, sk_hashSizeByte> id;

		Hasher::Calc<HashType::SHA256>(key, id);

		std::vector<uint8_t> val;
		GetData(id, val);

		sgx_status_t ocallRet = ocall_dht_client_malloc(out_val_buf, val.size());
		
		if (ocallRet != SGX_SUCCESS)
		{
			return false;
		}

		uint8_t* ValBytePtr = static_cast<uint8_t*>(*out_val_buf);
		std::copy(val.begin(), val.end(), ValBytePtr);
		*out_val_size = val.size();

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to read data.\nError message: %s.", e.what());
		return false;
	}
}

extern "C" int ecall_dht_client_delete(const void* key_buf, size_t key_size)
{
	try
	{
		const uint8_t* keyBytePtr = static_cast<const uint8_t*>(key_buf);

		std::vector<uint8_t> key(keyBytePtr, keyBytePtr + key_size);

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
