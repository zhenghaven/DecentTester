#include <cstdint>

#include <vector>
#include <algorithm>

#include <DecentApi/Common/Common.h>
#include <DecentApi/Common/GeneralKeyTypes.h>
#include <DecentApi/Common/make_unique.h>
#include <DecentApi/Common/Ra/TlsConfigWithName.h>
#include <DecentApi/Common/MbedTls/Hasher.h>

#include <DecentApi/CommonEnclave/Tools/Crypto.h>

#include "../Common_Enclave/DhtClient/DhtClient.h"
#include "../Common_Enclave/DhtClient/States.h"
#include "../Common_Enclave/DhtClient/AppNames.h"
#include "../Common_Enclave/DhtClient/StatesSingleton.h"
#include "../Common_Enclave/DhtClient/ConnectionManager.h"

#include "../Common_Enclave/DhtClient/AccessCtrl/AbPolicy.h"
#include "../Common_Enclave/DhtClient/AccessCtrl/FullPolicy.h"
#include "../Common_Enclave/DhtClient/AccessCtrl/EntityList.h"

#include "Enclave_t.h"

using namespace Decent;
using namespace Decent::DhtClient;
using namespace Decent::Ra;
using namespace Decent::MbedTlsObj;

//#define ENCLAVE_ACCESS_CONTROL_ON

namespace
{
	static DhtClient::States& gs_state = GetStatesSingleton();

	static Dht::AccessCtrl::FullPolicy GetTestAccPolicy()
	{
		using namespace Dht::AccessCtrl;

		const std::vector<uint8_t>& selfHashBin = Tools::GetSelfHash();
		general_256bit_hash selfHash;
		if (selfHashBin.size() != sizeof(general_256bit_hash))
		{
			throw Decent::RuntimeException("Feature not supported.");
		}
		std::copy(selfHashBin.begin(), selfHashBin.end(), std::begin(selfHash));

		EntityItem owner({ selfHash });

#ifdef ENCLAVE_ACCESS_CONTROL_ON
		std::unique_ptr<EntityList> enclaveList1 = Tools::make_unique<EntityList>();
		enclaveList1->Insert(owner);
		enclaveList1->Insert(EntityItem({ 1 }));
		enclaveList1->Insert(EntityItem({ 2 }));
		enclaveList1->Insert(EntityItem({ 3 }));
		enclaveList1->Insert(EntityItem({ 4 }));
		enclaveList1->Insert(EntityItem({ 5 }));
		enclaveList1->Insert(EntityItem({ 6 }));
		enclaveList1->Insert(EntityItem({ 7 }));
		enclaveList1->Insert(EntityItem({ 8 }));
		enclaveList1->Insert(EntityItem({ 9 }));
		std::unique_ptr<EntityList> enclaveList2 = Tools::make_unique<EntityList>();
		enclaveList2->Insert(owner);
		enclaveList2->Insert(EntityItem({ 1 }));
		enclaveList2->Insert(EntityItem({ 2 }));
		enclaveList2->Insert(EntityItem({ 3 }));
		enclaveList2->Insert(EntityItem({ 4 }));
		enclaveList2->Insert(EntityItem({ 5 }));
		enclaveList2->Insert(EntityItem({ 6 }));
		enclaveList2->Insert(EntityItem({ 7 }));
		enclaveList2->Insert(EntityItem({ 8 }));
		enclaveList2->Insert(EntityItem({ 9 }));

		EntityBasedControl enclaveControl(std::move(enclaveList1), std::move(enclaveList2), nullptr);
#else
		EntityBasedControl enclaveControl = EntityBasedControl::AllowAll();
#endif

		return FullPolicy(owner, std::move(enclaveControl), AttributeBasedControl::AllowAll());
	}

	static const Dht::AccessCtrl::FullPolicy& GetTestAccPolicyStatic()
	{
		static const Dht::AccessCtrl::FullPolicy inst = GetTestAccPolicy();

		return inst;
	}
}

extern "C" int ecall_dht_client_init()
{
	try
	{
		gs_state.SetTlsConfigToDht(
			std::make_shared<TlsConfigWithName>(gs_state, TlsConfigWithName::Mode::ClientHasCert, AppNames::sk_decentDHT, nullptr));
	}
	catch (const std::exception&)
	{
		return false;
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

		AppInsertData(cnt_pool_ptr, gs_state, id, GetTestAccPolicyStatic(), val);

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to insert data. Error message: %s", e.what());
		return false;
	}
}

extern "C" int ecall_dht_client_update(void* cnt_pool_ptr, const void* key_buf, size_t key_size, const void* val_buf, size_t val_size)
{
	try
	{
		const uint8_t* keyBytePtr = static_cast<const uint8_t*>(key_buf);
		const uint8_t* ValBytePtr = static_cast<const uint8_t*>(val_buf);

		std::vector<uint8_t> key(keyBytePtr, keyBytePtr + key_size);
		std::vector<uint8_t> val(ValBytePtr, ValBytePtr + val_size);

		std::array<uint8_t, sk_hashSizeByte> id;

		Hasher::Calc<HashType::SHA256>(key, id);

		AppUpdateData(cnt_pool_ptr, gs_state, id, val);

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to insert data. Error message: %s", e.what());
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

		std::vector<uint8_t> val = AppReadData(cnt_pool_ptr, gs_state, id);

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
		PRINT_W("Failed to read data. Error message: %s", e.what());
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

		AppDeleteData(cnt_pool_ptr, gs_state, id);

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to delete data. Error message: %s", e.what());
		return false;
	}
}
