#include <cstdint>

#include <vector>
#include <algorithm>

#include <DecentApi/Common/Common.h>
#include <DecentApi/Common/GeneralKeyTypes.h>
#include <DecentApi/Common/MbedTls/Hasher.h>

#include <DecentApi/Common/Ra/Crypto.h>
#include <DecentApi/Common/Ra/KeyContainer.h>
#include <DecentApi/DecentAppEnclave/AppCertContainer.h>

#include "../Common_Enclave/DhtClient/DhtClient.h"
#include "../Common_Enclave/DhtClient/States.h"
#include "../Common_Enclave/DhtClient/StatesSingleton.h"
#include "../Common_Enclave/DhtClient/ConnectionManager.h"

using namespace Decent;
using namespace Decent::DhtClient;
using namespace Decent::Ra;
using namespace Decent::Dht;
using namespace Decent::MbedTlsObj;

namespace
{
	static DhtClient::States& gs_state = GetStatesSingleton();

}

extern "C" int ecall_dht_client_init()
{
	AppCertContainer& certContainer = gs_state.GetAppCertContainer();

	if (!certContainer.GetCert() || !*certContainer.GetCert())
	{
		std::shared_ptr<MbedTlsObj::X509Cert> cert = std::make_shared<ServerX509>(*gs_state.GetKeyContainer().GetSignKeyPair(), "N/A", "N/A", "N/A");
		certContainer.SetCert(cert);
	}

	return true;
}

extern "C" int ecall_dht_client_insert(void* cnt_pool_ptr, const void* key_buf, size_t key_size, const void* val_buf, size_t val_size)
{
	try
	{
		const uint8_t* keyBytePtr = static_cast<const uint8_t*>(key_buf);
		const uint8_t* ValBytePtr = static_cast<const uint8_t*>(val_buf);

		std::vector<uint8_t> key(keyBytePtr, keyBytePtr + key_size);
		std::vector<uint8_t> val(ValBytePtr, ValBytePtr + val_size);

		std::array<uint8_t, sk_hashSizeByte> id;

		Hasher::Calc<HashType::SHA256>(key, id);

		SetData(cnt_pool_ptr, id, val);

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to insert data. Error msg: %s", e.what());
		return false;
	}
}

extern "C" int ecall_dht_client_read(void* cnt_pool_ptr, const void* key_buf, size_t key_size, void** out_val_buf, size_t* out_val_size)
{
	try
	{
		const uint8_t* keyBytePtr = static_cast<const uint8_t*>(key_buf);

		std::vector<uint8_t> key(keyBytePtr, keyBytePtr + key_size);

		std::array<uint8_t, sk_hashSizeByte> id;

		Hasher::Calc<HashType::SHA256>(key, id);

		std::vector<uint8_t> val;
		GetData(cnt_pool_ptr, id, val);

		*out_val_buf = new uint8_t[val.size()];

		uint8_t* ValBytePtr = static_cast<uint8_t*>(*out_val_buf);
		std::copy(val.begin(), val.end(), ValBytePtr);
		*out_val_size = val.size();

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to read data. Error msg: %s", e.what());
		return false;
	}
}

extern "C" int ecall_dht_client_delete(void* cnt_pool_ptr, const void* key_buf, size_t key_size)
{
	try
	{
		const uint8_t* keyBytePtr = static_cast<const uint8_t*>(key_buf);

		std::vector<uint8_t> key(keyBytePtr, keyBytePtr + key_size);

		std::array<uint8_t, sk_hashSizeByte> id;

		Hasher::Calc<HashType::SHA256>(key, id);

		DelData(cnt_pool_ptr, id);

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to delete data. Error msg: %s", e.what());
		return false;
	}
}
