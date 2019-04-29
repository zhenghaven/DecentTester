#pragma once

#include <DecentApi/Common/Net/SecureConnectionPool.h>

namespace Decent
{
	namespace Ra
	{
		class TlsConfig;
	}

	namespace Dht
	{
		class DhtStates;
	}
	namespace DhtClient
	{

		class ConnectionPool : public Net::SecureConnectionPool<uint64_t>
		{
		public:
			ConnectionPool(size_t maxInCnt, size_t maxOutCnt) :
				SecureConnectionPool(maxInCnt, maxOutCnt)
			{}

			virtual ~ConnectionPool()
			{}

			virtual Net::CntPair GetNew(const uint64_t& addr, Ra::States& state) override;

			std::shared_ptr<Ra::TlsConfig> GetTlsConfig(Ra::States & state);
		};
	}
}
