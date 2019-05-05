#pragma once

#include <DecentApi/Common/Net/ConnectionPool.h>

namespace Decent
{
	namespace Tools
	{
		class ConfigManager;
	}

	namespace DhtClient
	{
		class ConnectionPool : public Net::ConnectionPool<uint64_t>, public std::enable_shared_from_this<ConnectionPool>
		{
		public:
			ConnectionPool() = delete;

			ConnectionPool(size_t maxInCnt, size_t maxOutCnt, const Tools::ConfigManager& cfgMgr);

			virtual ~ConnectionPool();

			virtual std::unique_ptr<Net::ConnectionBase> GetNew(const uint64_t& addr) override;

			std::pair<std::unique_ptr<Net::ConnectionBase>, uint64_t> GetAnyDhtNode();

			std::shared_ptr<ConnectionPool> GetSharedPtr();

		private:
			uint64_t m_firstNodeAddr;
		};
	}
}
