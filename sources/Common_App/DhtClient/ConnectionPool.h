#pragma once

#include <DecentApi/Common/Net/ConnectionPool.h>

#include <random>

namespace Decent
{
	namespace AppConfig
	{
		class EnclaveList;
	}

	namespace DhtClient
	{
		class ConnectionPool : public Net::ConnectionPool<uint64_t>, public std::enable_shared_from_this<ConnectionPool>
		{
		public:
			ConnectionPool() = delete;

			ConnectionPool(size_t maxInCnt, size_t maxOutCnt, const AppConfig::EnclaveList& cfgEnclaveList);

			virtual ~ConnectionPool();

			virtual std::unique_ptr<Net::ConnectionBase> GetNew(const uint64_t& addr) override;

			std::pair<std::unique_ptr<Net::ConnectionBase>, uint64_t> GetAnyDhtNode();

			std::shared_ptr<ConnectionPool> GetSharedPtr();

			const std::vector<uint64_t>& GetKnownNodeAddr() const;

		private:
			std::random_device m_rd;
			std::mt19937 m_randGen;

			std::vector<uint64_t> m_knownNodeAddr;

			std::unique_ptr<std::uniform_int_distribution<size_t> > m_uniDist;
		};
	}
}
