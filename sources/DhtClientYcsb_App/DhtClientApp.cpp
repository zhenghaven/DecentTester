#include "DhtClientApp.h"

#include <DecentApi/Common/SGX/RuntimeError.h>
#include <DecentApi/CommonApp/SGX/IasConnector.h>
#include <DecentApi/CommonApp/Base/EnclaveException.h>

#include "Enclave_u.h"

#define DECENT_DHT_NAIVE_RA_VER

#ifdef DECENT_DHT_NAIVE_RA_VER
#	include<cppcodec/hex_upper.hpp>
#endif // DECENT_DHT_NAIVE_RA_VER

using namespace Decent::Net;
using namespace Decent::DhtClient;

DhtClientApp::DhtClientApp(const std::string & enclavePath, const std::string & tokenPath, const std::string & wListKey, ConnectionBase & serverConn) :
	DecentApp(enclavePath, tokenPath, wListKey, serverConn)
{
}

DhtClientApp::DhtClientApp(const fs::path & enclavePath, const fs::path & tokenPath, const std::string & wListKey, ConnectionBase & serverConn) :
	DecentApp(enclavePath, tokenPath, wListKey, serverConn)
{
}

DhtClientApp::DhtClientApp(const std::string & enclavePath, const std::string & tokenPath, const size_t numTWorker, const size_t numUWorker,
	const size_t retryFallback, const size_t retrySleep, const std::string & wListKey, ConnectionBase & serverConn) :
	DecentApp(enclavePath, tokenPath, numTWorker, numUWorker, retryFallback, retrySleep, wListKey, serverConn)
{
}

DhtClientApp::DhtClientApp(const fs::path & enclavePath, const fs::path & tokenPath, const size_t numTWorker, const size_t numUWorker,
	const size_t retryFallback, const size_t retrySleep, const std::string & wListKey, ConnectionBase & serverConn) :
	DecentApp(enclavePath, tokenPath, numTWorker, numUWorker, retryFallback, retrySleep, wListKey, serverConn)
{
}

DhtClientApp::~DhtClientApp()
{
}

void DhtClientApp::Init(int64_t maxOpPerTicket)
{
	sgx_spid_t spid;

#ifdef DECENT_DHT_NAIVE_RA_VER

	m_ias = std::make_unique<Ias::Connector>("key");
	std::string spidStr = "AA";
	cppcodec::hex_upper::decode(spid.id, sizeof(spid.id), spidStr);

#endif // DECENT_DHT_NAIVE_RA_VER

	int enclaveRet = true;

#ifdef DECENT_DHT_NAIVE_RA_VER
	DECENT_CHECK_SGX_FUNC_CALL_ERROR(ecall_dht_client_init, GetEnclaveId(), &enclaveRet, m_ias.get(), &spid, GetEnclaveId(), maxOpPerTicket);
#else
	DECENT_CHECK_SGX_FUNC_CALL_ERROR(ecall_dht_client_init, GetEnclaveId(), &enclaveRet, nullptr, &spid, GetEnclaveId(), maxOpPerTicket);
#endif // DECENT_DHT_NAIVE_RA_VER

	if (!enclaveRet)
	{
		throw Decent::RuntimeException("Failed to initilize DhtClientApp");
	}
}

void DhtClientApp::Insert(std::shared_ptr<ConnectionPool> cntPool, const std::string & key, const std::string & val)
{
	int retValue = false;

	sgx_status_t enclaveRet = ecall_dht_client_insert(GetEnclaveId(), &retValue, cntPool.get(), key.data(), key.size(), val.data(), val.size());
	DECENT_CHECK_SGX_STATUS_ERROR(enclaveRet, ecall_dht_client_insert);

	if (!retValue)
	{
		throw Decent::RuntimeException("Failed to insert value!");
	}
}

void DhtClientApp::Update(std::shared_ptr<ConnectionPool> cntPool, const std::string & key, const std::string & val)
{
	int retValue = false;

	sgx_status_t enclaveRet = ecall_dht_client_update(GetEnclaveId(), &retValue, cntPool.get(), key.data(), key.size(), val.data(), val.size());
	DECENT_CHECK_SGX_STATUS_ERROR(enclaveRet, ecall_dht_client_update);

	if (!retValue)
	{
		throw Decent::RuntimeException("Failed to update value!");
	}
}

std::string DhtClientApp::Read(std::shared_ptr<ConnectionPool> cntPool, const std::string & key)
{
	int retValue = false;

	size_t valSize = 0;
	void* valBuf = nullptr;

	sgx_status_t enclaveRet = ecall_dht_client_read(GetEnclaveId(), &retValue, cntPool.get(), key.data(), key.size(), &valBuf, &valSize);
	DECENT_CHECK_SGX_STATUS_ERROR(enclaveRet, ecall_dht_client_delete);

	if (!retValue)
	{
		throw Decent::RuntimeException("Failed to read value!");
	}

	uint8_t* valBufByte = static_cast<uint8_t*>(valBuf);
	const char* valBufChar = static_cast<const char*>(valBuf);
	std::string val(valBufChar, valSize);

	delete [] valBufByte;

	return std::move(val);
}

void DhtClientApp::Delete(std::shared_ptr<ConnectionPool> cntPool, const std::string & key)
{
	int retValue = false;

	sgx_status_t enclaveRet = ecall_dht_client_delete(GetEnclaveId(), &retValue, cntPool.get(), key.data(), key.size());
	DECENT_CHECK_SGX_STATUS_ERROR(enclaveRet, ecall_dht_client_delete);

	if (!retValue)
	{
		throw Decent::RuntimeException("Failed to delete value!");
	}
}

bool DhtClientApp::ProcessSmartMessage(const std::string & category, ConnectionBase & connection, ConnectionBase*& freeHeldCnt)
{
	return Decent::RaSgx::DecentApp::ProcessSmartMessage(category, connection, freeHeldCnt);
}
