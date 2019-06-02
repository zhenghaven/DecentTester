#include "DhtClientApp.h"

#include <DecentApi/Common/Common.h>
#include <DecentApi/Common/Ra/KeyContainer.h>
#include <DecentApi/Common/Ra/WhiteList/LoadedList.h>
#include <DecentApi/Common/Ra/WhiteList/DecentServer.h>

#include <DecentApi/CommonApp/Base/EnclaveException.h>

#include <DecentApi/DecentAppEnclave/AppCertContainer.h>

#include "../Common_Enclave/DhtClient/States.h"
#include "../Common_Enclave/DhtClient/ConnectionManager.h"

extern "C" int ecall_dht_client_init(void* cnt_pool_ptr, void* states);
extern "C" int ecall_dht_client_insert(void* cnt_pool_ptr, void* states, const void* key_buf, size_t key_size, const void* val_buf, size_t val_size);
extern "C" int ecall_dht_client_update(void* cnt_pool_ptr, void* states, const void* key_buf, size_t key_size, const void* val_buf, size_t val_size);
extern "C" int ecall_dht_client_read(void* cnt_pool_ptr, void* states, const void* key_buf, size_t key_size, void** out_val_buf, size_t* out_val_size);
extern "C" int ecall_dht_client_delete(void* cnt_pool_ptr, void* states, const void* key_buf, size_t key_size);

using namespace Decent::DhtClient;

namespace
{
	static const Decent::Ra::WhiteList::LoadedList& GetLoadedWhiteListImpl(Decent::Ra::WhiteList::LoadedList* instPtr)
	{
		static const Decent::Ra::WhiteList::LoadedList inst(instPtr);
		return inst;
	}
}

DhtClientApp::DhtClientApp() :
	m_certContainer(std::make_unique<Ra::AppCertContainer>()),
	m_keyContainer(std::make_unique<Ra::KeyContainer>()),
	m_serverWl(std::make_unique<Ra::WhiteList::DecentServer>()),
	m_connectionMgr(std::make_unique<ConnectionManager>(50)),
	m_states(std::make_unique<DhtClient::States>(*m_certContainer, *m_keyContainer, *m_serverWl, &GetLoadedWhiteListImpl, *m_connectionMgr))
{
}

DhtClientApp::~DhtClientApp()
{
}

void DhtClientApp::Init(std::shared_ptr<ConnectionPool> cntPool, const Decent::Ra::WhiteList::StaticList& loadedWhiteList)
{
	Decent::Ra::WhiteList::LoadedList tmpLoadedWhiteList(loadedWhiteList.GetMap());
	GetLoadedWhiteListImpl(&tmpLoadedWhiteList);

	int enclaveRet = ecall_dht_client_init(cntPool.get(), m_states.get());

	if (!enclaveRet)
	{
		throw Decent::RuntimeException("Failed to initilize DhtClientApp");
	}
}

void DhtClientApp::Insert(std::shared_ptr<ConnectionPool> cntPool, const std::string & key, const std::string & val)
{
	int retValue = ecall_dht_client_insert(cntPool.get(), m_states.get(), key.data(), key.size(), val.data(), val.size());

	if (!retValue)
	{
		throw Decent::RuntimeException("Failed to insert value!");
	}
}

void DhtClientApp::Update(std::shared_ptr<ConnectionPool> cntPool, const std::string & key, const std::string & val)
{
	int retValue = ecall_dht_client_update(cntPool.get(), m_states.get(), key.data(), key.size(), val.data(), val.size());

	if (!retValue)
	{
		throw Decent::RuntimeException("Failed to insert value!");
	}
}

std::string DhtClientApp::Read(std::shared_ptr<ConnectionPool> cntPool, const std::string & key)
{
	size_t valSize = 0;
	void* valBuf = nullptr;

	int retValue = ecall_dht_client_read(cntPool.get(), m_states.get(), key.data(), key.size(), &valBuf, &valSize);

	if (!retValue)
	{
		throw Decent::RuntimeException("Failed to delete value!");
	}

	uint8_t* valBufByte = static_cast<uint8_t*>(valBuf);
	const char* valBufChar = static_cast<const char*>(valBuf);
	std::string val(valBufChar, valSize);

	delete [] valBufByte;

	return val;
}

void DhtClientApp::Delete(std::shared_ptr<ConnectionPool> cntPool, const std::string & key)
{
	int retValue = ecall_dht_client_delete(cntPool.get(), m_states.get(), key.data(), key.size());

	if (!retValue)
	{
		throw Decent::RuntimeException("Failed to delete value!");
	}
}
