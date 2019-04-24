#pragma once

#include <memory>

namespace Decent
{
	namespace Net
	{
		class Connection;
	}

	namespace Tools
	{
		class ConfigManager;
	}

	namespace DhtClient
	{
		namespace ConnectionManager
		{
			void SetConfigManager(const Decent::Tools::ConfigManager& mgrRef);

			std::unique_ptr<Decent::Net::Connection> GetConnection2DecentDhtNode();
			std::unique_ptr<Decent::Net::Connection> GetConnection2DecentDhtStore(uint64_t addr);
		}
	}
}
