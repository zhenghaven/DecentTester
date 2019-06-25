#include "ConnectionManager.h"

#include <DecentApi/Common/make_unique.h>
#include <DecentApi/Common/Net/TlsCommLayer.h>
#include <DecentApi/Common/Net/ConnectionBase.h>
#include <DecentApi/Common/Ra/TlsConfigWithName.h>

#include "UntrustedConnectionPool.h"
#include "AppNames.h"
#include "States.h"

#ifdef DECENT_DHT_NAIVE_RA_VER
#include <DecentApi/Common/Ra/KeyContainer.h>
#include <DecentApi/Common/SGX/RaProcessorSp.h>
#include <DecentApi/CommonEnclave/SGX/RaProcessorClient.h>
#include <DecentApi/CommonEnclave/SGX/RaMutualCommLayer.h>
#endif // DECENT_DHT_NAIVE_RA_VER

using namespace Decent;
using namespace Decent::Ra;
using namespace Decent::Net;
using namespace Decent::DhtClient;

namespace
{
#ifdef DECENT_DHT_NAIVE_RA_VER
	static Sgx::RaProcessorSp::SgxQuoteVerifier quoteVrfy = [](const sgx_quote_t&)
	{
		return true;
	};
#endif // DECENT_DHT_NAIVE_RA_VER
}

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

	auto session = m_sessionCache.Get(addr);

#ifdef DECENT_DHT_NAIVE_RA_VER

	std::unique_ptr<Sgx::RaMutualCommLayer> secComm =
		Tools::make_unique<Sgx::RaMutualCommLayer>(*connection,
			Tools::make_unique<Sgx::RaProcessorClient>(state.GetEnclaveId(),
				Sgx::RaProcessorClient::sk_acceptAnyPubKey, Sgx::RaProcessorClient::sk_acceptAnyRaConfig),
			Tools::make_unique<Sgx::RaProcessorSp>(state.GetIasConnector(),
				state.GetKeyContainer().GetSignKeyPair(), state.GetSpid(),
				Sgx::RaProcessorSp::sk_defaultRpDataVrfy, quoteVrfy),
			session);

	std::shared_ptr<const Sgx::RaClientSession> neSession = secComm->GetClientSession();
	if (session != neSession)
	{
		m_sessionCache.Put(addr, neSession, false);
	}

#else

#	ifdef ENCLAVE_PLATFORM_NON_ENCLAVE

#		ifndef DHT_USER_TEST
	std::unique_ptr<TlsCommLayer> secComm = Tools::make_unique<TlsCommLayer>(*connection, state.GetTlsConfigToDht(), false, session);
#		else
	std::unique_ptr<TlsCommLayer> secComm = Tools::make_unique<TlsCommLayer>(*connection, state.GetTlsConfigToDht(), true, session);
#		endif // !DHT_USER_TEST

#	else

	std::unique_ptr<TlsCommLayer> secComm = Tools::make_unique<TlsCommLayer>(*connection, state.GetTlsConfigToDht(), true, session);

#	endif // ENCLAVE_PLATFORM_NON_ENCLAVE

	if (!session)
	{
		m_sessionCache.Put(addr, secComm->GetSessionCopy(), false);
	}

#endif //DECENT_DHT_NAIVE_RA_VER

	return CntPair(std::move(connection), std::move(secComm));
}

CntPair ConnectionManager::GetAny(void* cntPoolPtr, DhtClient::States & state)
{
	std::pair<std::unique_ptr<Net::ConnectionBase>, uint64_t> cntPair = UntrustedConnectionPool::GetAnyDhtNode(cntPoolPtr);

	auto session = m_sessionCache.Get(cntPair.second);

#ifdef DECENT_DHT_NAIVE_RA_VER

	std::unique_ptr<Sgx::RaMutualCommLayer> secComm =
		Tools::make_unique<Sgx::RaMutualCommLayer>(*cntPair.first,
			Tools::make_unique<Sgx::RaProcessorClient>(state.GetEnclaveId(),
				Sgx::RaProcessorClient::sk_acceptAnyPubKey, Sgx::RaProcessorClient::sk_acceptAnyRaConfig),
			Tools::make_unique<Sgx::RaProcessorSp>(state.GetIasConnector(),
				state.GetKeyContainer().GetSignKeyPair(), state.GetSpid(),
				Sgx::RaProcessorSp::sk_defaultRpDataVrfy, quoteVrfy),
			session);

	std::shared_ptr<const Sgx::RaClientSession> neSession = secComm->GetClientSession();
	if (session != neSession)
	{
		m_sessionCache.Put(cntPair.second, neSession, false);
	}

#else

#	ifdef ENCLAVE_PLATFORM_NON_ENCLAVE

#		ifndef DHT_USER_TEST
	std::unique_ptr<TlsCommLayer> secComm = Tools::make_unique<TlsCommLayer>(*cntPair.first, state.GetTlsConfigToDht(), false, session);
#		else
	std::unique_ptr<TlsCommLayer> secComm = Tools::make_unique<TlsCommLayer>(*cntPair.first, state.GetTlsConfigToDht(), true, session);
#		endif // !DHT_USER_TEST

#	else
	
	std::unique_ptr<TlsCommLayer> secComm = Tools::make_unique<TlsCommLayer>(*cntPair.first, state.GetTlsConfigToDht(), true, session);

#	endif // ENCLAVE_PLATFORM_NON_ENCLAVE

	if (!session)
	{
		m_sessionCache.Put(cntPair.second, secComm->GetSessionCopy(), false);
	}

#endif //DECENT_DHT_NAIVE_RA_VER

	return CntPair(std::move(cntPair.first), std::move(secComm));
}
