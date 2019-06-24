#include "ConnectionManager.h"

#include <DecentApi/Common/make_unique.h>
#include <DecentApi/Common/Net/TlsCommLayer.h>
#include <DecentApi/Common/Net/ConnectionBase.h>
#include <DecentApi/Common/Ra/TlsConfigWithName.h>

#include "UntrustedConnectionPool.h"
#include "AppNames.h"
#include "States.h"

using namespace Decent;
using namespace Decent::Ra;
using namespace Decent::Net;
using namespace Decent::DhtClient;

ConnectionManager::ConnectionManager(size_t cacheSize) :
	m_sessionCache(cacheSize)
{
}

ConnectionManager::~ConnectionManager()
{
}

CntPair ConnectionManager::GetNew(void* cntPoolPtr, const uint64_t & addr, DhtClient::States & state)
{
	std::unique_ptr<ConnectionBase> connection = UntrustedConnectionPool::GetDhtNode(cntPoolPtr, addr);

	std::shared_ptr<MbedTlsObj::Session> session = m_sessionCache.Get(addr);

#ifdef ENCLAVE_PLATFORM_NON_ENCLAVE
#	ifndef DHT_USER_TEST
	std::unique_ptr<TlsCommLayer> secComm = Tools::make_unique<TlsCommLayer>(*connection, state.GetTlsConfigToDht(), false, session);
#	else
	std::unique_ptr<TlsCommLayer> secComm = Tools::make_unique<TlsCommLayer>(*connection, state.GetTlsConfigToDht(), true, session);
#	endif // !DHT_USER_TEST
#else
	std::unique_ptr<TlsCommLayer> secComm = Tools::make_unique<TlsCommLayer>(*connection, state.GetTlsConfigToDht(), true, session);
#endif // ENCLAVE_PLATFORM_NON_ENCLAVE

	if (!session)
	{
		m_sessionCache.Put(addr, secComm->GetSessionCopy(), false);
	}

	return CntPair(std::move(connection), std::move(secComm));
}

CntPair ConnectionManager::GetAny(void* cntPoolPtr, DhtClient::States & state)
{
	std::pair<std::unique_ptr<Net::ConnectionBase>, uint64_t> cntPair = UntrustedConnectionPool::GetAnyDhtNode(cntPoolPtr);

	std::shared_ptr<MbedTlsObj::Session> session = m_sessionCache.Get(cntPair.second);

#ifdef ENCLAVE_PLATFORM_NON_ENCLAVE
#	ifndef DHT_USER_TEST
	std::unique_ptr<TlsCommLayer> secComm = Tools::make_unique<TlsCommLayer>(*cntPair.first, state.GetTlsConfigToDht(), false, session);
#	else
	std::unique_ptr<TlsCommLayer> secComm = Tools::make_unique<TlsCommLayer>(*cntPair.first, state.GetTlsConfigToDht(), true, session);
#	endif // !DHT_USER_TEST
#else
	std::unique_ptr<TlsCommLayer> secComm = Tools::make_unique<TlsCommLayer>(*cntPair.first, state.GetTlsConfigToDht(), true, session);
#endif // ENCLAVE_PLATFORM_NON_ENCLAVE

	if (!session)
	{
		m_sessionCache.Put(cntPair.second, secComm->GetSessionCopy(), false);
	}

	return CntPair(std::move(cntPair.first), std::move(secComm));
}
