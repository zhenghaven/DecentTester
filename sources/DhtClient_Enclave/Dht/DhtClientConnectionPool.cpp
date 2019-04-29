#include "DhtClientConnectionPool.h"

#include <DecentApi/Common/make_unique.h>
#include <DecentApi/Common/Ra/States.h>
#include <DecentApi/Common/Net/ConnectionBase.h>
#include <DecentApi/Common/Net/TlsCommLayer.h>

#include <DecentApi/Common/Ra/TlsConfigWithName.h>

#include "DhtClientConnection.h"
#include "AppNames.h"

using namespace Decent;
using namespace Decent::Net;
using namespace Decent::Ra;
using namespace Decent::DhtClient;

namespace
{
	std::shared_ptr<TlsConfigWithName> GetTlsCfg2Dht(Ra::States & state)
	{
		static std::shared_ptr<TlsConfigWithName> tlsCfg = std::make_shared<TlsConfigWithName>(state, TlsConfigWithName::Mode::ClientHasCert, AppNames::sk_decentDHT);
		return tlsCfg;
	}
}

CntPair ConnectionPool::GetNew(const uint64_t & addr, Ra::States & state)
{
	std::unique_ptr<ConnectionBase> connection = DhtClient::GetConnection2DhtStore(addr);
	std::unique_ptr<SecureCommLayer> tls = Tools::make_unique<TlsCommLayer>(*connection, GetTlsCfg2Dht(state), true);
	return CntPair(connection, tls);
}

std::shared_ptr<Ra::TlsConfig> ConnectionPool::GetTlsConfig(Ra::States & state)
{
	return GetTlsCfg2Dht(state);
}
