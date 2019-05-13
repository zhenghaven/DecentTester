#include "ConnectionManager.h"

#include <DecentApi/Common/make_unique.h>
#include <DecentApi/Common/Net/TlsCommLayer.h>
#include <DecentApi/Common/Net/ConnectionBase.h>
#include <DecentApi/Common/Ra/TlsConfigWithName.h>

#include "UntrustedConnectionPool.h"
#include "AppNames.h"

using namespace Decent::Ra;
using namespace Decent::Net;
using namespace Decent::DhtClient;

namespace
{
	std::shared_ptr<TlsConfigWithName> GetTlsCfg2Dht(States & state)
	{
#ifdef ENCLAVE_PLATFORM_NON_ENCLAVE
		static std::shared_ptr<TlsConfigWithName> tlsCfg = std::make_shared<TlsConfigWithName>(state, TlsConfigWithName::Mode::ClientNoCert, AppNames::sk_decentDHT, nullptr);
#else
		static std::shared_ptr<TlsConfigWithName> tlsCfg = std::make_shared<TlsConfigWithName>(state, TlsConfigWithName::Mode::ClientHasCert, AppNames::sk_decentDHT, nullptr);
#endif // ENCLAVE_PLATFORM_NON_ENCLAVE
		return tlsCfg;
	}
}

ConnectionManager::ConnectionManager(size_t cacheSize) :
	m_sessionCache(cacheSize)
{
}

ConnectionManager::~ConnectionManager()
{
}

CntPair ConnectionManager::GetNew(void* cntPoolPtr, const uint64_t & addr, States & state)
{
	std::unique_ptr<ConnectionBase> connection = UntrustedConnectionPool::GetDhtNode(cntPoolPtr, addr);

	std::shared_ptr<MbedTlsObj::Session> session = m_sessionCache.Get(addr);

#ifdef ENCLAVE_PLATFORM_NON_ENCLAVE
	std::unique_ptr<TlsCommLayer> tls = Tools::make_unique<TlsCommLayer>(*connection, GetTlsCfg2Dht(state), false, session);
#else
	std::unique_ptr<TlsCommLayer> tls = Tools::make_unique<TlsCommLayer>(*connection, GetTlsCfg2Dht(state), true, session);
#endif // ENCLAVE_PLATFORM_NON_ENCLAVE

	if (!session)
	{
		m_sessionCache.Put(addr, tls->GetSessionCopy(), false);
	}

	std::unique_ptr<SecureCommLayer> comm = std::move(tls);
	return CntPair(connection, comm);
}

CntPair ConnectionManager::GetAny(void* cntPoolPtr, States & state)
{
	std::pair<std::unique_ptr<Net::ConnectionBase>, uint64_t> cntPair = UntrustedConnectionPool::GetAnyDhtNode(cntPoolPtr);

	std::shared_ptr<MbedTlsObj::Session> session = m_sessionCache.Get(cntPair.second);

#ifdef ENCLAVE_PLATFORM_NON_ENCLAVE
	std::unique_ptr<TlsCommLayer> tls = Tools::make_unique<TlsCommLayer>(*cntPair.first, GetTlsCfg2Dht(state), false, session);
#else
	std::unique_ptr<TlsCommLayer> tls = Tools::make_unique<TlsCommLayer>(*cntPair.first, GetTlsCfg2Dht(state), true, session);
#endif // ENCLAVE_PLATFORM_NON_ENCLAVE

	if (!session)
	{
		m_sessionCache.Put(cntPair.second, tls->GetSessionCopy(), false);
	}

	std::unique_ptr<SecureCommLayer> comm = std::move(tls);
	return CntPair(cntPair.first, comm);
}
