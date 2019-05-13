#include "DhtClientApp.h"

#include <DecentApi/CommonApp/Base/EnclaveException.h>

extern "C" int ecall_dht_client_init();
extern "C" int ecall_dht_client_insert(void* cnt_pool_ptr, const void* key_buf, size_t key_size, const void* val_buf, size_t val_size);
extern "C" int ecall_dht_client_read(void* cnt_pool_ptr, const void* key_buf, size_t key_size, void** out_val_buf, size_t* out_val_size);
extern "C" int ecall_dht_client_delete(void* cnt_pool_ptr, const void* key_buf, size_t key_size);

using namespace Decent::DhtClient;

DhtClientApp::~DhtClientApp()
{
}

void DhtClientApp::Init()
{
	int enclaveRet = ecall_dht_client_init();

	if (!enclaveRet)
	{
		throw Decent::RuntimeException("Failed to initilize DhtClientApp");
	}
}

void DhtClientApp::Insert(std::shared_ptr<ConnectionPool> cntPool, const std::string & key, const std::string & val)
{
	int retValue = ecall_dht_client_insert(cntPool.get(), key.data(), key.size(), val.data(), val.size());

	if (!retValue)
	{
		throw Decent::RuntimeException("Failed to insert value!");
	}
}

std::string DhtClientApp::Read(std::shared_ptr<ConnectionPool> cntPool, const std::string & key)
{
	size_t valSize = 0;
	void* valBuf = nullptr;

	int retValue = ecall_dht_client_read(cntPool.get(), key.data(), key.size(), &valBuf, &valSize);

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
	int retValue = ecall_dht_client_delete(cntPool.get(), key.data(), key.size());

	if (!retValue)
	{
		throw Decent::RuntimeException("Failed to delete value!");
	}
}
