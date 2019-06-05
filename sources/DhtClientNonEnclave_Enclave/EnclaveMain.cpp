#include <cstdint>

#include <vector>
#include <algorithm>

#include <cppcodec/base64_default_rfc4648.hpp>

#include <DecentApi/Common/Common.h>
#include <DecentApi/Common/make_unique.h>
#include <DecentApi/Common/GeneralKeyTypes.h>
#include <DecentApi/Common/MbedTls/Hasher.h>

#include <DecentApi/Common/Ra/Crypto.h>
#include <DecentApi/Common/Ra/KeyContainer.h>
#include <DecentApi/Common/Ra/TlsConfigWithName.h>
#include <DecentApi/DecentAppEnclave/AppCertContainer.h>

#include "../Common_Enclave/DhtClient/DhtClient.h"
#include "../Common_Enclave/DhtClient/States.h"
#include "../Common_Enclave/DhtClient/AppNames.h"
#include "../Common_Enclave/DhtClient/ConnectionManager.h"
#include "../Common_Enclave/DhtClient/AccessCtrl/AbPolicy.h"
#include "../Common_Enclave/DhtClient/AccessCtrl/FullPolicy.h"
#include "../Common_Enclave/DhtClient/AccessCtrl/EntityList.h"

using namespace Decent;
using namespace Decent::DhtClient;
using namespace Decent::MbedTlsObj;

namespace
{
	static void GetUserId(States& states, general_256bit_hash& outId)
	{
		std::string pubKeyPem = states.GetKeyContainer().GetSignKeyPair()->ToPubPemString();

		Hasher::Calc<HashType::SHA256>(pubKeyPem, outId);
	}

#ifndef DHT_USER_TEST
	static Dht::AccessCtrl::FullPolicy GetTestAccPolicy(States& states)
	{
		Dht::AccessCtrl::EntityItem owner({ 0 });

		return Dht::AccessCtrl::FullPolicy(owner, Dht::AccessCtrl::EntityBasedControl::AllowAll(), Dht::AccessCtrl::AttributeBasedControl::AllowAll());
	}
#else
#	define DHT_USER_TEST_TEST_LABEL "TestList"

	static Dht::AccessCtrl::FullPolicy GetTestAccPolicy(States& states)
	{
		using namespace Dht::AccessCtrl;

		Dht::AccessCtrl::EntityItem owner({ 0 });

		std::string pubKeyPem = states.GetKeyContainer().GetSignKeyPair()->ToPubPemString();

		general_256bit_hash userId;
		Hasher::Calc<HashType::SHA256>(pubKeyPem, userId);

		general_256bit_hash labelId1;
		general_256bit_hash labelId2;
		general_256bit_hash labelId3;
		general_256bit_hash labelId4;
		general_256bit_hash labelId5;

		Hasher::Calc<HashType::SHA256>(std::string(DHT_USER_TEST_TEST_LABEL "1"), labelId1);
		Hasher::Calc<HashType::SHA256>(std::string(DHT_USER_TEST_TEST_LABEL "2"), labelId2);
		Hasher::Calc<HashType::SHA256>(std::string(DHT_USER_TEST_TEST_LABEL "3"), labelId3);
		Hasher::Calc<HashType::SHA256>(std::string(DHT_USER_TEST_TEST_LABEL "4"), labelId4);
		Hasher::Calc<HashType::SHA256>(std::string(DHT_USER_TEST_TEST_LABEL "5"), labelId5);

		return Dht::AccessCtrl::FullPolicy(owner, Dht::AccessCtrl::EntityBasedControl::AllowAll(), 
			Dht::AccessCtrl::AttributeBasedControl(
				Tools::make_unique<AbPolicyAttribute>(AbAttributeItem(userId, labelId1)) &
				Tools::make_unique<AbPolicyAttribute>(AbAttributeItem(userId, labelId2)) &
				Tools::make_unique<AbPolicyAttribute>(AbAttributeItem(userId, labelId3)) &
				Tools::make_unique<AbPolicyAttribute>(AbAttributeItem(userId, labelId4)) &
				Tools::make_unique<AbPolicyAttribute>(AbAttributeItem(userId, labelId5)),
				Tools::make_unique<AbPolicyAttribute>(AbAttributeItem(userId, labelId1)) &
				Tools::make_unique<AbPolicyAttribute>(AbAttributeItem(userId, labelId2)) &
				Tools::make_unique<AbPolicyAttribute>(AbAttributeItem(userId, labelId3)) &
				Tools::make_unique<AbPolicyAttribute>(AbAttributeItem(userId, labelId4)) &
				Tools::make_unique<AbPolicyAttribute>(AbAttributeItem(userId, labelId5)),
				AbPolicyNot::DenyAll()));
	}

	static Dht::AccessCtrl::EntityList GetTestEntityList(const std::string& pubKeyPem)
	{
		using namespace Dht::AccessCtrl;

		EntityList list;

		general_256bit_hash userId;
		Hasher::Calc<HashType::SHA256>(pubKeyPem, userId);

		list.Insert(EntityItem(userId));

		return list;
	}
#endif // !DHT_USER_TEST

	struct TestAccListInserter
	{
		TestAccListInserter(States& statesRef, void* cnt_pool_ptr)
		{
			std::string pubKeyPem = statesRef.GetKeyContainer().GetSignKeyPair()->ToPubPemString();

			UserInsertAttrList(cnt_pool_ptr, statesRef, DHT_USER_TEST_TEST_LABEL "1", GetTestEntityList(pubKeyPem));
			UserInsertAttrList(cnt_pool_ptr, statesRef, DHT_USER_TEST_TEST_LABEL "2", GetTestEntityList(pubKeyPem));
			UserInsertAttrList(cnt_pool_ptr, statesRef, DHT_USER_TEST_TEST_LABEL "3", GetTestEntityList(pubKeyPem));
			UserInsertAttrList(cnt_pool_ptr, statesRef, DHT_USER_TEST_TEST_LABEL "4", GetTestEntityList(pubKeyPem));
			UserInsertAttrList(cnt_pool_ptr, statesRef, DHT_USER_TEST_TEST_LABEL "5", GetTestEntityList(pubKeyPem));
		}
	};
}

extern "C" int ecall_dht_client_init(void* cnt_pool_ptr, void* states)
{
	States& statesRef = *static_cast<States*>(states);

	general_256bit_hash userId;
	GetUserId(statesRef, userId);
	std::string userIdStr = cppcodec::base64_rfc4648::encode(userId);

	PRINT_I("Initializing DHT client with ID: %s.", userIdStr.c_str());

	Ra::AppCertContainer& certContainer = statesRef.GetAppCertContainer();

	if (!certContainer.GetCert() || !*certContainer.GetCert())
	{
		std::shared_ptr<MbedTlsObj::X509Cert> cert = std::make_shared<Ra::ServerX509>(*statesRef.GetKeyContainer().GetSignKeyPair(), "N/A", "N/A", "N/A");
		certContainer.SetCert(cert);
	}

	//Set TLS configuration to DHT
#ifdef DHT_USER_TEST
	statesRef.SetTlsConfigToDht(
		std::make_shared<Ra::TlsConfigWithName>(statesRef, Ra::TlsConfigWithName::Mode::ClientHasCert, AppNames::sk_decentDHT, nullptr));
#else
	statesRef.SetTlsConfigToDht(
		std::make_shared<Ra::TlsConfigWithName>(statesRef, Ra::TlsConfigWithName::Mode::ClientNoCert, AppNames::sk_decentDHT, nullptr));
#endif

#ifdef DHT_USER_TEST
	try
	{
		static TestAccListInserter inst(statesRef, cnt_pool_ptr);
	}
	catch (const std::exception&)
	{
	}
#endif // DHT_USER_TEST

	statesRef.GetTestAccPolicy() = std::make_shared<Dht::AccessCtrl::FullPolicy>(GetTestAccPolicy(statesRef));

	return true;
}

extern "C" int ecall_dht_client_insert(void* cnt_pool_ptr, void* states, const void* key_buf, size_t key_size, const void* val_buf, size_t val_size)
{
	States& statesRef = *static_cast<States*>(states);
	try
	{
		const uint8_t* keyBytePtr = static_cast<const uint8_t*>(key_buf);
		const uint8_t* ValBytePtr = static_cast<const uint8_t*>(val_buf);

		std::vector<uint8_t> key(keyBytePtr, keyBytePtr + key_size);
		std::vector<uint8_t> val(ValBytePtr, ValBytePtr + val_size);

		std::array<uint8_t, sk_hashSizeByte> id;

		Hasher::Calc<HashType::SHA256>(key, id);

#ifndef DHT_USER_TEST
		AppInsertData(cnt_pool_ptr, statesRef, id, GetTestAccPolicyStatic(statesRef), val);
#else
		UserInsertData(cnt_pool_ptr, statesRef, id, *statesRef.GetTestAccPolicy(), val);
#endif // !DHT_USER_TEST

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to insert data. Error msg: %s", e.what());
		return false;
	}
}

extern "C" int ecall_dht_client_update(void* cnt_pool_ptr, void* states, const void* key_buf, size_t key_size, const void* val_buf, size_t val_size)
{
	States& statesRef = *static_cast<States*>(states);
	try
	{
		const uint8_t* keyBytePtr = static_cast<const uint8_t*>(key_buf);
		const uint8_t* ValBytePtr = static_cast<const uint8_t*>(val_buf);

		std::vector<uint8_t> key(keyBytePtr, keyBytePtr + key_size);
		std::vector<uint8_t> val(ValBytePtr, ValBytePtr + val_size);

		std::array<uint8_t, sk_hashSizeByte> id;

		Hasher::Calc<HashType::SHA256>(key, id);

#ifndef DHT_USER_TEST
		AppUpdateData(cnt_pool_ptr, statesRef, id, val);
#else
		UserUpdateData(cnt_pool_ptr, statesRef, id, val);
#endif // !DHT_USER_TEST

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to update data. Error msg: %s", e.what());
		return false;
	}
}

extern "C" int ecall_dht_client_read(void* cnt_pool_ptr, void* states, const void* key_buf, size_t key_size, void** out_val_buf, size_t* out_val_size)
{
	States& statesRef = *static_cast<States*>(states);
	try
	{
		const uint8_t* keyBytePtr = static_cast<const uint8_t*>(key_buf);

		std::vector<uint8_t> key(keyBytePtr, keyBytePtr + key_size);

		std::array<uint8_t, sk_hashSizeByte> id;

		Hasher::Calc<HashType::SHA256>(key, id);

#ifndef DHT_USER_TEST
		std::vector<uint8_t> val = AppReadData(cnt_pool_ptr, statesRef, id);
#else
		std::vector<uint8_t> val = UserReadData(cnt_pool_ptr, statesRef, id);
#endif // !DHT_USER_TEST

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

extern "C" int ecall_dht_client_delete(void* cnt_pool_ptr, void* states, const void* key_buf, size_t key_size)
{
	States& statesRef = *static_cast<States*>(states);
	try
	{
		const uint8_t* keyBytePtr = static_cast<const uint8_t*>(key_buf);

		std::vector<uint8_t> key(keyBytePtr, keyBytePtr + key_size);

		std::array<uint8_t, sk_hashSizeByte> id;

		Hasher::Calc<HashType::SHA256>(key, id);

#ifndef DHT_USER_TEST
		AppDeleteData(cnt_pool_ptr, statesRef, id);
#else
		UserDeleteData(cnt_pool_ptr, statesRef, id);
#endif // !DHT_USER_TEST

		return true;
	}
	catch (const std::exception& e)
	{
		PRINT_W("Failed to delete data. Error msg: %s", e.what());
		return false;
	}
}
